

import serial #for serial communication with GSM SIM800L
import time 
import pygame #to play music
import numpy as np
import RPi.GPIO as gpio

Interrupt_Pin = 12
gpio.setmode(gpio.BOARD)
gpio.setup(Interrupt_Pin,gpio.IN, pull_up_down=gpio.PUD_DOWN)

# _____________________________________________________________________________#
# Intro text
print("Setting up Raspberry PI IVR")




#Speak with SIM800 -> gets AT command return as response
def SIM800(command):
	AT_command = command + "\r\n"
	ser.write(str(AT_command).encode('ascii'))
	time.sleep(1)
	if ser.inWaiting() > 0:
		echo = ser.readline() #waste the echo
		response_byte = ser.readline()
		response_str = response_byte.decode('ascii')
		return (response_str)
	else:
		return ("ERROR")

#checks if SIM800L is speaking and returns it as response
def wait_for_SIM800():
	echo = ser.readline()  # waste the echo
	response_byte = ser.readline()
	response_str = response_byte.decode('ascii')
	return (response_str)

#Checks SIM800L status and connects with ShopifyAPI
def Init_GSM():

	if "OK" in SIM800("AT"):
		if ("OK" in (SIM800("AT+CLCC=1"))) or ("OK" in (SIM800("AT+DDET=1"))) or ("OK" in (SIM800("AT+CNMI =0,0,0,0,0"))) or ("OK" in (SIM800("AT+CMGF=1"))) or ("OK" in (SIM800("AT+CSMP=17,167,0,0"))):  # enble DTMF / disable notifications
			print("SIM800 Module -> Active and Ready")
	else:
		print("------->ERROR -> SIM800 Module not found")

#plays the given wav file #8000Mhz mono audio WAV works best on SIM800L
def play_wav(file_name):
	pygame.mixer.init()
	pygame.mixer.music.load(file_name)
	pygame.mixer.music.play()
	
# Makes a call to given number and returns NONE, NOT_REACHABLE, CALL_REJECTED, REJECTED_AFTER_ANSWERING,  REQ_CALLBACK,CANCELED, CONFIRMED
def Call_response_for (phone_number):
	AT_call = "ATD" + phone_number + ";"
	response = "NONE"

	time.sleep(1)
	ser.flushInput() #clear serial data in buffer if any

	if ("OK" in (SIM800(AT_call))) and (",2," in (wait_for_SIM800())) and (",3," in (wait_for_SIM800())):
		print("RINGING...->", phone_number)
		call_status = wait_for_SIM800()
		if "1,0,0,0,0" in call_status:
			print("**ANSWERED**")
			ser.flushInput()
			play_wav("voice .wav") #replace it with our voice message
			time.sleep(14)
			response = "CALL_ANSWERED"
			hang = SIM800("ATH")
			time.sleep(0.5)
		else:
			print("REJECTED")
			response = "CALL_REJECTED"
			hang = SIM800("ATH")
			time.sleep(1)
			ser.flushInput()
	else:
		print("NOT_REACHABLE")
		response = "NOT_REACHABLE"
		hang = SIM800("ATH")
		time.sleep(1)
		ser.flushInput()

	ser.flushInput()
	return (response)

#Receives the message and phone number and send that message to that phone number
def send_message(message, recipient):
	ser.write(b'AT+CMGF=1\r\n')
	time.sleep(3)
	ser.write(b'AT+CMGS="' + recipient.encode() + b'"\r')
	time.sleep(0.5)   
	ser.write(message.encode() + b"\r")
	#ser.write(b'\x1A')
	time.sleep(0.5)
	ser.write(bytes([26]))
	time.sleep(0.5)
	print ("Message sent to customer")
	time.sleep(2)

def incoming_call():
	while ser.in_waiting: #if I have something in the serial monitor
		print ("%%Wait got something in the buffer")
		ser.flushInput()
		response = SIM800("ATH") #cut the incoming call
		if "+CLCC" in response:
			cus_phone = response[21:31]
			print("%%Incoming Phone call detect from ->", cus_phone)
			return (cus_phone)
		else:
			print("Nope its something else")
			return "0"
	return "0"

cus_name = "Aisha"
cus_phone = "+201206255912"
location= "30.620094,32.268776"
print(cus_phone)

while (1): #Infinite loop

	# COM defanition for windows -> Should change for Pi
	ser = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=15)  # timeout affects call duration and waiting for response currently 30sec
	serialPort = serial.Serial(
		port="/dev/ttyUSB1", baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
	)
	serialString = ""  # Used to hold data coming over UART
	#waiting_bytes = serialPort.in_waiting
	#if waiting_bytes >= 0:
		#print(serialPort.in_waiting)
		#print("hi")
	serialPort.flushInput()
	gpio.wait_for_edge(Interrupt_Pin,gpio.RISING)
		# Read data out of the buffer until a carraige return / new line is found
	serialString = serialPort.readline().decode("utf-8")
		#print(serialString)
		# Print the contents of the serial data
	try:
		print(serialString)
	except:
		pass
	#serialString="30.620094,32.268776"
	#print(serialString)

	print("Established communication with", ser.name)

	Init_GSM() #check if GSM is connected and initialize it

	print("_____________________IVR START___________________")
	

	response = Call_response_for(cus_phone) #place a call and get response from customer
	print ("Response from customer   => ", response)

	if response == "CALL_ANSWERED":
		 text_message = "help me ,this is my location maps.google.com/?q="+serialString
		 send_message(text_message, cus_phone)
		 print("**ANSWERE123456**")
		 

	if ((response == "CALL_REJECTED") or (response == "NOT_REACHABLE")):  
		text_message = "Help me, this is my location maps.google.com/?q="+serialString
		send_message(text_message, cus_phone)
	  

	print("_____________________IVR END___________________")

	ser.close()
	serialPort.close()
	time.sleep (5)
	break

#chr()
#, timeout=0
#.decode('ascii').rstrip()









