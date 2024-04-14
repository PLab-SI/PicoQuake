#include <Arduino.h>
#include <SPI.h>
#include <FreeRTOS.h>
#include <task.h>
#include <queue.h>
#include <hardware/flash.h>
#include <pb_encode.h>
#include <pb_decode.h>

#include "pico/stdlib.h"

#include "ICM42688P.h"
#include "msg/messages.pb.h"
#include "cobs.h"

// Config
static constexpr uint16_t kSampleQueueSize = 64;

//PINS
//ICM42688P connections
static constexpr uint8_t spi_miso = 16;
static constexpr uint8_t spi_mosi = 19;
static constexpr uint8_t spi_sck = 18;
static constexpr uint8_t cs = 17;
static constexpr uint8_t int1 = 28;
static constexpr uint8_t int2 = 27;
//usr led
static constexpr uint8_t usr_led = 4;

//SPI clk (not exact - sets to first available lower value prolly?)
static constexpr uint32_t spi_clk_hz = 25000000UL;


//packed IDs
static constexpr uint8_t imu_data_id = 0x01;
static constexpr uint8_t status_id = 0x02;
static constexpr uint8_t device_info_id = 0x03;
static constexpr uint8_t command_id = 0x04;


// freertos queue for data read from icm in interrupt
QueueHandle_t raw_data_q;
volatile uint32_t buff_full_sample_missed_count = 0;

ICM42688P icm(&SPI, cs, spi_clk_hz, int1, int2);
uint64_t sample_count = 0;

ICM42688PAllData imu_all_data;
ICM42688PAllData q_pop_data;

// packet framing
IMUData pb_imu_data = IMUData_init_zero;
pb_ostream_t nanopb_stream;
uint8_t nanopb_buffer[IMUData_size];
uint8_t out_buffer[IMUData_size + 4]; // start 0x00, end 0x00, cobs overhead, ID byte (right after start byte)

//incoming data stuff
uint8_t incoming_buffer[64];
uint8_t incoming_cobs_buffer[64];

void __time_critical_func(DataReadyInterrupt)(){
  //todo
  digitalWrite(usr_led, HIGH);
  imu_all_data = icm.ReadAll();
  if(xQueueSendFromISR(raw_data_q, &imu_all_data, NULL) != pdTRUE){
    // queue send error - queue full!
    buff_full_sample_missed_count++;
  }
  digitalWrite(usr_led, LOW);
}

// basic ICM setup (prepared for sampling)
void SetupICM(){
  //set spi drive strength on icm (6-18ns) to reduce overshoot of MISO
  icm.SetSpiDriveConfigBits(0b100);
  // switch to external clock
  icm.StartClockGen();
  icm.setClockSourceExtInt2();
  delay(100);
  
  // setup data ready interuupt
  icm.SetIntPulsesShort();
  icm.IntAsyncReset();
  icm.EnableDataReadyInt1();
  icm.SetInt1PushPullActiveHighPulsed();
}

// start sampling at specified settings. To change settings, stop sampling and use this function again
void StartSampling(ICM42688P::OutputDataRate rate, ICM42688P::AccelFullScale accel_range, ICM42688P::GyroFullScale gyro_range, FilterConfig filter_cfg){
  icm.SetAccelSampleRate(rate);
  icm.SetGyroSampleRate(rate);
  icm.setAccelFullScale(accel_range);
  icm.setGyroFullScale(gyro_range);
  icm.SetAccelFilterBandwidth(filter_cfg);
  icm.SetAccelModeLn();
  delay(10);
  icm.SetGyroModeLn();
  delay(10);
}

// stop sampling
void StopSampling(){
  icm.SetAccelModeOff();
  icm.SetGyroModeOff();
}

void HandleCommand(Command cmd){
  //todo
}

void SendIMUData() {
  if(uxQueueMessagesWaiting(raw_data_q) > 0){
    xQueueReceive(raw_data_q, &q_pop_data, 0);
  } else {
    return;
  }

  pb_imu_data.count = sample_count++;
  pb_imu_data.acc_x = q_pop_data.accel_x;
  pb_imu_data.acc_y = q_pop_data.accel_y;
  pb_imu_data.acc_z = q_pop_data.accel_z;
  pb_imu_data.gyro_x = q_pop_data.gyro_x;
  pb_imu_data.gyro_y = q_pop_data.gyro_y;
  pb_imu_data.gyro_z = q_pop_data.gyro_z;

  // nanopb
  nanopb_stream = pb_ostream_from_buffer(nanopb_buffer, sizeof(nanopb_buffer));
  pb_encode(&nanopb_stream, IMUData_fields, &pb_imu_data);
  size_t nanopb_size = nanopb_stream.bytes_written;

  //add ID to the front of the packet. ID is never 0, no need to run cobs on it

  // COBS
  cobs_encode_result cobs_result = cobs_encode(out_buffer + 2, 
      sizeof(out_buffer) - 3, nanopb_buffer, nanopb_size);
  
  size_t out_packet_len = cobs_result.out_len + 3;
      
  out_buffer[0] = 0x00; //start byte
  out_buffer[1] = imu_data_id; //id byte
  out_buffer[out_packet_len - 1] = 0x00; //end byte

  // Send
  Serial.write(out_buffer, out_packet_len);
}


#define BUF_SIZE 64

void ParseIncoming() {
  static size_t buf_index = 0;

  while (Serial.available()) {
    uint8_t byte = Serial.read();

    if (byte == 0x00 && buf_index == 0) { //start byte 0x00
      // start byte detected, increment buffer index
      buf_index++;
      return;
    }
    if(byte == 0x00 && buf_index == 1){
      // two 0x00 in a row. first was incorrectly interpreted as start byte but was actually end byte. This byte is now start, reset index to 1
      // tldr: if multiple 0x00 in a row, last one is taken as start byte
      buf_index = 1;
      return;
    }
    if(byte == 0x00 && buf_index > 1){ //end byte 0x00
      // end byte detected, process the buffer
      uint8_t packet_id = incoming_buffer[1];
      //decode COBS
      cobs_decode_result result = cobs_decode(incoming_cobs_buffer, sizeof(incoming_cobs_buffer), incoming_buffer+1, buf_index-2);
      if(result.status == COBS_DECODE_OK){
        // Use nanopb to decode the message
        pb_istream_t stream = pb_istream_from_buffer(incoming_cobs_buffer, result.out_len);
        //switch to decode different packet types (not needed for now, only command is received)
        switch(packet_id){
          case status_id:{ //namespace brackets to be able to initialize msg
            Command msg = Command_init_zero;
            if (pb_decode(&stream, Command_fields, &msg)) {
              // Handle the decoded message
              HandleCommand(msg);
            }
            else {
              // Handle nanopb the error
            }
            }break;
          default:
            return;
            break;
        }
      }
      else {
        // Handle COBS the error
      }


      buf_index = 0; //reset buffer index
      return;
    }
    else{ // normal bytes in between start and end
      if(buf_index < BUF_SIZE){
        //add to buffer and increment index
        incoming_buffer[buf_index++] = byte;
      } else {
        // buffer full ERROR
        while(1);
        return;
      }
    }

  }
}

void setup() {
  // set_sys_clock_khz(270000, true);

  raw_data_q = xQueueCreate(kSampleQueueSize, sizeof(ICM42688PAllData));

  //set INT1 as input for data ready interrupt
  pinMode(int1, INPUT);
  pinMode(usr_led, OUTPUT);
  


  delay(3000);
  Serial.begin(115200);
  digitalWrite(usr_led, HIGH);
  delay(100);
  digitalWrite(usr_led, LOW);
  delay(500);
  Serial.println("PLab vibration probe boot ok!");
  // uint8_t unique_id[10];
  // flash_get_unique_id(unique_id);
  // //print uid
  // Serial.print("UID: ");
  // for(int i = 0; i < 9; i++){
  //   Serial.print(unique_id[i], HEX);
  // }
  // Serial.println();
  // delay(3000);

  SPI.setRX(spi_miso);
  SPI.setTX(spi_mosi);
  SPI.setSCK(spi_sck);
  // // SPI.setCS(cs);
  SPI.begin();

  //begin ICM42688P
  if(!icm.Begin()){
    Serial.println("ICM42688P not found Stopping here!");
    Serial.println("Rebooting in 5 seconds...");
    vTaskDelay(5000);
    rp2040.reboot();
  }

  SetupICM();
  
  StartSampling(ICM42688P::OutputDataRate::RATE_4K, ICM42688P::AccelFullScale::RANGE_16G, ICM42688P::GyroFullScale::RANGE_2000DPS, filter_config::f_126hz);

  //setup interrupt on INT1 pin
  attachInterrupt(int1, DataReadyInterrupt, RISING);

}

void loop() {
  // todo: listen for cmd packets
  // todo: send status packet
  // Serial.println("loop");
  delay(1000);
}

void setup1() {
  delay(6000);
}


void loop1() {
  SendIMUData();
}
