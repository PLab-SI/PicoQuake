# Firmware update

## Check firmware version

Check the current firmware version on you device by running:

```bash
picoquake info <short_id>
```

## Update firmware

To update the firmware on your device, follow these steps:

1. Download the latest firmware (.uf2) from the [releases page](https://github.com/PLab-SI/PicoQuake/releases)
1. Put the device in BOOTSEL mode by running:
    ```bash
    picoquake bootsel <short_id>
    ```
    The device will appear as a removable drive named `RPI-RP2` on your computer.
1. Flash the firmware:
    - Drag and drop the downloaded .uf2 firmware file to the `RPI-RP2` drive.
    - Device will automatically reboot after the firmware is flashed.
1. Check if firmware updated correctly  by running:
    ```bash
    picoquake info <short_id>
    ```
