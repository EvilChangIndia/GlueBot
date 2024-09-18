#debugMode control
#debugMode = 0 #turns off all terminal outputs
debugMode = 1 #output on terminal


#The machine states are as follows
#state 0: FailSafe
#state 1: OFF
#state 2: Un Clamped
#state 3: Homing
#state 4: Safety
#state 5: Clamped
#state 6: gluing
#state 7: framing


import readline
from subprocess import call
from tabnanny import check
from xml.sax.handler import property_declaration_handler
import RPi.GPIO as GPIO 
from threading import Thread
import time
import gi 
gi.require_version('Gtk', '3.0')            # Load the correct namespace and version of GTK
from gi.repository import Gtk               # Include the python bindings for GTK
from gi.repository import GLib              # included for adding things to gtk main loop
import serial


#import UI glade file into a GTK.Builder object
gladeFile = "glueBotUI_v1.glade"      #gladeFile holding the UI XML file. maybe give full path
builder = Gtk.Builder()            # GTK Builder called 
builder.add_from_file(gladeFile)   # GTK Builder passed the XML file path for translation

#define window and notebook onjects and link it to our design using the builder object
notebook=builder.get_object("mainNotebook")
window = builder.get_object("mainWindow")
unclampedTextBox = builder.get_object("unclampedTextBox").get_buffer()
clampedTextBox = builder.get_object("clampedTextBox").get_buffer()
glueTextBox = builder.get_object("glueTextBox").get_buffer()
confirmTextBox = builder.get_object("confirmTextBox").get_buffer()
loadingTextBox = builder.get_object("loadingTextBox").get_buffer()

#pages are (0-off page 1-unclamped page 2-clamped page 3-glue page 4-confirm page, 5-loading page, 6-framing page)
#define pages 
page = { 1:0, 2:1, 3:5, 4:5, 5:2, 6:3, 7:6 }		#{state:corresponding page number} #make page for failsafe and loading
currentPage = 0


#actions
activity={0:"Entering Failsafe", 1:"Turning the machine OFF...", 2:"Turning the machine ON and Un-Clamping...", 3:"Homing...", 4:"Moving to safe space", 5:"Clamping...", 6:"Gluing..."}

#state names 
stateName={0:"Failsafe", 1:"OFF", 2:"Un-Clamped", 3:"Homing", 4:"Safety",  5:"Clamped", 6:"Gluing", 7:"Framing"}

#full USB address of clamp ESP depending on which RPi port it is connected to
esp_ID = '/dev/ttyUSB0'      
#esp_ID = '/dev/ttyUSB1' 
#esp_ID = '/dev/ttyUSB2' 
#esp_ID = '/dev/ttyUSB3' 

#READ THE GLUING GCODE
gluingFile = open("/home/pi/GlueBot/gcodes/glueGcode.txt",'r')
gluingGcode = gluingFile.readlines()
gluingGCodeLen = len(gluingGcode)
gluingGCodeIter  = 0
gluingFile.close

#READ THE HOMING GCODE
homingFile = open("/home/pi/GlueBot/gcodes/homeGcode.txt",'r')
homingGcode = homingFile.readlines()
homingGCodeLen = len(homingGcode)
homingGCodeIter  = 0
homingFile.close

#READ THE HOMING GCODE
safetyFile = open("/home/pi/GlueBot/gcodes/safetyGcode.txt",'r')
safetyGcode = safetyFile.readlines()
safetyGCodeLen = len(safetyGcode)
safetyGCodeIter  = 0
safetyFile.close

#pages are (0-off page 1-unclamped page 2-clamped page 3-glue page 4-confirm page)
#define a class for handling on UI inputs
class UIHandler:
	#onDestroy triggers. can use just one onDestroy 
	autoPageChange = 1
	addTextClamped = ""
	addTextUnclamped = ""
	addTextLoading = ""
	addTextGlue = ""
	addTextOn = ""
	confirmAction = 0	#0-shutdown	1-abort gluing

	def onDestroy(self, *args):
		say("Destroy triggered")
		Gtk.main_quit()

	def confirm(self, action=confirmAction):
		if self.confirmAction:
			say("Aborting gluing process..")
			glueBot.glue(False)
			#abort code here
		else:
			say("Shutting down..")
			#replace with shutdown cli-commands
			Gtk.main_quit()
			GPIO.cleanup()
			
	#button triggers
	def onButtonPressShutdown(self, button):
		say("Shutdown button pressed")
		#change comnfirm page text here
		self.confirmAction = 0
		self.autoPageChange = 0
		confirmTextBox.set_text("Confirm Shutdown?")
		notebook.set_current_page(4)
		
		
	def onButtonPressConfirm(self, button):
		say("Confirm button pressed")
		self.autoPageChange = 1
		self.confirm()

	def onButtonPressCancel(self,button):
		say("Continuing...")
		self.autoPageChange = 1
		
	def onButtonPressOn(self, button):
		say("ON button pressed")
		#turn to machine-on page
		
		if glueBot.turnOn():
			say("Machine ON")
		#check success?
		#switch to un-clamped state page
		#notebook.set_current_page(page[clamp1.state])
	
	def onButtonPressOff(self, button):
		say("OFF button pressed")
		if glueBot.turnOff():
			say("Machine OFF")
		#notebook.set_current_page(page[clamp1.state])
		#write else part
	
	def onButtonPressHome(self, button):
		say("Home button pressed")
		if glueBot.home():
			say("Homing successful")
			self.addTextUnclamped ="\nCalibration Successful"
		else:
			say("Calibration failed")
			self.addTextUnclamped ="Calibration failed. See logs for debugging..."
			#add failsafe?

	def onButtonPressClamp(self, button):
		self.addTextGlue = ""
		say("clamp button pressed")
		self.addTextClamped =""
		if not glueBot.isSafe:
			say("Move to safety before clamping..")
			self.addTextUnclamped ="\nMove to safety before clamping.."

		elif not glueBot.clamp(True):
			#failsafe
			say("Clamping failed")
			self.addTextClamped ="\nClamping failed. Try again"
		#notebook.set_current_page(page[clamp1.state])
	
	def onButtonPressUGS(self, button):
		say("UGS button clicked")
		call(["/home/pi/ugsplatform-linux-arm/bin/ugsplatform"]) #runs in terminal

	def onButtonPressSafety(self, button):
		say("SAFETY button pressed")
		glueBot.safety()
	
	def onButtonPressUnclamp(self, button):
		say("un-clamp button pressed")
		self.addTextClamped =""
		self.addTextUnclamped=""
		if glueBot.isSafe:
			if not glueBot.clamp(False):
				#failsafe
				say("Un-Clamping failed")
		else:
			say("Move to safety before clamping..")
			self.addTextClamped ="Move to safety before clamping.."
		#notebook.set_current_page(page[clamp1.state])

	def onButtonPressStart(self, button):
		say("Start button pressed")
		self.addTextGlue = "Gluing..."
		self.autoPageChange = 1
		glueBot.glue(True)
		
	def onButtonPressAbort(self, button):
		say("Abort button pressed")
		self.confirmAction = 1
		self.autoPageChange = 0
		confirmTextBox.set_text("Abort gluing operation?")
		notebook.set_current_page(4)
	
	def onButtonPressCentre(self, button):
		say("Centre button pressed!")
		glueBot.isSafe=1
		glueBot.centreRotor()
	
	def onButtonPressTF1(self, button):
		say("TF1 button pressed!")
		glueBot.isSafe=0
		glueBot.setRotor(45)

	def onButtonPressTF2(self, button):
		say("TF2 button pressed!")
		glueBot.isSafe=0
		glueBot.setRotor(-135)
	
	def onButtonPressBF(self, button):
		say("BF button pressed!")
		glueBot.isSafe=0
		glueBot.setRotor(-225)




UI = UIHandler()

class GlueBot:
	#gcodeOf= {"homeRotor": "G0 A0", "absoluteDistance":"G90\n", "storage": "storage postion", "safety":"safe position", 5:"gcode for clamping", "clamp": "gcode for clamping", 2:"gcode for un-clamping", "unclamp":"gcode for un-clamping", "home":"$H"}
	gcodeOf= { "absoluteDistance":"G90\n", "storage": "g90 z50 y145\n", 5:"M8\n", "clamp":"M8\n", 2:"M9\n", "unclamp":"M9\n", "home":"\n"}
	expectedReply = {"general":"ok", "home":"ok", "":"ok"}
	#gluingGcode=["G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n","G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n","G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n", "G0 Y10\n","G0 Y-10\n"]
	def __init__(self, id = '/dev/ttyUSB0',baudrate = 115200 ):
		self.ID=id
		self.state = 1
		self.prevState = 1
		self.engaged = 1
		self.baudrate = baudrate
		self.espReply = ""
		self.gluing = 0
		self.isSafe = 0

	def connect(self):
		say("trying to connect to ESP at "+self.ID)
		self.esp = serial.Serial(self.ID, self.baudrate, timeout=1)
		self.esp.reset_input_buffer()
		self.sendLine("$G\n")
		self.sendLine("$X\n")
	
	def sendLine(self, line="?"):
		self.espReply=""
		say("Trying to send gcode: "+line )
		self.esp.write(line.encode('utf-8'))
		while self.espReply =="":
			self.espReply = self.esp.readline().decode('utf-8').rstrip()
		#say("Reply from ESP: "+self.espReply + "\n")
		return True

	#def sendCode(self):
	#	for gcode in gluingGcode:
	#		self.sendLine(gcode)
	#	say("done")
	#	self.gluing = False
	#	self.state = self.prevState

	def glue(self, flag = True):
		global gluingGCodeIter
		self.prevState=self.state
		if flag:
			gluingGCodeIter = 0
			self.state = 6
			self.gluing = True
			notebook.set_current_page(page[glueBot.state])
			say("starting glueCode execution..")
			#self.sendCode() #PUT IN A THREAD

		else:
			gluingGCodeIter = -1
			say("stopping glueCode execution")
			#ADD CODE FOR STOPPING THREAD AND SENDING A STOP COMMAND
			self.state = 5
			self.gluing = False

	def startupRoutine(self):
		say("Trying to connect to the GlueBot..")
		UI.addTextLoading="Trying to connect to the GlueBot.."
		#try:
		self.connect()
		#set distances in absolute coordinates
		self.sendLine(self.gcodeOf["absoluteDistance"])
		#move rotor to home
		self.isSafe=1
		self.clamp(False)
		self.home()
		return True
		#except FileNotFoundError:
		#	say("Robot no connected! check usb connection to esp..")
		#	return False
		#except:
		#	say("Unknown Error. Check usb connection to esp..")
		#	return False

	def testRun(self):
		say("Trying to connect to the GlueBot..")
		self.connect()
		#set distances in absolute coordinates
		self.sendLine(self.gcodeOf["absoluteDistance"])
		say("doing the y axis Jiggle jiggle gcode")
		self.sendCode()

	def turnOn(self):
		say("Trying to turn machine ON and unclamp ")
		#turn machine on
		if self.startupRoutine():
			say("Machine on and ready!")
			return 1
		else:
			self.state= 1
			say("Machine failed to turn on..")
			return 0

	def clamp(self, yes):
		self.prevState=self.state
		if self.isSafe:
			say("actuating clamp..")
			UI.addTextLoading="actuating clamp.."
			self.state = 5 if yes else 2
			self.sendLine(self.gcodeOf[self.state])
			#status = self.sendLine(self.gcodeOf[self.state])
			#if status=="yes":
			say("Machine clamped") if yes else say("Machine Un-clamped")
			self.engaged = 1 if yes else 0
			return 1
		else:
			say("Move to safety before clamping..")
			UI.addTextUnclamped="Move to safety before (un)clamping.."
			UI.addTextClamped="Move to safety before (un)clamping.."
			return 0
		#self.state = self.prevState
		#return 0

	def turnOff(self):
		self.prevState=self.state
		say("Trying to move to storage position..")
		self.sendLine(self.gcodeOf["storage"])
		say("Trying to turn machine OFF")
		self.state = 1
		#self.sendLine()
		return True

	#change to specific reply dependant on send code type
	def checkReply(self, codeType = "general"):
		if self.espReply != None:
			if (self.espReply==self.expectedReply[codeType]):	
					say("Expected reply received!")
					return True
			else:
				say("Unexpected reply received!")
				return False
		say("Received empty response from esp!")
		return False
	
	#complete calibration function
	def home(self):
		self.prevState = self.state
		say("Trying to ensue homing procedure...")
		UI.addTextLoading="Homing..."
		self.state = 3
		return True
	
	def safety(self):
		self.isSafe=0
		self.prevState = self.state
		say("Switching to SAFETY state...")
		UI.addTextLoading="Moving to safety.."
		self.state = 4
		return True
	
	def setRotor(self, angle = 0):
		say("setting rotor to angle: "+ str(angle))
		gcd="G90 A"+str(angle)+"\n"
		return self.sendLine(gcd)
	
	def centreRotor(self):
		self.isSafe=1
		say("centring the rotor..")
		return self.setRotor(0)
	

glueBot=GlueBot(esp_ID)	


def updateTextBoxes():
	clampedTextBox.set_text("Machine is in state "+stateName[glueBot.state]+"\n\n"+UI.addTextClamped)
	unclampedTextBox.set_text("Machine is in state "+stateName[glueBot.state]+"\n\n"+UI.addTextUnclamped)
	glueTextBox.set_text(UI.addTextGlue)
	loadingTextBox.set_text(UI.addTextLoading)
	#confirmTextBox.set_text("gluing in progress..")
	return True

def updatePage():
	#give condition to check for state change
	if UI.autoPageChange == 1:
		notebook.set_current_page(page[glueBot.state])
	return True

def gcodeHandler():
	global gluingGCodeIter
	global homingGCodeIter
	global safetyGCodeIter
	#if gluingGCodeIter == -1:
	#	say("sending abort code : ")
	if glueBot.state==6 and gluingGCodeIter!=-1:	# for gluing . and 'gluingGCodeIter!=-1' means abort
		if gluingGCodeIter < gluingGCodeLen:
			glueBot.sendLine(gluingGcode[gluingGCodeIter])
			gluingGCodeIter +=1
		else: 
			say("Gluing successful!")
			glueBot.gluing = False
			glueBot.state = 7
			glueBot.safety()
			gluingGCodeIter = 0
			UI.addTextGlue = "Done gluing!\nPress UNCLAMP.."

	if glueBot.state==3 and homingGCodeIter!=-1:
		if homingGCodeIter < homingGCodeLen:
			glueBot.sendLine(homingGcode[homingGCodeIter])
			homingGCodeIter +=1
		else:
			say("Done homing!")
			homingGCodeIter = 0
			say("moving to safety")
			glueBot.state = 2
			glueBot.safety()
			UI.addTextUnclamped = "Done Homing!\nReady to CLAMP"

	if glueBot.state==4 and safetyGCodeIter!=-1:
		if safetyGCodeIter < safetyGCodeLen:
			glueBot.sendLine(safetyGcode[safetyGCodeIter])
			safetyGCodeIter +=1
		else:
			say("Moved to safety!")
			safetyGCodeIter = 0
			glueBot.state = glueBot.prevState
			glueBot.isSafe=1

	return True

#function for printing on terminal
def say(output): 
	if debugMode==1:
		print(output)
	return

def main():
	#connect the callbacks from glade file widgets
	builder.connect_signals(UI)
	#make UI window fullscreen
	window.fullscreen()
	#display the UI
	window.show()
	#run robot startup routine
	#glueBot.startupRoutine()
	#initiate the gtk main loop
	Gtk.main()
	#glueBot.testRun()
	

if __name__ == "__main__":
	try:
		GLib.timeout_add(200, updateTextBoxes)     #adds function to gtk main loop
		#GLib.timeout_add(200, pedalUpdateState)
		GLib.timeout_add(500, updatePage)
		GLib.timeout_add(200, gcodeHandler)
		
		main()
	except KeyboardInterrupt:
		say("Execute GPIO-cleanup")
		GPIO.cleanup()
	#finally:
	#	say("Execute GPIO-cleanup")
	#	GPIO.cleanup()
