#! /usr/bin/env python3

# This is taken from Adafruit examples...
# it requies adafruit stuff, so may not be that useful.
# it comes from a github repository
# https://github.com/adafruit/Adafruit_Python_MCP3008.git

# Simple example of reading the MCP3008 analog input channels and printing
# them all out.
# Author: Tony DiCola
# License: Public Domain
import time
import sys
import pdb
# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008


# Software SPI configuration:
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Hardware SPI configuration:
# SPI_PORT   = 0
# SPI_DEVICE = 0
# mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))


print('Reading MCP3008 values, press Ctrl-C to quit...')
# Print nice channel column headers.
print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*range(8)))
print('-' * 57)
# Main program loop.
pdb
while True:
    # Read all the ADC channel values in a list.
    values = [0]*8
    for i in range(8):
        # The read_adc function will get the value of the specified channel (0-7).
        values[i] = mcp.read_adc(i)
        if values[i] != 0:
        # added by cgb copying code from cgbanother and formula from https://learn.adafruit.com/tmp36-temperature-sensor/using-a-temp-sensor
        # to get actual temperature
           values[i] = ((values[i] * (3300/1024)))
           values[i] = ((values[i] - 500)/10)
           values[i] = round(values[i],2)

    # Print the ADC values.
    print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
    # Pause for half a second.
    # changed by cgb to run all night
    time.sleep(0.5)
    # time.sleep(600)
