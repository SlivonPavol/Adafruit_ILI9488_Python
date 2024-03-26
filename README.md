# ILI9488 Python Library (Modified from Adafruit_Python_ILI9341)

This repository contains a modified version of the Python library to control an ILI9341 TFT LCD display. It has been adapted specifically for use with ILI9488 displays.

## Description

The ILI9488 Python Library is a modified version of the original library designed to control ILI9341 TFT LCD displays. While the original library was tailored for Adafruit 2.8" LCDs, this modified version provides compatibility and optimizations for ILI9488 displays. It allows simple drawing on the display without the need to install a kernel module, making it suitable for various platforms including Raspberry Pi and BeagleBone Black.

## Dependencies
For all platforms (Raspberry Pi and BeagleBone Black), ensure you have the following dependencies installed:

```bash
sudo apt-get update
sudo apt-get install build-essential python-dev python-smbus python-pip python-imaging
```
For Raspberry Pi, install the RPi.GPIO library:
```bash
sudo pip install RPi.GPIO
```
For BeagleBone Black, install the Adafruit_BBIO library:
```bash
sudo pip install Adafruit_BBIO
```
### Usage
To use the library, download the repository, unzip it, navigate to the directory containing the library, and execute the desired Python script:
```bash
python3 shapes.py
```
### Credits
This library is based on the original ILI9341 Python library by Tony DiCola for Adafruit Industries, available at: Adafruit_Python_ILI9341. It has been modified for ILI9488 displays.

