from machine import Pin, I2C
from struct import unpack
from time import sleep
import machine, onewire, ds18x20, time
from ssd1306 import SSD1306_I2C
import utime
import math
from machine import Pin, I2C
import sdcard
import uos
led = Pin(25, Pin.OUT)


# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(13, machine.Pin.OUT)

# Intialize SPI peripheral (start with 1 MHz)
spi=machine.SPI(1,baudrate=40000000,sck=Pin(10),mosi=Pin(11),miso=Pin(12))



# Initialize the SD card
spi=machine.SPI(1,baudrate=40000000,sck=Pin(10),mosi=Pin(11),miso=Pin(12))
# Create a instance of MicroPython Unix-like Virtual File System (VFS),
sd = sdcard.SDCard(spi, Pin(13))
 

# Debug print SD card directory and files
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")


global SHUNT_OHMS
SHUNT_OHMS = 0.1

ina_i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=100000)
ds_pin = machine.Pin(22)
#ina_i2c.scan()

class ina219:
    REG_CONFIG = 0x00
    REG_SHUNTVOLTAGE = 0x01
    REG_BUSVOLTAGE = 0x02
    REG_POWER = 0x03
    REG_CURRENT = 0x04
    REG_CALIBRATION = 0x05
    
    def __init__(self,sr, address, maxi):
        self.address = address
        self.shunt = sr
            
    def vshunt(icur):
        # Read Shunt register 1, 2 bytes
        reg_bytes = ina_i2c.readfrom_mem(icur.address, icur.REG_SHUNTVOLTAGE, 2)
        reg_value = int.from_bytes(reg_bytes, 'big')
        if reg_value > 2**15: #negative
            sign = -1
            for i in range(16): 
                reg_value = (reg_value ^ (1 << i))
        else:
            sign = 1
        return (float(reg_value) * 1e-4 * sign)
        
    def vbus(ivolt):
        # Read Vbus voltage
        reg_bytes = ina_i2c.readfrom_mem(ivolt.address, ivolt.REG_BUSVOLTAGE, 2)
        reg_value = int.from_bytes(reg_bytes, 'big') >> 3
        return float(reg_value) * 0.004
        
    def configure(conf):
        #ina_i2c.writeto_mem(conf.address, conf.REG_CONFIG, b'\x01\x9F') # PG = 1
        #ina_i2c.writeto_mem(conf.address, conf.REG_CONFIG, b'\x09\x9F') # PG = /2
        ina_i2c.writeto_mem(conf.address, conf.REG_CONFIG, b'\x11\x9F') # PG = /3
        #ina_i2c.writeto_mem(conf.address, conf.REG_CONFIG, b'\x19\x9F') # PG = /4
        ina_i2c.writeto_mem(conf.address, conf.REG_CALIBRATION, b'\x00\x00')

        
print('Found a ds18x20 device')
# Create current measuring object
oled = SSD1306_I2C(128, 64, ina_i2c)
ina = ina219(SHUNT_OHMS, 64, 5)
ina.configure()
utime.sleep_ms(10)

ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()


# Write sample text

    
    
# Close the file


start = time.ticks_ms()

while True:
    oled.fill(0)    
    utime.sleep_ms(10)
    v = ina.vbus()
    utime.sleep_ms(10) # Delay to avoid micropython error
    i = ina.vshunt()
    utime.sleep_ms(10) # Delay to avoid micropython error
    p = i * v
    ds_sensor.convert_temp()
    utime.sleep_ms(10)
    for rom in roms:
        tmp = ds_sensor.read_temp(rom)
    #print("t = %d" %  (time.ticks_diff(time.ticks_ms(),start)/100) ,", U = %.3f" % v ,", I = %.3f" % i , ", P = %.2f" % p, ", Temp = %.2f" % tmp)
    sleep(1)
    oled.text("P = %.3f" % p, 0, 0)
    oled.text("U = %.3f" % v, 0, 16)
    oled.text("I = %.3f" % i, 0, 32)
    oled.text("Temp = %.2f" % tmp, 0, 48)
    with open("/sd/data.txt", "a")  as file:
        led.value(1)
        file.write(str(time.ticks_diff(time.ticks_ms(),start)/1000))
        file.write(";")
        file.write(str(v))
        file.write(";")
        file.write(str( i) )
        file.write(";")
        file.write(str(p))
        file.write(";")
        file.write(str( tmp))
        file.write("\r\n")
        led.value(0)
        
    time.sleep(1)
    oled.show()
    time.sleep(14)