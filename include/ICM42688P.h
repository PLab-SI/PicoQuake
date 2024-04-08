#ifndef ICM42688P_H
#define ICM42688P_H

#include <Arduino.h>
#include <SPI.h>
#include "ICM42688P_filter_config.h"

/* ICM42688 registers
https://invensense.tdk.com/wp-content/uploads/2020/04/ds-000347_icm-42688-p-datasheet.pdf
*/
// User Bank 0
#define ICM42688_DEVICE_CONFIG             0x11
#define ICM42688_DRIVE_CONFIG              0x13
#define ICM42688_INT_CONFIG                0x14
#define ICM42688_FIFO_CONFIG               0x16
#define ICM42688_TEMP_DATA1                0x1D
#define ICM42688_TEMP_DATA0                0x1E
#define ICM42688_ACCEL_DATA_X1             0x1F
#define ICM42688_ACCEL_DATA_X0             0x20
#define ICM42688_ACCEL_DATA_Y1             0x21
#define ICM42688_ACCEL_DATA_Y0             0x22
#define ICM42688_ACCEL_DATA_Z1             0x23
#define ICM42688_ACCEL_DATA_Z0             0x24
#define ICM42688_GYRO_DATA_X1              0x25
#define ICM42688_GYRO_DATA_X0              0x26
#define ICM42688_GYRO_DATA_Y1              0x27
#define ICM42688_GYRO_DATA_Y0              0x28
#define ICM42688_GYRO_DATA_Z1              0x29
#define ICM42688_GYRO_DATA_Z0              0x2A
#define ICM42688_TMST_FSYNCH               0x2B
#define ICM42688_TMST_FSYNCL               0x2C
#define ICM42688_INT_STATUS                0x2D
#define ICM42688_FIFO_COUNTH               0x2E
#define ICM42688_FIFO_COUNTL               0x2F
#define ICM42688_FIFO_DATA                 0x30
#define ICM42688_APEX_DATA0                0x31
#define ICM42688_APEX_DATA1                0x32
#define ICM42688_APEX_DATA2                0x33
#define ICM42688_APEX_DATA3                0x34
#define ICM42688_APEX_DATA4                0x35
#define ICM42688_APEX_DATA5                0x36
#define ICM42688_INT_STATUS2               0x37   
#define ICM42688_INT_STATUS3               0x38   
#define ICM42688_SIGNAL_PATH_RESET         0x4B
#define ICM42688_INTF_CONFIG0              0x4C
#define ICM42688_INTF_CONFIG1              0x4D
#define ICM42688_PWR_MGMT0                 0x4E
#define ICM42688_GYRO_CONFIG0              0x4F
#define ICM42688_ACCEL_CONFIG0             0x50
#define ICM42688_GYRO_CONFIG1              0x51
#define ICM42688_GYRO_ACCEL_CONFIG0        0x52
#define ICM42688_ACCEL_CONFIG1             0x53
#define ICM42688_TMST_CONFIG               0x54
#define ICM42688_APEX_CONFIG0              0x56
#define ICM42688_SMD_CONFIG                0x57
#define ICM42688_FIFO_CONFIG1              0x5F
#define ICM42688_FIFO_CONFIG2              0x60
#define ICM42688_FIFO_CONFIG3              0x61
#define ICM42688_FSYNC_CONFIG              0x62
#define ICM42688_INT_CONFIG0               0x63
#define ICM42688_INT_CONFIG1               0x64
#define ICM42688_INT_SOURCE0               0x65
#define ICM42688_INT_SOURCE1               0x66
#define ICM42688_INT_SOURCE3               0x68
#define ICM42688_INT_SOURCE4               0x69
#define ICM42688_FIFO_LOST_PKT0            0x6C
#define ICM42688_FIFO_LOST_PKT1            0x6D
#define ICM42688_SELF_TEST_CONFIG          0x70
#define ICM42688_WHO_AM_I                  0x75 // should return 0x47
#define ICM42688_REG_BANK_SEL              0x76

// User Bank 1
#define ICM42688_SENSOR_CONFIG0            0x03
#define ICM42688_GYRO_CONFIG_STATIC2       0x0B
#define ICM42688_GYRO_CONFIG_STATIC3       0x0C
#define ICM42688_GYRO_CONFIG_STATIC4       0x0D
#define ICM42688_GYRO_CONFIG_STATIC5       0x0E
#define ICM42688_GYRO_CONFIG_STATIC6       0x0F
#define ICM42688_GYRO_CONFIG_STATIC7       0x10
#define ICM42688_GYRO_CONFIG_STATIC8       0x11
#define ICM42688_GYRO_CONFIG_STATIC9       0x12
#define ICM42688_GYRO_CONFIG_STATIC10      0x13
#define ICM42688_XG_ST_DATA                0x5F
#define ICM42688_YG_ST_DATA                0x60
#define ICM42688_ZG_ST_DATA                0x61
#define ICM42688_TMSTAL0                   0x63
#define ICM42688_TMSTAL1                   0x64
#define ICM42688_TMSTAL2                   0x62
#define ICM42688_INTF_CONFIG4              0x7A
#define ICM42688_INTF_CONFIG5              0x7B
#define ICM42688_INTF_CONFIG6              0x7C

// User Bank 2
#define ICM42688_ACCEL_CONFIG_STATIC2      0x03
#define ICM42688_ACCEL_CONFIG_STATIC3      0x04
#define ICM42688_ACCEL_CONFIG_STATIC4      0x05
#define ICM42688_XA_ST_DATA                0x3B
#define ICM42688_YA_ST_DATA                0x3C
#define ICM42688_ZA_ST_DATA                0x3D

// User Bank 4
#define ICM42688_APEX_CONFIG1              0x40
#define ICM42688_APEX_CONFIG2              0x41
#define ICM42688_APEX_CONFIG3              0x42
#define ICM42688_APEX_CONFIG4              0x43
#define ICM42688_APEX_CONFIG5              0x44
#define ICM42688_APEX_CONFIG6              0x45
#define ICM42688_APEX_CONFIG7              0x46
#define ICM42688_APEX_CONFIG8              0x47
#define ICM42688_APEX_CONFIG9              0x48
#define ICM42688_ACCEL_WOM_X_THR           0x4A
#define ICM42688_ACCEL_WOM_Y_THR           0x4B
#define ICM42688_ACCEL_WOM_Z_THR           0x4C
#define ICM42688_INT_SOURCE6               0x4D
#define ICM42688_INT_SOURCE7               0x4E
#define ICM42688_INT_SOURCE8               0x4F
#define ICM42688_INT_SOURCE9               0x50
#define ICM42688_INT_SOURCE10              0x51
#define ICM42688_OFFSET_USER0              0x77
#define ICM42688_OFFSET_USER1              0x78
#define ICM42688_OFFSET_USER2              0x79
#define ICM42688_OFFSET_USER3              0x7A
#define ICM42688_OFFSET_USER4              0x7B
#define ICM42688_OFFSET_USER5              0x7C
#define ICM42688_OFFSET_USER6              0x7D
#define ICM42688_OFFSET_USER7              0x7E
#define ICM42688_OFFSET_USER8              0x7F

#define WHOAMI_RETVAL                      0x47 

//at 32kHz external clock, ODRs (output data rate) are as per datasheet. External clock can be 31kHz to 50Khz. ODR scales with clock frequency!
#define ICM42688_EXTERNAL_CLK_FREQ                  32000UL

typedef struct {
    float accel_x;
    float accel_y;
    float accel_z;
} ICM42688PAccelData;

typedef struct {
    float gyro_x;
    float gyro_y;
    float gyro_z;
} ICM42688PGyroData;

typedef struct {
    float accel_x;
    float accel_y;
    float accel_z;
    float gyro_x;
    float gyro_y;
    float gyro_z;
    float temp;
} ICM42688PAllData;




class ICM42688P{
    public:
        enum class GyroOutputDataRate {
            RATE_32K = 0b0001,
            RATE_16K = 0b0010,
            RATE_8K = 0b0011,
            RATE_4K = 0b0100,
            RATE_2K = 0b0101,
            RATE_1K = 0b0110,
            RATE_500 = 0b1111,
            RATE_200 = 0b0111,
            RATE_100 = 0b1000,
            RATE_50 = 0b1001,
            RATE_25 = 0b1010,
            RATE_12_5 = 0b1011
        };

        // Only rates that are supported in LN (normal) mode.
        enum class AccelOutputDataRate {
            RATE_32K = 0b0001,
            RATE_16K = 0b0010,
            RATE_8K = 0b0011,
            RATE_4K = 0b0100,
            RATE_2K = 0b0101,
            RATE_1K = 0b0110,
            RATE_500 = 0b1111,
            RATE_200 = 0b0111,
            RATE_100 = 0b1000,
            RATE_50 = 0b1001,
            RATE_25 = 0b1010,
            RATE_12_5 = 0b1011,
        };

        enum class AccelFullScale {
            RANGE_2G = 0b011,
            RANGE_4G = 0b010,
            RANGE_8G = 0b001,
            RANGE_16G = 0b000
        };

        enum class GyroFullScale {
            RANGE_15_625DPS = 0b111,
            RANGE_31_25DPS = 0b110,
            RANGE_62_5DPS = 0b101,
            RANGE_125DPS = 0b100,
            RANGE_250DPS = 0b011,
            RANGE_500DPS = 0b010,
            RANGE_1000DPS = 0b001,
            RANGE_2000DPS = 0b000
        };


        ICM42688P(SPIClass *spi, uint8_t cs, uint32_t spiclk, uint8_t int1_pin, uint8_t int2_pin);
        uint8_t ReadRegister(uint8_t reg);
        void ReadMulti(uint8_t reg_first, uint8_t *buf, uint8_t len);
        void WriteRegister(uint8_t reg, uint8_t data);
        bool WriteRegisterSecure(uint8_t reg, uint8_t data);
        void SelectBank(uint8_t bank);
        uint8_t GetBank();


        bool Begin();

        void SoftReset();
        void SetInt1PushPullActiveHighPulsed();
        void EnableDataReadyInt1();
        void IntAsyncReset();
        void DataReadyIntSetClearOnAnyRead();
        void setClockSourceExtInt2();

        void SetAccelModeLn();
        void SetGyroModeLn();
        void SetAccelModeOff();
        void SetGyroModeOff();
        void setAccelFullScale(AccelFullScale scale);
        void setGyroFullScale(GyroFullScale scale);
        void SetAccelSampleRate(AccelOutputDataRate rate);
        void SetGyroSampleRate(GyroOutputDataRate rate);
        void SetAccelFilterBandwidth(const FilterConfig& bw);
        void SetGyroFilterBandwidth(const FilterConfig& bw);

        ICM42688PAccelData ReadAccel();
        ICM42688PGyroData ReadGyro();
        ICM42688PAllData ReadAll();
        bool CheckDataReady();

        void StartClockGen();
        void StopClockGen();
   
        

    private:
        SPIClass *_spi;
        SPISettings _spiSettings;
        uint8_t _cs;
        uint8_t _int1_pin;
        uint8_t _int2_pin;
        uint8_t _bank_selected = 0;
        float _gyro_full_scale = 32768.0/2000.0; //default is +-2000dps
        float _accel_full_scale = 2048.0; //default is +-16g
        //todo: check default and set when range is changed
};


#endif // ICM42688P_H