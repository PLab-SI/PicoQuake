#include "ICM42688P.h"

ICM42688P::ICM42688P(SPIClass *spi, uint8_t cs, uint32_t spiclk, uint8_t int1_pin, uint8_t int2_pin){
    // SPI interface should be set up with correct pins outside of this class
    _spi = spi;
    _spiSettings = SPISettings(spiclk, MSBFIRST, SPI_MODE0);
    _cs = cs;
    _int1_pin = int1_pin;
    _int2_pin = int2_pin;
}

void ICM42688P::Begin(){
    pinMode(_cs, OUTPUT);
    digitalWrite(_cs, HIGH);
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

// always return bank to 0!
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

//TODO: clock generation with analogWrite seems to be a bit jittery in some cases. verify if this is a problem / write custom implementation if needed
void ICM42688P::StartClockGen(){
    //set pin mode
    pinMode(_int2_pin, OUTPUT);
    //set resolution
    analogWriteResolution(10);
    //set frequency
    analogWriteFreq(ICM42688_EXTERNAL_CLK_FREQ);
    //start generating clock at 50% duty cycle
    analogWrite(_int2_pin, 512);
}

void ICM42688P::StopClockGen(){
    //stop generating clock
    analogWrite(_int2_pin, 0);
    digitalWrite(_int2_pin, LOW);
    //set pin to input
    pinMode(_int2_pin, INPUT);
}

// clock generation on int2 needs to be enabled before this! Use StartClockGen()
void ICM42688P::setClockSourceExtInt2(){
    //select bank 1
    SelectBank(1);
    //write INTF_CONFIG5 register (bank 1) to set int2 pin mode as clkin (to 0x04)
    WriteRegister(ICM42688_INTF_CONFIG5, 0x04);
    //select bank 0
    SelectBank(0);
    // write register INTF_CONFIG1 clksel bits (register to 0x95 - sets RTC MODE bit)
    WriteRegister(ICM42688_INTF_CONFIG1, 0x95);
}

void ICM42688P::SetAccelModeLn(){
    //read register
    uint8_t reg = ReadRegister(ICM42688_PWR_MGMT0);
    //set bits 1:0 to enable low noise mode (low noise mode is default full performance mode)
    reg |= 0b00000011;
    WriteRegister(ICM42688_PWR_MGMT0, reg);
    delay(1);  // wait to turn on (see datasheet)
}

void ICM42688P::SetAccelModeOff(){
    //read register
    uint8_t reg = ReadRegister(ICM42688_PWR_MGMT0);
    //reset bits 1:0 to power off accel
    reg &= ~0b00000011;
    WriteRegister(ICM42688_PWR_MGMT0, reg);
}

void ICM42688P::SetGyroModeLn(){
    //read register
    uint8_t reg = ReadRegister(ICM42688_PWR_MGMT0);
    //set bits 3:2 to enable low noise mode (low noise mode is default full performance mode)
    reg |= 0b00001100;
    WriteRegister(ICM42688_PWR_MGMT0, reg);
    delay(1); // wait to turn on (see datasheet)
}

void ICM42688P::SetGyroModeOff(){
    //read register
    uint8_t reg = ReadRegister(ICM42688_PWR_MGMT0);
    //reset bits 3:2 to power off gyro
    reg &= ~0b00001100;
    WriteRegister(ICM42688_PWR_MGMT0, reg);
}

void ICM42688P::SetAccelSampleRate(AccelOutputDataRate rate){
    //rate has a value that we need to set the register to. 4 LSB bits are valid, others 0
    uint8_t rate_bits = (uint8_t)rate;
    //read register
    uint8_t reg = ReadRegister(ICM42688_ACCEL_CONFIG0);
    //set bits 3:0 according to sample rate
    //clear bits 3:0, then set them according to rate
    reg = (reg & 0b11111000) | rate_bits;
    // write register
    WriteRegister(ICM42688_ACCEL_CONFIG0, reg);
}

void ICM42688P::SetGyroSampleRate(GyroOutputDataRate rate){
    //rate has a value that we need to set the register to. 4 LSB bits are valid, others 0
    uint8_t rate_bits = (uint8_t)rate;
    //read register
    uint8_t reg = ReadRegister(ICM42688_GYRO_CONFIG0);
    //set bits 3:0 according to sample rate
    //clear bits 3:0, then set them according to rate
    reg = (reg & 0b11111000) | rate_bits;
    // write register
    WriteRegister(ICM42688_GYRO_CONFIG0, reg);
}

void ICM42688P:: setGyroFullScale(GyroFullScale scale){
    //scale has a value that we need to set the register to. 3 LSB bits are valid, others 0
    uint8_t scale_bits = (uint8_t)scale;
    // shift bits to correct position (7:5)
    scale_bits = scale_bits << 5;
    //read register
    uint8_t reg = ReadRegister(ICM42688_GYRO_CONFIG0);
    //set bits 7:5 according to scale
    //clear bits 7:5, then set them according to scale
    reg = (reg & 0b00011111) | scale_bits;
    // write register
    WriteRegister(ICM42688_GYRO_CONFIG0, reg);
}

void ICM42688P:: setAccelFullScale(AccelFullScale scale){
    //scale has a value that we need to set the register to. 3 LSB bits are valid, others 0
    uint8_t scale_bits = (uint8_t)scale;
    // shift bits to correct position (7:5)
    scale_bits = scale_bits << 5;
    //read register
    uint8_t reg = ReadRegister(ICM42688_ACCEL_CONFIG0);
    //set bits 7:5 according to scale
    //clear bits 7:5, then set them according to scale
    reg = (reg & 0b00011111) | scale_bits;
    // write register
    WriteRegister(ICM42688_ACCEL_CONFIG0, reg);
}

void ICM42688P::SetAccelFilterBandwidth(const FilterConfig& bw){
    //registers are in bank2
    SelectBank(2);

    // *** DELT BITS ***
    //get delt bits (6 bit number). 6 LSB are valid. Covert uint16 to uint8 to match register
    uint8_t delt_bits = (uint8_t)bw.aaf_delt;
    //delt bits are 6:1 in register ACCEL_CONFIG_STATIC2 of bank 2. bitshift bits to correct place
    delt_bits = delt_bits << 1;
    //read register
    uint8_t reg = ReadRegister(ICM42688_ACCEL_CONFIG_STATIC2);
    //clear bits 6:1, then set them according to delt_bits
    reg = (reg & 0b10000001) | delt_bits;
    // write register
    WriteRegister(ICM42688_ACCEL_CONFIG_STATIC2, reg);

    // *** BITSHIFT BITS ***
    //get bitshift bits (4 bit number). 4 LSB are valid. Covert uint16 to uint8 to match register
    uint8_t bitshift_bits = (uint8_t)bw.aaf_bitshift;
    //bitshift bits are 7:4 in register ACCEL_CONFIG_STATIC4 of bank 2. bitshift bits to correct place
    bitshift_bits = bitshift_bits << 4;
    //read register
    reg = ReadRegister(ICM42688_ACCEL_CONFIG_STATIC4);
    //clear bits 7:4, then set them according to bitshift_bits
    reg = (reg & 0b00001111) | bitshift_bits;
    // write register
    WriteRegister(ICM42688_ACCEL_CONFIG_STATIC4, reg);

    // *** DELTSQR BITS ***
    //deltsqr bits (12 bit number) are in two regs:
    //ACCEL_CONFIG_STATIC3(7:0) are deltsqr(7:0)
    //ACCEL_CONFIG_STATIC4(3:0) are deltsqr(11:8)
    uint16_t deltsqr_bits = bw.aaf_deltsqr;
    // take bits 7:0
    uint8_t deltsqr_7_0 = (uint8_t)(deltsqr_bits & 0xFF);
    uint8_t deltsqr_11_8 = (uint8_t)((deltsqr_bits >> 8) & 0x0F);
    // no bitshift needed, 7:0 is whole register, 11:8 are already on LSB side (3:0 in register)
    //write static3 register. no read needed (only deltsqr 7:0 in register)
    WriteRegister(ICM42688_ACCEL_CONFIG_STATIC3, deltsqr_7_0);
    //read register static4
    reg = ReadRegister(ICM42688_ACCEL_CONFIG_STATIC4);
    //clear bits 3:0, then set them according to deltsqr_11_8
    reg = (reg & 0b11110000) | deltsqr_11_8;
    // write register
    WriteRegister(ICM42688_ACCEL_CONFIG_STATIC4, reg);


    //return to bank 1
    SelectBank(1);

}

