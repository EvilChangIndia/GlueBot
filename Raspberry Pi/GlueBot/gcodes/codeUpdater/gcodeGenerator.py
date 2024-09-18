homeGcodeFileLocation = "/home/pi/GlueBot/gcodes/homeGcode.txt"
glueGcodeFileLocation = "/home/pi/GlueBot/gcodes/glueGcode.txt"
configFileLocation = "/home/pi/GlueBot/gcodes/codeUpdater/config.txt" 



class generator():
    def __init__(self, c = configFileLocation, g = glueGcodeFileLocation, h= homeGcodeFileLocation):
        self.configLocation = c
        self.glueFileLocation = g
        self.homeFileLocation= h

        with open(self.configLocation, 'r') as configFile:
            self.config = configFile.read().splitlines()

        self.liftup = float(self.config[10]) #in mm
        self.defaultRate = int(self.config[9])
        self.startWaitTime = float(self.config[11])
        self.waitTime = float(self.config[12])
        self.feedRate = 0
        self.Gcode = ["G21", "G90", "G94", "\n"]
        #default values of points
        #point a1
        self.a1y = float(self.config[0])
        self.a1z = float(self.config[1])
        self.a1a = float(self.config[2])
        #point a2
        self.a2y = float(self.config[3])
        self.a2z = float(self.config[4])
        self.a2a = float(self.config[5])
        #point a3
        self.a3y = float(self.config[6])
        self.a3z = float(self.config[7])
        self.a3a = float(self.config[8])
        #home location (origin)
        self.hy = float(self.config[13])
        self.hz = float(self.config[14])
        self.ha = float(self.config[15])

    def addMove0(self, seq=[], y=0, z=0, a=0):
        newLine = "G0 Y" + str(y) + " Z" + str(z) + " A" + str(a) 
        seq.append(newLine)
        return

    def addMove1(self, seq=[], y=0, z=0, a=0, newRate= -1):
        if newRate == -1:
            newLine = "G1 Y" + str(y) + " Z" + str(z) + " A" + str(a)
        else:
            newLine = "G1 Y" + str(y) + " Z" + str(z) + " A" + str(a) + " F" + str(newRate) 
            self.feedRate=newRate
        seq.append(newLine)
        return

    def addGlue(self, seq = [], state = 0, wait= -1):
        if state:
            seq.append("M3 S100")
            newLine = "G4 P" + (str(wait) if wait!=-1 else str(self.waitTime))
            seq.append(newLine)
        else:
            seq.append("M5")
        return

    def updateConfig(self):
        self.config=[str(self.a1y),str(self.a1z),str(self.a1a),str(self.a2y),str(self.a2z),str(self.a2a),str(self.a3y),str(self.a3z),str(self.a3a),str(self.defaultRate),str(self.liftup),str(self.startWaitTime),str(self.waitTime),str(self.hy),str(self.hz),str(self.ha)]
        with open(self.configLocation, 'w') as c:
            c.write('\n'.join(self.config))

    def updateA1(self, a1y, a1z):
        self.a1y= a1y
        self.a1z= a1z
        #now write it to config file
        self.updateConfig()
        return
    
    def updateA2(self, a2y, a2z):
        self.a2y= a2y
        self.a2z= a2z
        #now write it to config file
        self.updateConfig()
        return
    
    def updateA3(self, a3y, a3z):
        self.a3y= a3y
        self.a3z= a3z
        #now write it to config file
        self.updateConfig()
        return
    
    def updateFeedRate(self,feed= 1500):
        self.defaultRate=feed
        self.updateConfig()
        return

    def updateWaitTimes(self, startWaitTime= 0, waitTime= 0):
        self.startWaitTime= startWaitTime
        self.waitTime= waitTime
        self.updateConfig()
        return


    def updateHomeGcode(self):
        #LEFT-SIDE SEQUENCE : seq1
        seq1 = ["G21 ; millimeters","G90 F2000 ; absolute coordinate", "G94 ; units per minute feed rate mode", "$H", "G4 P0.1", "$HA", "G4 P0.1"]
        newLine = "G10 P0 L20 Y" + str(0-self.hy) + " Z" + str(0-self.hz) + " A" + str(360-self.ha)
        seq1.append(newLine)
        seq1.append("\n")

        #ADD TO FILE
        with open(self.homeFileLocation, 'w') as f:
            f.write('\n'.join(seq1))

    def updateGlueGcode(self):
        #LEFT-SIDE SEQUENCE : seq1
        seq1 = [";SEQUENCE 1","G90", "G0 Z100"]
        self.addMove0(seq1, self.a1y - self.liftup, 100, self.a1a)
        self.addMove0(seq1, self.a1y - self.liftup, self.a1z + self.liftup, self.a1a)
        #switch incremental
        seq1.append("G91")
        #ab
        seq1.append(";ab")
        self.addMove1(seq1, self.liftup,-self.liftup,0,self.defaultRate)
        self.addGlue(seq1, 1)
        self.addMove1(seq1, 7, 7)
        self.addGlue(seq1, 0)
        self.addMove1(seq1, 2, 2)
        self.addMove1(seq1, 2, -1.5) #dip-off glue
        self.addMove1(seq1, -2, 1.5) #dip-off glue
        self.addMove1(seq1, -self.liftup, self.liftup) #lift up
        #cd
        seq1.append(";cd")
        self.addMove1(seq1, 8, 8)
        self.addMove1(seq1, self.liftup,-self.liftup)#lift down
        self.addGlue(seq1, 1)
        self.addMove1(seq1, 2.5, 2.5)
        self.addGlue(seq1, 0)
        self.addMove1(seq1, 2, 2)
        self.addMove1(seq1, 2, -1.5) #dip-off glue
        self.addMove1(seq1, -2, 1.5) #dip-off glue
        self.addMove1(seq1, -self.liftup, self.liftup) #lift up
        #efghi
        seq1.append(";efghi")
        self.addMove1(seq1, 6.5, 6.5)
        self.addMove1(seq1, self.liftup,-self.liftup)#lift down
        self.addGlue(seq1, 1)
        self.addMove1(seq1,50,50)
        self.addMove1(seq1,4,4.5)
        self.addMove1(seq1,5.2,1.5)
        self.addMove1(seq1,4.8,-1.7)
        self.addGlue(seq1, 0)
        self.addMove1(seq1, 3.5, -3.5)
        self.addMove1(seq1,0,-2.5)
        self.addMove1(seq1, 0, 2.5)
        self.addMove1(seq1, self.liftup, self.liftup) #lift up
        seq1.append("\n")

        #RIGHT-SIDE SEQUENCE: seq2
        seq2 = [";SEQUENCE 2", "G90", "G0 Z100"]
        self.addMove0(seq2, self.a2y + self.liftup, self.a2z + self.liftup, self.a2a)#a2
        #switch incremental
        seq2.append("G91")
        #a2b2
        seq2.append(";a2b2")
        self.addMove1(seq2, -self.liftup,-self.liftup,0,self.defaultRate)#lift down
        self.addGlue(seq2, 1, self.startWaitTime) #glue on
        self.addMove1(seq2, -7, 7)
        self.addGlue(seq2, 0) #glue off
        self.addMove1(seq2, -2, 2)
        self.addMove1(seq2, -2, -1.5) #dip-off glue
        self.addMove1(seq2, 2, 1.5) #dip-off glue
        self.addMove1(seq2, self.liftup, self.liftup) #lift up
        #c2d2
        seq2.append(";c2d2")
        self.addMove1(seq2, -7.5, 7.5)#c2
        self.addMove1(seq2, -self.liftup,-self.liftup)#lift down
        self.addGlue(seq2, 1) #glue on
        self.addMove1(seq2, -2.5, 2.5)
        self.addGlue(seq2, 0) #glue off
        self.addMove1(seq2, -2, 2)
        self.addMove1(seq2, -2, -1.5) #dip-off glue
        self.addMove1(seq2, 2, 1.5) #dip-off glue
        self.addMove1(seq2, self.liftup, self.liftup) #lift up
        #e2f2g2h2i2
        seq2.append(";e2f2g2h2i2")
        self.addMove1(seq2, -6.5, 6.5)
        self.addMove1(seq2, -self.liftup,-self.liftup)#lift down
        self.addGlue(seq2, 1) #glue on
        self.addMove1(seq2, -50, 50)
        self.addMove1(seq2, -4, 4)
        self.addMove1(seq2, -4.5, 1.5)
        self.addMove1(seq2,-4.8,-1.7)
        self.addGlue(seq2, 0) #glue off
        self.addMove1(seq2, -2.5, -2.5)
        self.addMove1(seq2,0,-2.5)#dip-off glue
        self.addMove1(seq2, 0, 2.5)#dip-off glue
        self.addMove1(seq2, -self.liftup, self.liftup) #lift up
        seq2.append("\n")

        #BOTTOM SEQUENCE: seq3
        seq3 = [";SEQUENCE 3","G90 Z90"]
        self.addMove0(seq3, self.a3y + self.liftup, self.a3z + self.liftup, self.a3a)#a3
        #switch incremental
        seq3.append("G91")
        self.addMove1(seq3, -self.liftup,-self.liftup,0,self.defaultRate)#lift down
        self.addGlue(seq3, 1) #glue on
        self.addMove1(seq3,-2,4.5)
        self.addMove1(seq3,-7,4.25)
        self.addMove1(seq3,-40) 
        self.addMove1(seq3,-4,-1.25)
        self.addGlue(seq3, 0) #glue off
        self.addMove1(seq3,-3,-3)
        self.addMove1(seq3,43,0,35)############################tune thiss
        self.addMove1(seq3,-1,-1.5) #dip-off glue
        self.addMove1(seq3,-10,-10) #dip-off glue
        self.addMove1(seq3,-5,5) #lift up
        seq3.append("\n")

        #combine sequences in required order
        self.Gcode= self.Gcode + seq2 + seq1 + seq3
        #self.Gcode.append("G90")
        #self.Gcode.append("G90 Z100")
        self.Gcode.append("\n")
        #ADD TO FILE
        with open(self.glueFileLocation, 'w') as f:
            f.write('\n'.join(self.Gcode))

def enterHomeCoordinates(gcode):
    gcode.hy = float(input("Enter Coordinate of point \'ORIGIN\'\nY: "))
    gcode.hz = float(input("Z: "))
    gcode.ha = float(input("A: "))
    gcode.updateConfig()
    return

def enterCoordinates(gcode):
    gcode.a1y = float(input("Enter Coordinate of point \'a1\'\nY: "))
    gcode.a1z = float(input("Z: "))
    gcode.a1a = float(input("A: "))

    gcode.a2y = float(input("Enter Coordinate of point \'a2\'\nY: "))
    gcode.a2z = float(input("Z: "))
    gcode.a2a = float(input("A: "))

    gcode.a3y = float(input("Enter Coordinate of point \'a3\'\nY: "))
    gcode.a3z = float(input("Z: "))
    gcode.a3a = float(input("A: "))
    #now write it to config file
    gcode.updateConfig()
    return

if __name__ == '__main__':
    Gcode=generator(configFileLocation,glueGcodeFileLocation, homeGcodeFileLocation)
    print("GLUEBOT GCODE MAKER\n")
    while True:
        print("WHAT IS YOUR DEEPEST DARKEST DESIRE??\n\n0:EXIT.\n\n1: Update start coordinates\n   [({c1},{c2},{c3}) , ({c4},{c5},{c6}) , ({c7},{c8},{c9})]\n\n2: Update feedrate[{feed}].\n\n3: Update glue dispensing wait times[({start},{normal})].\n\n4: Update home/origin location[({hy},{hz},{ha})] \n\n5: Update Gcode with current settings. ".format(c1=Gcode.a1y, c2=Gcode.a1z, c3=Gcode.a1a, c4=Gcode.a2y, c5=Gcode.a2z, c6=Gcode.a2a, c7=Gcode.a3y, c8=Gcode.a3z, c9=Gcode.a3a, feed=Gcode.defaultRate, start=Gcode.startWaitTime, normal=Gcode.waitTime, hy=Gcode.hy, hz=Gcode.hz, ha=Gcode.ha))
        choice= int(input("\nEnter your choice: "))
        
        if choice==0:
            break

        if choice==1:
            enterCoordinates(Gcode)

        if choice==2:
            feedRate=int(input("Enter the desired rate: "))
            Gcode.updateFeedRate(feedRate)
       
        if choice==3:
            startWaitTime=float(input("Enter the desired start wait time: "))
            waitTime=float(input("Enter the desired normal wait time: "))
            Gcode.updateWaitTimes(startWaitTime, waitTime)
        
        if choice==4:
            enterHomeCoordinates(Gcode)

        if choice==5:
            Gcode.updateGlueGcode()
            Gcode.updateHomeGcode()

            
        
        print("Operation Completed!")
