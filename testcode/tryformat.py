#!/usr/bin/python

# This is the code from https://www.canalworld.net/forums/index.php?/topic/69439-monitoring-my-electrics-with-a-raspberry-pi/&page=2
# it has lost all indentation, so a bit useless......... But might give some examples.

import numpy as np

#import matplotlib as mpl

import matplotlib.font_manager as font_manager

import matplotlib.pyplot as plt

import matplotlib.dates as mdates

from pylab import *

import spidev

import time

from time import gmtime

import RPi.GPIO as GPIO

import os

import ftplib

 

 

 

Save = 1 # 1 = Save data to file

print_data = 1 # Print data to stdout

TimeSleep = 5 # Sleep time

ftp_out = 1 # 1 = upload, 2 = verbose

 

# Set timers

period_get_data = 60 * 10

period_graph1 = 60 * 30

period_graph2 = 60 * 60 * 12

period_fridge = 60 * 15

period_aux = 60 * 6

 

# Initialise timers

time_get_data = int(time.time())

time_graph1 = int(time.time())

time_graph2 = int(time.time())

time_fridge = int(time.time())

time_aux = int(time.time())

 

 

# Font

path = '/home/pi/PythonProgs/YanoneKaffeesatz-Bold.ttf'

prop = font_manager.FontProperties(fname=path, size=13)

 

# Use Broadcom pin numbers (as printed on Humble Pi)

GPIO.setmode(GPIO.BCM)

 

# set up GPIO input/output channels

GPIO.setup(17, GPIO.OUT) # LED on pin17

for i in range(22, 26):

   GPIO.setup(i, GPIO.OUT) # Relays on pins 22-25

 

# Define relay on/off functions

def relay_on(pin):

   GPIO.output(pin,GPIO.HIGH)

# print 'Pin ', pin,' on'

 

def relay_off(pin):

   GPIO.output(pin,GPIO.LOW)

# print 'Pin ', pin,' off'

 

 

# Set up Serial Periperal Interface

spi = spidev.SpiDev()

spi.open(0,0)

 

def read_spi(channel):

   spidata = spi.xfer2([1,(8+channel)<<4,0])

# print("Raw ADC: {}".format(spidata)),

   data = ((spidata[1] & 3) << 8) + spidata[2]

# print("Data: {}".format(data))

   return data

 

# Set up data file

try:

   f = open("data.csv", "r"); f.close() # Check if file exists

except IOError as e: # If not, write headers

   f = open("data.csv", "w"); f.write('tt,year,month,date,day,hour,ttt,balanceI,solarI,boatI,data3,auxV,panelV,startV,battV,temp0,temp1,temp2,temp3,temp4,AhSolar,AhConsumed,AhAux \n'); f.close()

 

# Set up log file

try:

   f = open("log.txt", "r"); f.close() # Check if file exists

except IOError as e: # If not, write something

   f = open("log.txt", "w"); f.write('This is not an EMPTY FILE'); f.close()

 

# Set up stats file

try:

   f = open("stats.txt", "r"); f.close() # Check if file exists

except IOError as e: # If not, write something

   f = open("stats.txt", "w"); f.write('0,0'); f.close()

 

#make global variables

data0 = data1 = data2 = data3 = data4 = data5 = data6 = data7 = 1

temp0 = temp1 = temp2 = temp3 = temp4 = 1

thour = tdate = tmonth = tyear = tday = ttt = 1

log1 = log2 = log3 = log4 = log5 = "."

AhSolar = AhConsumed = AhAux = 0

tday_old = str(time.strftime('%a')) # tday

 

# Read stats file

##f = open("stats.txt", "r")

##f.read (AhSolar, AhConsumed)

##f.close()

 

 

##AhSolar, AhConsumed = np.genfromtxt('stats.txt', delimiter = ',', unpack = True, usecols=(0,1))

##print 'Test: '+AhSolar+AhConsumed

 

################### Temperature ################

 

os.system('modprobe w1-gpio')

os.system('modprobe w1-therm')

temp_sensor = '/sys/bus/w1/devices/28-0000056ed968/w1_slave'

 

def temp_raw():

   f = open(temp_sensor, 'r')

   lines = f.readlines()

   f.close()

   return lines

 

def read_temp():

   lines = temp_raw()

   while lines[0].strip()[-3:] != 'YES':

      time.sleep(0.2)

   lines = temp_raw()

 

   temp_output = lines[1].find('t=')

   if temp_output != -1:

      temp_string = lines[1].strip()[temp_output+2:]

      temp_c = float(temp_string) / 1000.0

      temp_f = temp_c * 9.0 / 5.0 + 32.0

   return temp_c #, temp_f

 

########################### Update log file #########################

def log(log0):

   global log1, log2, log3, log4, log5

   log4 = log3

   log3 = log2

   log2 = log1

   log1 = log0

   if Save == 1:

      f = open("log.txt", "w")

      f.write(log4+"<br>"+log3+"<br>"+log2+"<br>"+log1)

      f.close()

 

 

 

########################### ADC and One-Wire Inputs ##############

def get_data():

   global data0, data1, data2, data3, data4, data5, data6, data7, AhSolar, AhConsumed

# Read the ADC channels (0-7) : ([0 to 1033] * Correction for divider resistors

   data0 = (read_spi(0) - 525.0) * -0.074 # Balance I

   data1 = (read_spi(1) - 495.0) * -0.0685 # Solar I

   data2 = (read_spi(2) - 510.0) * 0.074 # Boat I

   data3 = read_spi(3)

   data4 = read_spi(4) * 0.0365 # Aux V

   data5 = read_spi(5) * 0.333 # Panel V

   data6 = read_spi(6) * 0.0365 # Start V

   data7 = read_spi(7) * 0.0367 # Boat V

 

 

global temp0, temp1, temp2, temp3, temp4

# Read the 1-wire inputs

temp0 = read_temp()

temp1 = 0

temp2 = 0

temp3 = 0

temp4 = 0

 

tempC = int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1e3

 

if print_data > 0:

print("Balance: {0:0.1f}A,".format(data0)),

print("Solar: {0:0.1f}A,".format(data1)),

print("Boat: {0:0.1f}A,".format(data2)),

print("Aux: {0:0.1f}V,".format(data4)),

print("Start: {0:0.1f}V,".format(data6)),

print("Domestic: {0:0.1f}V,".format(data7)),

print("Panels: {0:0.1f}V,".format(data5)),

 

print("Ext Temp: {0:0.1f}".format(temp0)) + u"℃",

print("Core Temp: {0:0.1f}".format(tempC)) + u"℃"

 

#Eliminate small readings

if data0 < 0.15: data0 = 0

if data1 < 0.15: data1 = 0

if data2 < 0.15: data2 = 0

if data3 < 0.15: data3 = 0

if data4 < 0.15: data4 = 0

if data5 < 0.15: data5 = 0

if data6 < 0.15: data6 = 0

if data7 < 0.15: data7 = 0

 

 

# Time values for graph

global thour, tdate, tmonth, tyear, tday, ttt

tyear = str(time.strftime('%Y'))

tmonth = str(time.strftime('%B'))

tdate = str(time.strftime('%d'))

tday = str(time.strftime('%a'))

thour = str(time.strftime('%H:%M'))

ttt = time.strftime('%y%m%d%H%M')

# print tday,

 

stats()

 

if Save == 1:

f = open("data.csv", "a")

f.write(str(time.time())); f.write(',')

 

f.write(tyear); f.write(',')

f.write(tmonth); f.write(',')

f.write(tdate); f.write(',')

f.write(tday); f.write(',')

f.write(thour); f.write(',')

f.write(ttt); f.write(',')

 

f.write(str(data0)); f.write(',')

f.write(str(data1)); f.write(',')

f.write(str(data2)); f.write(',')

f.write(str(data3)); f.write(',')

f.write(str(data4)); f.write(',')

f.write(str(data5)); f.write(',')

f.write(str(data6)); f.write(',')

f.write(str(data7)); f.write(',')

 

f.write(str(temp0)); f.write(',')

f.write(str(temp1)); f.write(',')

f.write(str(temp2)); f.write(',')

f.write(str(temp3)); f.write(',')

f.write(str(temp4)); f.write(',')

 

f.write(str(AhSolar)); f.write(',')

f.write(str(AhConsumed)); f.write(',')

f.write(str(AhAux)); f.write('\n')

f.close()

 

f = open("is.txt", "w")

f.write ("SOLAR CHARGE: {0:0.1f} Ah".format(AhSolar))

f.close()

 

f = open("ic.txt", "w")

f.write ("CONSUMED CHARGE: {0:0.1f} Ah".format(AhConsumed))

f.close()

 

f = open("vb.txt", "w")

f.write ("CORE VOLTAGE: {0:0.1f} V".format(data7))

f.close()

 

f = open("time.txt", "w")

f.write ("DATA UPDATE: " + thour + ' ' + tday)

f.close()

 

#log('Test message '+str(time.strftime('%H:%M')))

 

print'.',

 

################### Statistics ##################

 

def stats():

global AhSolar, AhConsumed, AhAux, tday_old

 

if tday_old != str(time.strftime('%a')): # detect midnight

AhSolar = 0

AhConsumed = 0

AhAux = 0

tday_old = str(time.strftime('%a')) # reset day

 

AhSolar = AhSolar + (data1 * period_get_data / 3600)

AhConsumed = AhConsumed + (data2 * period_get_data / 3600)

AhAux = AhAux + (data0 * period_get_data / 3600)

# print AhSolar, AhConsumed

 

## f = open("stats.txt", "w")

## f.write (AhSolar, AhConsumed)

## f.close()

 

 

 

 

#################################################

 

 

 

get_data() # Initial run

 

 

###################### Draw Graphs #####################

 

 

def graph(type):

print ''

print 'Graphs ',str(time.strftime('%H:%M')),

 

if type == 1:

period_list = ['6 hours', '24 hours']

else:

period_list = ['6 hours', '24 hours', '7 days', '30 days', '90 days']

 

for period in period_list:

# plt.xkcd()

tt, day, hour, balanceI, solarI, boatI, auxV, panelV, startV, battV, temp0, AhSolar, AhConsumed, AhAux = np.genfromtxt('data.csv', delimiter = ',',

unpack = True, usecols=(0,4,5,7,8,9,11,12,13,14,15,20,21,22))

tnow = time.time()

 

if period == '6 hours':

tlimit = tnow - (60 * 60 * 6)

if period == '24 hours':

tlimit = tnow - (60 * 60 * 24)

elif period == '7 days':

tlimit = tnow - (60 * 60 * 24 * 7)

elif period == '30 days':

tlimit = tnow - (60 * 60 * 24 * 30)

elif period == '90 days':

tlimit = tnow - (60 * 60 * 24 * 90)

 

# mpl.rcParams['font.weight'] = 500 # Sets heading and legends only

mpl.rcParams['text.color'] = '#ff9900'

mpl.rcParams['axes.edgecolor'] = 'red'

 

 

 

fig = plt.figure(figsize=(8,20))

 

ax2 = fig.add_subplot(5,1,1, axisbg='black')

plt.title("MASTER SYSTEMS DISPLAY", fontproperties=prop)

plt.plot(tt, solarI, label='Solar', color='blue')

if (tnow - tlimit) < (60 * 60 * 24 * 7):

plt.plot(tt, boatI, label='Consumed', color='green')

## plt.plot(tt, balanceI, label='Aux', color='deepskyblue')

legend = ax2.legend(loc='best', prop={'size':11})

# frame = legend.get_frame()

# frame.set_facecolor('black')

# frame.set_edgecolor('red')

plt.legend(prop=prop, framealpha=0, loc='best')

plt.grid(color='red')

plt.ylabel('Current (A)', color='#ff9900', fontproperties=prop)

setp(ax2.get_xticklabels(), visible=False)

setp(ax2.get_yticklabels(), color='#ff9900', fontproperties=prop)

plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)# remove sci notation

ax2.ticklabel_format(style='plain', axis='x')

ax2.set_xlim(tlimit, tnow)

ax2.set_ylim(0, 20)

 

 

ax1 = fig.add_subplot(5,1,2, axisbg='black')

plt.plot(tt, battV, label='Domestic', color='red')

if (tnow - tlimit) < (60 * 60 * 24 * 7):

plt.plot(tt, startV, label='Starter', color='darkorange')

plt.plot(tt, auxV, label='Aux', color='#c12283')

legend = ax1.legend(loc='best', prop={'size':11})

plt.legend(prop=prop, framealpha=0, loc='best')

plt.grid(color='red')

plt.ylabel('Battery Voltage (V)', color='#ff9900', fontproperties=prop)

setp(ax1.get_xticklabels(), visible=False)

setp(ax1.get_yticklabels(), color='#ff9900', fontproperties=prop)

plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)# remove sci notation

ax1.ticklabel_format(style='plain', axis='x')

ax1.set_xlim(tlimit, tnow)

ax1.set_ylim(10,15)

 

if period == '6 hours' or period == '24 hours':

yy = 20

if AhSolar[-1] > yy:

yy = AhSolar[-1]

if AhConsumed[-1] > yy:

yy = AhConsumed[-1]

## if AhAux[-1] > yy:

## yy = AhAux[-1]

yy = yy + 20

else:

yy = 160

 

 

ax5 = fig.add_subplot(5,1,3, axisbg='black')

plt.plot(tt, AhSolar, label='Solar', color='blue')

#if (tnow - tlimit) < (60 * 60 * 24 * 7):

plt.plot(tt, AhConsumed, label='Consumed', color='green')

## plt.plot(tt, AhAux, label='Aux', color='deepskyblue')

legend = ax5.legend(loc='best', prop={'size':11})

# frame = legend.get_frame()

# frame.set_facecolor('black')

# frame.set_edgecolor('red')

plt.legend(prop=prop, framealpha=0, loc='best')

plt.grid(color='red')

plt.ylabel('Daily Charge (Ah)', color='#ff9900', fontproperties=prop)

setp(ax5.get_xticklabels(), visible=False)

setp(ax5.get_yticklabels(), color='#ff9900', fontproperties=prop)

plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)# remove sci notation

ax5.ticklabel_format(style='plain', axis='x')

ax5.set_xlim(tlimit, tnow)

ax5.set_ylim(0, yy)

 

ax3 = fig.add_subplot(5,1,4, axisbg='black')

plt.grid()

plt.plot(tt, temp0, color='#9898ff')

plt.grid(color='red')

plt.ylabel(u'Temp (\u00B0C)', color='#ff9900', fontproperties=prop) # \u00B0 = degree symbol setp(ax3.get_xticklabels(), visible=False)

setp(ax3.get_yticklabels(), color='#ff9900', fontproperties=prop)

plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)# remove sci notation

ax3.ticklabel_format(style='plain', axis='x')

ax3.set_xlim(tlimit, tnow)

# x = [tlimit, tnow]

# ax3.xaxis.set_ticks(x)

 

ax4 = fig.add_subplot(5,1,5, axisbg='black')

plt.grid()

plt.plot(tt, panelV, color='#ffcc66')

# ax4.fill_between(tt, panelV, color='#ffcc66')

plt.grid(color='red')

plt.ylabel('Panel Voltage (V)', color='#ff9900', fontproperties=prop)

plt.xlabel(tday + '. ' + period + ' to ' + thour, color='#ff9900', fontproperties=prop)

setp(ax4.get_xticklabels(), visible=False)

setp(ax4.get_yticklabels(), color='#ff9900', fontproperties=prop)

plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)# remove sci notation

ax4.ticklabel_format(style='plain', axis='x')

ax4.set_xlim(tlimit, tnow)

 

#plt.show()

plt.tight_layout()

savefig(period+'.png', facecolor='black')

plt.close(fig) # close figure to save memory

print '.',

print 'done'

 

# graph(1) # Initial run

 

##########Set up ftp upload #######################

 

def upload(ftp, file):

ext = os.path.splitext(file)[1]

if ext in (".txt", ".htm", ".html"):

ftp.storlines("STOR " + file, open(file))

else:

ftp.storbinary("STOR " + file, open(file, "rb"), 1024)

 

 

######################## FTP ####################

ftp_server = " "

ftp_name = " "

ftp_pwd = " "

 

 

def do_upload(type):

print 'Uploading ',str(time.strftime('%H:%M')),

try:

ftp = ftplib.FTP(ftp_server)

if ftp_out == 2:

ftp.set_debuglevel(1)

else:

ftp.set_debuglevel(0)

ftp.login(ftp_name, ftp_pwd)

 

if type > 1:

upload(ftp, "90 days.png"); print '.',

upload(ftp, "30 days.png"); print '.',

upload(ftp, "7 days.png"); print '.',

log('ALIENS DETECTED '+str(time.strftime('%H:%M')))

upload(ftp, "24 hours.png"); print '.',

upload(ftp, "6 hours.png"); print '.',

upload(ftp, "is.txt"); print '.',

upload(ftp, "ic.txt"); print '.',

upload(ftp, "vb.txt"); print '.',

upload(ftp, "time.txt"); print '.',

upload(ftp, "log.txt"); print '.',

 

## #read the TEMPERATURE file

## tempC = int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1e3

## #print tempC

##

## temp_string = '<p>uploaded: '+str(time.asctime())+ \

## '</p><p>Pi temperature: ' + '%.1f' % tempC + '°C</p>'

## #print temp_string

## f = open('ships_computer.txt', 'w')

## f.write(temp_string)

## f.close()

##

##

## upload(ftp, "ships_computer.txt")

 

ftp.quit()

print 'done'

 

except IOError as e:

temp_string = 'FTP failed: '+str(time.asctime())

print temp_string

print "I/O error({0}): {1}".format(e.errno, e.strerror)

time.sleep(2) # Wait a bit for FTP to sort itself out

print "Resuming..."

 

##if ftp_out > 0:

## do_upload(2) # Initial run

 

###################### Fridge Control ###########

 

def fridge():

data7 = read_spi(7) * 0.0367 # Update Boat V

if data7 > 13.3: # Boat batt OK

if GPIO.input(25) == 0: # Check if already on

bell(2)

relay_on(25)

print''

print'Fridge on ',str(time.strftime('%H:%M'))

log('Fridge on '+str(time.strftime('%H:%M')))

 

 

 

if data2 > (data0 + data1 + 1.0): # fridge off: Balance I + Boat I > Solar I

data7 = read_spi(7) * 0.0367 # Update Boat V

if data7 < 13.25: # Check if engine running

if GPIO.input(25) == 1:

bell(4)

relay_off(25)

print''

print'Fridge off ',str(time.strftime('%H:%M'))

log('Fridge off '+str(time.strftime('%H:%M')))

 

 

###################### Bell #####################

def bell(ting):

for i in range (0,ting):

relay_on(23)

time.sleep(0.2)

relay_off(23)

time.sleep(0.2)

time.sleep(3)

 

###################### Aux Control ###########

 

def aux():

# global data0, data1, data2, data3, data4, data5, data6, data7

 

data4 = read_spi(4) * 0.0365 # Aux batt

data7 = read_spi(7) * 0.0367 # Boat Batt

data2 = (read_spi(2) - 491.5) * 0.074 # Boat I

## print data4, data7, data2

 

if GPIO.input(24) == 1: # Check if on

if data2 < 2: # Boat I low

bell(1)

relay_off(24)

print'Aux off ',str(time.strftime('%H:%M')),' Boat current < 2A'

log('Boat I low '+str(time.strftime('%H:%M')))

 

 

if GPIO.input(24) == 1: # Check if on

if data4 < 11.6: # Aux bat low

bell(1)

relay_off(24)

print'Aux off ',str(time.strftime('%H:%M')),' Aux batt < 11.6'

log('Aux low '+str(time.strftime('%H:%M')))

 

if GPIO.input(24) == 1: # Check if on

if data7 > 13.0: # Boat bat high

bell(1)

relay_off(24)

print'Aux off ',str(time.strftime('%H:%M')),' Boat batt > 13.0V'

log('Main batt high '+str(time.strftime('%H:%M')))

 

data4 = read_spi(4) * 0.0365 # Aux batt

data7 = read_spi(7) * 0.0367 # Boat Batt

data2 = (read_spi(2) - 491.5) * 0.074 # Boat I

## print data4, data7, data2

 

 

if GPIO.input(24) == 0: # Check if off

if data7 < 12.6: # Boat Batt low

if data4 > 12.4: # Aux batt OK

if data2 > 2: # Boat current

bell(3)

relay_on(24)

print''

print'Aux on ',str(time.strftime('%H:%M'))

log('Aux on '+str(time.strftime('%H:%M')))

 

aux() # Initial run

 

 

###################### MAIN LOOP ################

 

try:

while True: # Loop indefinitely

 

if int(time.time()) > time_get_data + period_get_data: # Get data

time_get_data = int(time.time())

get_data()

 

if int(time.time()) > time_graph2 + period_graph2: # Do more graphs

time_graph2 = int(time.time())

graph(2)

if ftp_out > 0:

do_upload(2)

elif int(time.time()) > time_graph1 + period_graph1: # Do fewer graphs

time_graph1 = int(time.time())

graph(1)

if ftp_out > 0:

do_upload(1)

 

if int(time.time()) > time_fridge + period_fridge: # Fridge control

time_fridge = int(time.time())

fridge()

 

if int(time.time()) > time_aux + period_aux: # Aux control

time_aux = int(time.time())

aux()

 

 

 

 

 

GPIO.output(17,GPIO.LOW) # Turn LED off while sleeping,

time.sleep(TimeSleep)

GPIO.output(17,GPIO.HIGH) # on while working

 

 

 

except KeyboardInterrupt:

spi.close()

GPIO.cleanup()
