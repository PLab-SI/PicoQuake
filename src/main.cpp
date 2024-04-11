#include <Arduino.h>
#include <SPI.h>
#include <FreeRTOS.h>
#include <task.h>
#include <queue.h>
#include <hardware/flash.h>
#include <pb_encode.h>

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
static constexpr uint32_t spi_clk_hz = 16000000UL;


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
uint8_t out_buffer[IMUData_size + 3];

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

  // COBS
  cobs_encode_result cobs_result = cobs_encode(out_buffer + 1, 
      sizeof(out_buffer) - 2, nanopb_buffer, nanopb_size);
  
  size_t out_packet_len = cobs_result.out_len + 2;
      
  out_buffer[0] = 0x00;
  out_buffer[cobs_result.out_len + 1] = 0x00;

  // Send
  Serial.write(out_buffer, out_packet_len);
}

void setup() {
  raw_data_q = xQueueCreate(kSampleQueueSize, sizeof(ICM42688PAllData));


  delay(3000);
  Serial.begin(115200);
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

  //set INT1 as input for data ready interrupt
  pinMode(int1, INPUT);
  pinMode(usr_led, OUTPUT);

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
  
  // setup accel / gyro
  icm.SetAccelSampleRate(ICM42688P::AccelOutputDataRate::RATE_1K);
  icm.SetGyroSampleRate(ICM42688P::GyroOutputDataRate::RATE_1K);
  icm.SetAccelModeLn();
  icm.SetGyroModeLn();

  //setup interrupt on INT1 pin
  attachInterrupt(int1, DataReadyInterrupt, RISING);

}

void loop() {
  // todo: listen for cmd packets
  // todo: send status packet
  delay(1000);
}

void setup1() {
  delay(6000);
}


void loop1() {
  SendIMUData();
}
