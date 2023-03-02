# SimpleModbus2MQTT
This python script was mostly invented by ChatGPT after my instructions. It has been modified to get values from a GARO GNM3T power meter. The MQTT topic form has been setup so it gets autodiscovered in Home Assistant. There's A LOT of missing error handling, but I just wanna get this simple script out there.

I communicated with the modbus through a RS485 to USB dongle with a FTDI chip.

* It can be run just as it is or it can be made into a systemd service.
* Uses minimalmodbus and paho-mqtt, so you gotta pip that shit too.
* If run as non-root, user has to be added to dialout group.
