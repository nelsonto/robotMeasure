# -*- coding: utf-8 -*-
"""
3/28/2023
V0: EQ-318 - Mecademic Robot + Keyence TMX
- first deployed for use in production cleanroom

"""
## IP addresses:
# Mecademic meca500 robot - 192.168.0.100
# Omron Hawkeye Barcode Reader V430-F - 192.168.0.200, port 2001
# Keyence TM-X5000 - 192.168.0.201, port 8601

import os
import mecademicpy.robot as mdr
import socket
import time
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from skiveMeasure import skiveMeasure

robot = mdr.Robot()

#format graphs
plt.style.use('default')
plt.rcParams.update({'font.size': 8})

#Make a data folder if one doesn't exist
if not os.path.exists('Data'):
   os.makedirs('Data')
   
#initalize system variables
scanWidth = 0.03   #interval width of each scanned region
numSamples = 100    #Number of sampling points
tray = []
# fixture=[]
for i in range(10):
    fixture.append({"fxnumber": 0, "wire0":[0], "wire1":[0], "wire2":[0], "wire3":[0]})

# connect to meca500
def connectRobot():
    robot.Connect(address='192.168.0.100', disconnect_on_exception=True, enable_synchronous_mode=True)
    print('Connected to robot')

# initialize robot
def init():
    connectRobot()
    print('Initalizing Robot: Activate, home, set limits...')
    robot.ActivateRobot()
    robot.Home()
    robot.WaitHomed() # Pause execution until robot is homed.
    print('Robot is homed and ready.')
    
    returnHome()
    robot.SetGripperForce(30)
    robot.SetGripperRange(0,8)
    robot.SetJointVel(50)
    robot.GripperOpen()
    initTrayPositions()

def initTrayPositions():
    global tray
    for i in range(10):
        tray.append(tuple((178.75+(i*-0.11111),-130+(i*20.183333),142,0,90,0)))

def returnHome():
    robot.MoveJoints(0,0,0,0,0,0)
    print('Robot is zeroed.') 
    
def disconnectRobot():
    robot.WaitIdle()
    returnHome()
    robot.DeactivateRobot()
    robot.Disconnect()
    print('Deactivated and disconnected from the robot.')
    
def resetRobot():
    if (robot.GetStatusRobot().error_status == 1):
        robot.ResetError()
        robot.ResumeMotion()
        
    returnHome()
    print('Reset and Resume Motion to Robot.')
    
def readBarcode():
    moveBarcode ()
    s = socket.socket()
    s.connect(('192.168.0.200', 2001))
    s.send('< >'.encode())
    barcode = s.recv(1024).decode()
    s.close()
    return barcode

def moveMeasure ():
    robot.MovePose(150,87,160,-90,0,90) #keyence measurement way point
    
def moveBarcode ():
    robot.MovePose(225,17.5,170,-90,0,90) #keyence measurement way point

def moveTrayWaypoint ():
    robot.MovePose(225,-38,150,0,90,0) #pickup waypoint
    
def readKeyence ():
    wireDiameter = []
    
    s = socket.socket()
    s.connect(('192.168.0.201', 8601))
    s.send("GM,0,0\r".encode())
    rawDiameter = s.recv(2048).decode("utf-8")
    
    wireDiameter = rawDiameter.split(',')
    wireDiameter = wireDiameter [2:]
    wireDiameter = [float(i) for i in wireDiameter]    #convert all strings to floats
    wireDiameter = [i for i in wireDiameter if i > 0]  #filter out negative values (no measure from keyences shows up as -9999.99999 mm)
    
    print("Wire diameter:", wireDiameter)
    s.close()    
    return wireDiameter

def recordData(i):
    global fixture
    global numSamples

    rawstring = ""
    for j in range(numSamples):
        rawstring = rawstring +",Raw"+str(j+1)
        
    headerFormat = "DateTime,OperatorID, EquipmentID, LotID,SensorNumber,FixtureID,SensorID,TipDiameter,skiveWidth,tipLength"+ rawstring +"\n"
    file = open ("Data\wireDiameter-" + time.strftime("%Y%m%d-%H%M%S") +"_" + str(fixture[i]["fxnumber"]) + ".csv", 'w')
    file.write(headerFormat)
    
    for j in range (4):
        try:
            tipDiameter = max(fixture[i]["wire"+str(j)][0:9])  #only look for the max diameter in the first 0.25mm of the wire
        except:
            tipDiameter = 0
        
        fixture[i]["skiveWidth_wire"+str(j)], fixture[i]["tipLength__wire"+str(j)] = skiveMeasure(fixture[i]["wire"+str(j)])
        
        file.write(time.strftime('%m/%d/%y %H:%M,') + 'N/A'+ ',' + 'EQ-318 TMX,' + lotID.get() + ',' + str(j+1) + ',' + str(fixture[i]["fxnumber"]) + ',' + str(fixture[i]["fxnumber"]) + '-' + str(j+1) + ',' + str(tipDiameter) + ','+ fixture[i]["skiveWidth_wire"+str(j)] + ',' + str(fixture[i]["tipLength_wire"+str(j)]) + ',')
        file.write (str(fixture[i]["wire"+str(j)])[1:-1])
        file.write('\n')
    
    file.close()
    
def measureWires (i):
    global fixture
    moveMeasure()
    
    if (wireType.get() == 0):
        robot.MovePose(150,142.9,152.625,-90,0,90)     #pre wire 1 position for reference wire
    else:
        robot.MovePose(150,142.9,157.625,-90,0,90)     #pre wire 1 position for working wire

    for j in range (4): 
        robot.MoveLinRelTrf(0, 0, 9.25, 0, 0, 0)
        robot.Delay(0.75)
        fixture[i]["wire"+str(j)]= readKeyence()
    moveMeasure()
    recordData(i)
    
def pickFx(i):
    robot.MovePose(*(tray[i]))
    robot.MoveLinRelTrf(59, 0, 0, 0, 0, 0)
    robot.WaitIdle()
    robot.GripperClose()
    robot.MoveLinRelTrf(-65, 0, 0, 0, 0, 0)
    moveTrayWaypoint()
    
def placeFx(i):
    robot.MovePose(*(tray[i]))
    robot.MoveLinRelTrf(57, 0, 0, 0, 0, 0)
    robot.WaitIdle()
    robot.GripperOpen()
    robot.MoveLinRelTrf(-57, 0, 0, 0, 0, 0)
    moveTrayWaypoint()
    
def pickNplace():
    global fixture
    for i in range(10):
        pickFx(i)
        fixture[i]["fxnumber"] = readBarcode()
        print ("readBarcode for position: ", i, " is ", fixture[i]["fxnumber"])
        if fixture[i]["fxnumber"] != 'NOREAD':
            measureWires(i)
        placeFx(i)
    plotData()

def endProgram():  
    if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
        window.destroy()
        if (robot.GetStatusRobot().activation_state == 1):
            disconnectRobot()
            print ('Disconnecting Robot')
        print ('Closing Program')
    
def plotData():
    global fixture
    global scanWidth
    
    figure.clf()
        
    for k in range (len(fixture)):
        print("now plotting:", k)
        if fixture[k]["fxnumber"]!= 0:
            plt = figure.add_subplot(3,4,k+1)
            x = [[],[],[],[]]
            
            for i in range (4):
                for j in range (len(fixture[k]["wire"+str(i)])):
                    x[i].append(scanWidth*j)
                if fixture[k]["skiveWidth_wire"+str(i)]=='N/A':
                    plt.set_facecolor("yellow")
            
            plt.set_title(str(fixture[k]["fxnumber"]),color='black',fontsize=10)
            
            plt.plot(x[0],fixture[k]["wire0"],label="1")
            plt.plot(x[1],fixture[k]["wire1"],label="2")
            plt.plot(x[2],fixture[k]["wire2"],label="3")
            plt.plot(x[3],fixture[k]["wire3"],label="4")
            
            plt.set_xlabel('X (mm)')
            plt.set_ylabel('Diameter (mm)')
            plt.legend(loc="best")
            plt.grid(color = 'grey', linestyle="--", linewidth = 0.25)
    
    canvas.draw()
    canvas.flush_events()
    canvas.get_tk_widget().pack()

window = tk.Tk()
window.title('TM-X5006 Auto Wire Diameter Measurement')  
    
lotID=tk.StringVar()
wireType=tk.IntVar()

frmInput=tk.Frame()
frmGraph=tk.Frame()

frmInput.grid(row=1, column=0, sticky="nw",padx=20, pady=5)
frmGraph.grid(row=1, column=1, sticky="nw",padx=5, pady=5)

figure = Figure(figsize=(13.5, 9), dpi=96, tight_layout=True)
canvas = FigureCanvasTkAgg(figure, master = frmGraph)
    
tk.Label(master=frmInput,text="Lot #:", font=('Arial',12), anchor="e", width= 4).grid(row=1, column=0, pady=(20,20))
entLOT = tk.Entry(master=frmInput, textvariable = lotID, font=('Arial',12), width=12, justify='center')
entLOT.grid(row=1, column=1, pady=(20,20), padx=(5,5), ipady=5, ipadx=5)

entTypeCheck = tk.Checkbutton(master=frmInput, text='Reference', font=('Arial',12), variable=wireType, onvalue=1, offvalue=0) #wireType 0 = working wire, 1 = reference wire
entTypeCheck.grid(row=3, column=1, sticky="w", pady=(0,15))

btnConnect = tk.Button(master=frmInput, command = init, text="Connect Robot", width = 18, height=2)
btnReset = tk.Button(master=frmInput, command = resetRobot, text="Reset Robot", width = 18, height=2)
btnMeasure = tk.Button(master=frmInput, command = pickNplace, text="Measure Wires", width = 18, height=2, bg="#FFEBB3")
btnExit= tk.Button(master=frmInput, command = endProgram, text="Disconnect & Exit", width = 18, height=2)
btnPlt= tk.Button(master=frmInput, command = plotData, text="PlotGraphs", width = 18, height=2)

btnMeasure.grid(row=6, column=0, columnspan=2, sticky="e", pady=(0,10))
btnConnect.grid(row=7, column=0, columnspan=2, sticky="e", pady=(0,10))
btnReset.grid(row=8, column=0, columnspan=2, sticky="e", pady=(0,10))
btnExit.grid(row=9, column=0, columnspan=2, sticky="e", pady=(0,10))
btnPlt.grid(row=10, column=0, columnspan=2, sticky="e", pady=(0,10))

window.protocol("WM_DELETE_WINDOW", endProgram)
window.mainloop()
