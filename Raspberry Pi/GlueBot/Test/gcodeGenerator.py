liftup = 10 #in mm
defaultRate = 1500
startWaitTime = 0.8
waitTime = 0.5
feedRate= 0
Gcode = ["G21", "G90", "G94", "\n"]

fileLocation = "/home/pi/GlueBot/gcodes/glueGcode.txt"

#default values of points
a1y = -53
a1z = -14.5
a1a = 45

a2y = 53.5
a2z = -13.5
a2a = -45

a3y = 29.5
a3z = 67.5
a3a = -180

def addMove0(seq=[], y=0, z=0, a=0):
    newLine = "G0 Y" + str(y) + " Z" + str(z) + " A" + str(a) 
    seq.append(newLine)
    return

def addMove1(seq=[], y=0, z=0, a=0, newRate= defaultRate):
    global feedRate
    if newRate!=feedRate:
        newLine = "G1 Y" + str(y) + " Z" + str(z) + " A" + str(a) + " F" + str(newRate) 
        feedRate=newRate
    else:
        newLine = "G1 Y" + str(y) + " Z" + str(z) + " A" + str(a)
    seq.append(newLine)
    return

def addGlue(seq = [], state = 0, wait = waitTime):
    if state:
        seq.append("M3 S100")
        newLine = "G4 P" + str(wait)
        seq.append(newLine)
    else:
        seq.append("M5")
    return
def updateValues():
    global a1y
    global a1z
    global a1a
    global a2y
    global a2z
    global a2a
    global a3y
    global a3z
    global a3a
    a1y = int(input("Enter Coordinate of point \'a1\'\nY: "))
    a1z = int(input("Z: "))
    a1a = int(input("A: "))

    a2y = int(input("Enter Coordinate of point \'a2\'\nY: "))
    a2z = int(input("Z: "))
    a2a = int(input("A: "))

    a3y = int(input("Enter Coordinate of point \'a3\'\nY: "))
    a3z = int(input("Z: "))
    a3a = int(input("A: "))
    return

def updateFeedRate():
    global defaultRate
    defaultRate=int(input("Enter the desired rate: "))
    return

if __name__ == '__main__':
    print("GLUEBOT GCODE MAKER\n")
    while True:
        print("What is your deepest, darkest desire?\n0:Exit.\n1: Update start coordinates[({c1},{c2}) , ({c3},{c4}) , ({c5},{c6})]\n2: Update feedrate[{feed}].\n3: Make Gcode with current settings".format(c1=a1y, c2=a1z, c3=a2y, c4=a2z, c5=a3y, c6=a3z, feed=defaultRate))
        choice= int(input("Enter your choice: "))
        
        if choice==0:
            break
        if choice==1:
            updateValues()
        if choice==2:
            updateFeedRate()
        if choice==3:
            #SEQUENCE 1 : seq1
            seq1 = [";SEQUENCE 1","G90 Z100"]
            addMove0(seq1, a1y - liftup, a1z + liftup, a1a)
            #switch incremental
            seq1.append("G91")
            #ab
            addMove1(seq1, liftup,-liftup,0,defaultRate)
            addGlue(seq1, 1, startWaitTime)
            addMove1(seq1, 4, 4)
            addGlue(seq1, 0)
            addMove1(seq1, 5, 5)
            addMove1(seq1, 2, -1.5) #dip-off glue
            addMove1(seq1, -2, 1.5) #dip-off glue
            addMove1(seq1, -liftup, liftup) #lift up
            #cd
            addMove1(seq1, 6.5, 6.5)
            addMove1(seq1, liftup,-liftup)#lift down
            addGlue(seq1, 1)
            addMove1(seq1, 2.5, 2.5)
            addGlue(seq1, 0)
            addMove1(seq1, 2, 2)
            addMove1(seq1, 2, -1.5) #dip-off glue
            addMove1(seq1, -2, 1.5) #dip-off glue
            addMove1(seq1, -liftup, liftup) #lift up
            #efghi
            addMove1(seq1, 6.5, 6.5)
            addMove1(seq1, liftup,-liftup)#lift down
            addGlue(seq1, 1)
            addMove1(seq1,50,50)
            addMove1(seq1,4,4)
            addMove1(seq1,5.2,2.5)
            addMove1(seq1,4.4,-1.5)
            addMove1(seq1,0.4,-0.2)
            addGlue(seq1, 0)
            addMove1(seq1, 3.5, -3.5)
            addMove1(seq1,0,-1.5)
            addMove1(seq1, 0, 1.5)
            addMove1(seq1, liftup, liftup) #lift up
            seq1.append("\n")

            #SEQUENCE 2: seq2
            seq2 = [";SEQUENCE 2", "G90 Z100"]
            addMove0(seq2, a2y + liftup, a2z + liftup, a2a)#a2
            #switch incremental
            seq2.append("G91")
            #a2b2
            addMove1(seq2, -liftup,-liftup,0,defaultRate)#lift down
            addGlue(seq2, 1) #glue on
            addMove1(seq2, -4, 4)
            addGlue(seq2, 0) #glue off
            addMove1(seq2, -5, 5)
            addMove1(seq2, -2, -1.5) #dip-off glue
            addMove1(seq2, 2, 1.5) #dip-off glue
            addMove1(seq2, liftup, liftup) #lift up
            #c2d2
            addMove1(seq2, -7.5, 7.5)#c2
            addMove1(seq2, -liftup,-liftup)#lift down
            addGlue(seq2, 1) #glue on
            addMove1(seq2, -2.5, 2.5)
            addGlue(seq2, 0) #glue off
            addMove1(seq2, -2, 2)
            addMove1(seq2, -2, -1.5) #dip-off glue
            addMove1(seq2, 2, 1.5) #dip-off glue
            addMove1(seq2, liftup, liftup) #lift up
            #e2f2g2h2i2
            addMove1(seq2, -6.5, 6.5)
            addMove1(seq2, -liftup,-liftup)#lift down
            addGlue(seq2, 1) #glue on
            addMove1(seq2, -50, 50)
            addMove1(seq2, -4, 2.8)
            addMove1(seq2, -4.8, 2.7)
            addMove1(seq2,-4.8,-2)
            addGlue(seq2, 0) #glue off
            addMove1(seq2, -3.2, -3.2)
            addMove1(seq2,0,-1)#dip-off glue
            addMove1(seq2, 0, 1)#dip-off glue
            addMove1(seq2, -liftup, liftup) #lift up
            seq2.append("\n")

            #SEQUENCE 3: seq3
            seq3 = [";SEQUENCE 3","G90"]
            addMove0(seq3, a3y + liftup, a3z + liftup, a3a)#a3
            #switch incremental
            seq3.append("G91")
            addMove1(seq3, -liftup,-liftup,0,defaultRate)#lift down
            addGlue(seq3, 1) #glue on
            addMove1(seq3,-1.5,4)
            addMove1(seq3,-7,4.25)
            addMove1(seq3,-41)
            addGlue(seq3, 0) #glue off
            addMove1(seq3,-7,-4.25)
            addMove1(seq3,-2,-4)
            addMove1(seq3,2) #dip-off glue
            addMove1(seq3,-1,5) #lift up
            seq3.append("\n")

            #combine sequences
            Gcode= Gcode + seq1 + seq2 + seq3
            Gcode.append("\n")
            #ADD TO FILE
            with open(fileLocation, 'w') as f:
                f.write('\n'.join(Gcode))
        
        print("Operation Completed!")