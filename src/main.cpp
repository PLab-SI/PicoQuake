#include <Arduino.h>
#include <SPI.h>
#include <ICM42688P.h>
#include <FreeRTOS.h>
#include <task.h>

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

//SPI clk
static constexpr uint32_t spi_clk_hz = 1000000;

ICM42688P icm(&SPI, cs, spi_clk_hz, int1, int2);




void DataReadyInterrupt(){
  //todo
}


void setup() {
  //set INT1 as input for data ready interrupt
  pinMode(int1, INPUT);

  SPI.setRX(spi_miso);
  SPI.setTX(spi_mosi);
  SPI.setSCK(spi_sck);
  // SPI.setCS(cs);
  SPI.begin();

  //begin ICM42688P
  if(!icm.Begin()){
    Serial.println("ICM42688P not found Stopping here!");
    Serial.println("Rebooting in 5 seconds...");
    vTaskDelay(5000);
    rp2040.reboot();
  }

  //
  //setup interrupt on INT1 pin
  // attachInterrupt(int1, DataReadyInterrupt, RISING);



}

void loop() {
  // put your main code here, to run repeatedly:
  vTaskDelay(100);
}
