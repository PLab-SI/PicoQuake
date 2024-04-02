#include <Arduino.h>
#include <SPI.h>
#include <ICM42688P.h>

// ICM42688P icm(&SPI, 16, 1000000);


void setup() {
  SPI.setRX(16);
  SPI.setTX(19);
  SPI.setSCK(18);
  // SPI.setCS(cs);
  SPI.begin();



}

void loop() {
  // put your main code here, to run repeatedly:
  delay(100);
}
