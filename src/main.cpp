#include <Arduino.h>
#include <SPI.h>
#include <ICM42688P.h>
#include <FreeRTOS.h>
#include <task.h>
#include "queue.h"
#include <hardware/flash.h>

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
QueueHandle_t raw_data;

ICM42688P icm(&SPI, cs, spi_clk_hz, int1, int2);




void DataReadyInterrupt(){
  //todo
  digitalWrite(usr_led, HIGH);
  ICM42688PAllData data = icm.ReadAll();
  xQueueSendFromISR(raw_data, &data, NULL);
  digitalWrite(usr_led, LOW);
}


void setup() {
  raw_data = xQueueCreate(64, sizeof(ICM42688PAllData));


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

  //set spi drive strength on icm (6-18ns) to reducec overshoot ob MISO
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
  
  icm.SetAccelSampleRate(ICM42688P::AccelOutputDataRate::RATE_500);
  icm.SetGyroSampleRate(ICM42688P::GyroOutputDataRate::RATE_500);
  //setup acel / gyro
  icm.SetAccelModeLn();
  icm.SetGyroModeLn();
  

  
  //
  //setup interrupt on INT1 pin
  attachInterrupt(int1, DataReadyInterrupt, RISING);



}

void loop() {
  // check if anything is in queue and print it
  // check if the queue is full
  if(uxQueueSpacesAvailable(raw_data) == 0){
    Serial.println("ERROR: QUEUE FULL!");
  }
  if(uxQueueMessagesWaiting(raw_data) > 0){
    ICM42688PAllData pop_data;
    xQueueReceive(raw_data, &pop_data, 0);
    Serial.println("AX: " + String(pop_data.accel_x, 2) + " AY: " + String(pop_data.accel_y, 2) + " AZ: " + String(pop_data.accel_z, 2) + " GX: " + String(pop_data.gyro_x, 2) + " GY: " + String(pop_data.gyro_y, 2) + " GZ: " + String(pop_data.gyro_z, 2) + " T: " + String(pop_data.temp, 2));
  }


  
  // vTaskDelay(5);
  // digitalWrite(usr_led, LOW);






  // digitalWrite(usr_led, HIGH);
  // Serial.println("Hello World ON!");
  // vTaskDelay(1000);
  // digitalWrite(usr_led, LOW);
  // Serial.println("Hello World OFF!");
  // vTaskDelay(1000);
}
