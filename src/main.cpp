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

//SPI clk (not exact - sets to first available lower value prolly?)
static constexpr uint32_t spi_clk_hz = 16000000UL;

// global interrupt flag for testing
volatile bool interrupt_flag = false;
ICM42688PAllData int_read_data;

ICM42688P icm(&SPI, cs, spi_clk_hz, int1, int2);




void DataReadyInterrupt(){
  //todo
  digitalWrite(usr_led, HIGH);
  int_read_data = icm.ReadAll();
  digitalWrite(usr_led, LOW);
  interrupt_flag = true;
}


void setup() {
  delay(5000);
  Serial.begin(115200);
  Serial.println("PLab vibration probe boot ok!");
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
  icm.IntAsyncReset();
  icm.EnableDataReadyInt1();
  icm.SetInt1PushPullActiveHighPulsed();
  
  icm.SetAccelSampleRate(ICM42688P::AccelOutputDataRate::RATE_200);
  icm.SetGyroSampleRate(ICM42688P::GyroOutputDataRate::RATE_200);
  //setup acel / gyro
  icm.SetAccelModeLn();
  icm.SetGyroModeLn();
  

  
  //
  //setup interrupt on INT1 pin
  attachInterrupt(int1, DataReadyInterrupt, RISING);



}

void loop() {
  // put your main code here, to run repeatedly:
  // while(1);
  // while(!icm.CheckDataReady());
  while(!interrupt_flag);
  // Serial.println("#####################");
  // Serial.print("X: ");
  // Serial.print(data.accel_x);
  // Serial.print(" Y: ");
  // Serial.print(data.accel_y);
  // Serial.print(" Z: ");
  // Serial.println(data.accel_z);
  // Serial.print("Gyro X: ");
  // Serial.print(data.gyro_x);
  // Serial.print(" Gyro Y: ");
  // Serial.print(data.gyro_y);
  // Serial.print(" Gyro Z: ");
  // Serial.println(data.gyro_z);
  // Serial.print("Temp: ");
  // Serial.println(data.temp);
  Serial.println("AX: " + String(int_read_data.accel_x) + " AY: " + String(int_read_data.accel_y) + " AZ: " + String(int_read_data.accel_z) + " GX: " + String(int_read_data.gyro_x) + " GY: " + String(int_read_data.gyro_y) + " GZ: " + String(int_read_data.gyro_z) + " T: " + String(int_read_data.temp));
  // vTaskDelay(5);
  // digitalWrite(usr_led, LOW);






  // digitalWrite(usr_led, HIGH);
  // Serial.println("Hello World ON!");
  // vTaskDelay(1000);
  // digitalWrite(usr_led, LOW);
  // Serial.println("Hello World OFF!");
  // vTaskDelay(1000);
}
