import time
import board
import adafruit_dht
from datetime import datetime
from zoneinfo import ZoneInfo
import RPi.GPIO as GPIO
import boto3

sensor = adafruit_dht.DHT22(board.D4, use_pulseio=False) # This is my sensor.
fan = 26 # This is the GPIO of my fan.
heat = 25 # This is the GPIO of my heater.
fan_status = False # This sets my fan status as off.
heat_status = False # This sets my heater status as off.
spray_status = False # This sets the sprayer status as off.
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(fan, GPIO.OUT)
GPIO.setup(heat, GPIO.OUT)


# This while loop continues until the sensor does NOT have an error and gets a reading.
# If the sensor does get an error, the error is handled and we continue with the loop.
def get_temp():
    while True:
        try:
            temp = sensor.temperature
            temp = temp * (9/5) + 32
            humidity  = sensor.humidity
            temptime = datetime.now(ZoneInfo("America/Denver"))
            timestamp = temptime.strftime("%Y-%m-%d %H:%M:%S")
            # print(f"Temp:{temp:.1f} Humidity:{humidity:.1f}")
            return temp, humidity, timestamp
        except RuntimeError as error:
            time.sleep(2.0)
            continue

        except Exception as error:
            sensor.exit()
            raise error

def heater_on():
    GPIO.output(heat, True) # True turns the heater on.
    global heat_status
    heat_status = True
    print("Heater turning on")

def heater_off():
    GPIO.output(heat, False) # False turns the heater off.
    global heat_status
    heat_status = False
    print("Heater turning off")

def fan_on():
    GPIO.output(fan, True) # True turns the fan on.
    global fan_status
    fan_status = True
    print("Fan turning on")

def fan_off():
    GPIO.output(fan, False) # False turns the fan off.
    global fan_status
    fan_status = False
    print("Fan turning off")

def spray_on():
    global spray_status
    spray_status = True
    print("Sprayers turing on")

def spray_off():
    global spray_status
    spray_status = False
    print("Sprayers turing off")

def main():
    wanted_temp = 77
    wanted_humid = 30
    global heat_status, fan_status, spray_status

    client = boto3.resource(service_name = 'dynamodb', region_name = 'us-east-1', 
        aws_access_key_id = '', 
        aws_secret_access_key = '')
    table = client.Table('Capstone-DynamoDB')
    print(table.table_status)

    while True:
        try:
            temp, humid, timestamp = get_temp() # get_temp returns temperature, humidity, and timestamp.
            print(f"Temp:{temp:.1f}   Humidity:{humid:.1f}  Time:{timestamp}")
            if temp >= (wanted_temp-1) and heat_status is True:
                heater_off()
            elif temp <= wanted_temp and fan_status is True:
                fan_off()
            elif temp < (wanted_temp-1) and heat_status is False:
                heater_on()
            elif temp > wanted_temp and fan_status is False:
                fan_on()

            if spray_status is False:
                if humid < wanted_humid:
                    spray_on()
            else:
                spray_off()


            item = {'TimeStamp':timestamp,'Temperature':int(temp),'Humidity':int(humid),'FanStatus':fan_status, 'HeaterStatus':heat_status, 'SprayStatus':spray_status}
            table.put_item(Item=item)


            # I have this here to make sure the heater and fan functions are
            # not being called over and over again, and to make sure my loop
            # is functioning as it should.
            print("Working!")
            time.sleep(15)

        # This handles when I end the program and if the fan or heater is on,
        # it will turn them both off and exit with out errors.
        except KeyboardInterrupt as error:
            heater_off()
            fan_off()
            spray_off()
            print("Shutting Down")
            exit()


if __name__ == '__main__':
    main()
