#include "ICM42688P.h"

ICM42688P::ICM42688P(SPIClass *spi, uint8_t cs, uint32_t spiclk){
    // SPI interface should be set up with correct pins outside of this class
    _spi = spi;
    _spiSettings = SPISettings(spiclk, MSBFIRST, SPI_MODE0);
    _cs = cs;
}

void ICM42688P::Begin(){
    pinMode(_cs, OUTPUT);
    digitalWrite(_cs, HIGH);
    //todo: test comms / accel who am i
    uint8_t whoami = ReadRegister(ICM42688_WHO_AM_I);
    if(whoami != WHOAMI_RETVAL){
        Serial.println("ICM42688 not found! Stopping here!");
        while(1){
            delay(100);
        }
    }
    else{
        Serial.println("ICM42688 got correct whoami.");
    }
    //todo: set up external clock / other settings?
}



uint8_t ICM42688P::ReadRegister(uint8_t reg) {
    reg |= 0x80;
    uint8_t out[2] = {reg, 0xFF};
    uint8_t in[2];
    
    digitalWrite(_cs, LOW);

    SPI.beginTransaction(_spiSettings);
    SPI.transfer(out, in, 2);

    SPI.endTransaction();

    digitalWrite(_cs, HIGH);
    return in[1];
}

void ICM42688P::ReadMulti(uint8_t reg_first, uint8_t *buf, uint8_t len) {
    reg_first |= 0x80;
    
    digitalWrite(_cs, LOW);

    SPI.beginTransaction(_spiSettings);
    SPI.transfer(reg_first);
    SPI.transfer(nullptr, buf, len);

    SPI.endTransaction();
    digitalWrite(_cs, HIGH);
}

void ICM42688P::WriteRegister(uint8_t reg, uint8_t data) {
    uint8_t out[2] = {reg, data};
    
    digitalWrite(_cs, LOW);

    SPI.beginTransaction(_spiSettings);
    SPI.transfer(out, 2);

    SPI.endTransaction();

    digitalWrite(_cs, HIGH);
}

bool ICM42688P::WriteRegisterSecure(uint8_t reg, uint8_t data) {
    WriteRegister(reg, data);
    // Verify write
    uint8_t readback = ReadRegister(reg);
    return readback == data;

}

void ICM42688P::SelectBank(uint8_t bank){
    if(bank > 3){
        Serial.println("Invalid bank selection!");
        return;
    }
    WriteRegister(ICM42688_REG_BANK_SEL, bank);
    _bank_selected = bank;
}

uint8_t ICM42688P::GetBank(){
    return _bank_selected;
}

ICM42688PAccelData ICM42688P::ReadAccel(){
    ICM42688PAccelData data;
    uint8_t buf[6];
    ReadMulti(ICM42688_ACCEL_DATA_X1, buf, 6);
    data.accel_x = (int16_t)(buf[0] << 8 | buf[1]) / _accel_full_scale;
    data.accel_y = (int16_t)(buf[2] << 8 | buf[3]) / _accel_full_scale;
    data.accel_z = (int16_t)(buf[4] << 8 | buf[5]) / _accel_full_scale;
    return data;
}

ICM42688PGyroData ICM42688P::ReadGyro(){
    ICM42688PGyroData data;
    uint8_t buf[6];
    ReadMulti(ICM42688_GYRO_DATA_X1, buf, 6);
    data.gyro_x = (int16_t)(buf[0] << 8 | buf[1]) / _gyro_full_scale;
    data.gyro_y = (int16_t)(buf[2] << 8 | buf[3]) / _gyro_full_scale;
    data.gyro_z = (int16_t)(buf[4] << 8 | buf[5]) / _gyro_full_scale;
    return data;
}

ICM42688PAllData ICM42688P::ReadAll(){
    ICM42688PAllData data;
    uint8_t buf[14];
    ReadMulti(ICM42688_TEMP_DATA1, buf, 14);
    data.accel_x = (int16_t)(buf[2] << 8 | buf[3]) / _accel_full_scale;
    data.accel_y = (int16_t)(buf[4] << 8 | buf[5]) / _accel_full_scale;
    data.accel_z = (int16_t)(buf[6] << 8 | buf[7]) / _accel_full_scale;
    data.gyro_x = (int16_t)(buf[8] << 8 | buf[9]) / _gyro_full_scale;
    data.gyro_y = (int16_t)(buf[10] << 8 | buf[11]) / _gyro_full_scale;
    data.gyro_z = (int16_t)(buf[12] << 8 | buf[13]) / _gyro_full_scale;
    data.temp = (int16_t)(buf[0] << 8 | buf[1]) / 132.48 + 25.0;
    //todo: check temperture conversion
    return data;
}

//todo: this resets all interrupt flags in the register. We might need a function that reads all of them if other interrupts are used.
bool ICM42688P::CheckDataReady(){
    uint8_t intStat =  ReadRegister(ICM42688_INT_STATUS);
    //bit 3 is data ready flag
    return (bool)(intStat & 0b00001000);
}

void ICM42688P::SetInt1PushPullActiveHighPulsed(){
    //read register
    uint8_t reg = ReadRegister(ICM42688_INT_CONFIG);
    //set bits 2:0 to 0b011 for pulsed mode, pushpull and active high
    reg = reg & 0b11111000;
    //bits 2:0 cleared
    reg = reg | 0b011;
    WriteRegister(ICM42688_INT_CONFIG, reg);
}

void ICM42688P::SoftReset(){
    WriteRegister(ICM42688_DEVICE_CONFIG, 0x01);
    delay(10); //according to datasheet, 1ms is enough
    //todo: if needed, check soft reset done flag in ICM42688_INT_CONFIG
}

void ICM42688P::EnableDataReadyInt1(){
    //enables data ready interrupt on INT1 pin. Pin needs to be config'd sepparately (pulsed, latching, etc.)
    //read register
    uint8_t reg = ReadRegister(ICM42688_INT_SOURCE0);
    //set bit 3 to 1 for data ready interrupt
    reg = reg | 0b00001000;
    WriteRegister(ICM42688_INT_CONFIG, reg);
}

