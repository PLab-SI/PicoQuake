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