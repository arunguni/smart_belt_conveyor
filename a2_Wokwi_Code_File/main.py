import network
from machine import Pin, ADC
import time
from dht import DHT22
import ujson
from umqttsimple import MQTTClient

print("Connecting to WiFi")
wlan = network.WLAN(network.STA_IF) #creating WLAN object for the client mode
wlan.active(True) 
wlan.connect("Wokwi-GUEST", "") #connecting to SSID:"Wokwi-GUEST" with on password required

while not wlan.isconnected(): #wait until connected
  print(".")
  time.sleep(2) #pause two seconds and try again
print("WiFi Connected!")
time.sleep(1) #pause one second and proceed

# MQTT Server Parameters
MQTT_CLIENT_ID = "picow-01" 
MQTT_BROKER    = "a6d432d2f0a54631933788a1e8ba2111.s1.eu.hivemq.cloud" #mqtt broker address
MQTT_USER      = "client-1" 
MQTT_PASSWORD  = "Mahabharat7" #password to verify while connecting with mqtt broker
MQTT_TOPIC     = "a2/conveyorbelt" #mqtt topic to subscribe or publish to
print("Connecting to MQTT server... ")
# creating MQTT client instance
client = MQTTClient(client_id=MQTT_CLIENT_ID, 
	server=MQTT_BROKER, user=MQTT_USER, 
	password=MQTT_PASSWORD, 
	keepalive=6000,
	ssl=True,
	ssl_params={'server_hostname':'a6d432d2f0a54631933788a1e8ba2111.s1.eu.hivemq.cloud'})

client.connect() # connecting to MQTT broker using client variable's configuration
print("MQTT Connected!")

#dht22 pins
dht0 = DHT22(Pin(21))
dht1 = DHT22(Pin(6))
dht2 = DHT22(Pin(3))

#pir motion sensors pin
pir0 = Pin(22, Pin.IN) 
pir1 = Pin(14, Pin.IN)

led = Pin(2, Pin.OUT)  #led pin

#analog value of pressure Sensors signal using ADC
presSen0 = ADC(Pin(28))
presSen1 = ADC(Pin(27))
presSen2 = ADC(Pin(26))

dirPin = Pin(0, Pin.OUT)  #direction pin stepper-motor controller
stepPin = Pin(1, Pin.OUT)  #step pin steppper-motor controller

def moveStepper(direction, steps, delay):  #function to move the stepper motor according to given parameters
	dirPin.value(direction) 
	steps = abs(steps)
	for i in range(steps):  #rotating motor
		stepPin.value(1)
		time.sleep_us(delay)
		stepPin.value(0)
		time.sleep_us(delay)

productCounter = 0  #total number of counted products

tempThres = [10, 50]  #min and max temperature threshold
humThres = [10, 40]  #min and max humidity threshold
presThres = [0.5, 1.5]  #min and max pressure threshold

readSensor = 5  #every this seconds read data from the sensors and publish it to mqtt broker

startTime = time.time() - 1 #decreasing current time by 1 second to avoid divisionS by zero error if motion is detected exceptionally fast

nowTime = startTime
motorRunning = False #initialising status of motor running to false

prevTime = startTime

#outer infinity loop
while True:
	dht0.measure()
	dht1.measure()
	dht2.measure()
	
	temp = [dht0.temperature(), dht1.temperature(), dht2.temperature()]	#temperature array with values from 3 Dht sensors
	hum = [dht0.humidity(), dht1.humidity(), dht2.humidity()] #humidity array with values from 3 Dht sensors

	pres = [round(presSen0.read_u16()/800, 1), round(presSen1.read_u16()/800, 1), round(presSen2.read_u16()/800, 1)]  #dividing the voltage data from the pressure sensor to convert into appropriate psi and making array with values from 3 pressure sensors
	
	#inner infinity loop to count products
	while True:
		nowTime = time.time()  #retrive current time
		
		if min(temp)>=tempThres[0] and max(temp)<=tempThres[1] and min(hum)>=humThres[0] and max(hum)<=humThres[1] and min(pres)>=presThres[0] and max(pres)<=presThres[1]:  #checking if every sensor data is inside the defined threshhold values using
			
			led.off()  #turn off led if the motor/belt is moving

			motorRunning = True  #assign motor running  = True to indicate the motor is moving
			moveStepper(1, 1, 0)  #move motor clockwise by 5 step

			time.sleep(0.01)
			productCounter = productCounter + (pir0.value() or pir1.value()) #if pir0 or pir1 detects motion productCounter + 1
		
		else:  #if the sensor data is outside the threshold turn on led
			led.on()
			motorRunning = False	#assigning motorRunning = False to indicate the motor stopped moving

		if nowTime - prevTime >= readSensor:	#if this inner loop is executed for given seconds exit this inner loop
			prevTime = nowTime
			break

	prodPerMin = round(productCounter / ((nowTime - startTime) / 60))	#calculating product per minute
	prodPerHr = round(productCounter / ((nowTime - startTime) / 3600))	#calculating products per hour
	prodPerDay = round(productCounter / ((nowTime - startTime) / 86400))	#calculating products per day
	
	#if motorRunning is true print the information
	if motorRunning:
		print("Motor Running...")
		print("Products: " + str(productCounter))
		print("Product/Minute: " + str(prodPerMin))
		print("Product/Hour: " + str(prodPerHr)) 
		print("Product/Day: " + str(prodPerDay))
		print("Temperature: " + str(temp[0]) + "°C, " + str(temp[1]) + "°C, " + str(temp[2]) + "°C")  #print current temp
		print("Humidity: " + str(hum[0]) + "%, " + str(hum[1]) + "%, " + str(hum[2]) + "%")   #print current humidity
		print("Pressure: " + str(pres[0]) + "psi, " + str(pres[1]) + "psi, " + str(pres[2]) + "psi")  #print current pressure
	
	#if motor is not running print the error message
	else:
		print("Error! Environment threshold reached. Motor stopped....")

	#make a json object with the given properties
	message = ujson.dumps({	
		"belt": motorRunning,
		"products": productCounter,
		"prodPerMin": prodPerMin,
		"prodPerHr": prodPerHr,
		"prodPerDay": prodPerDay,
		"temp": temp,
		"hum": hum,
		"pres": pres,
	})

	#publish the json object message to broker as given topic
	client.publish(MQTT_TOPIC, message)