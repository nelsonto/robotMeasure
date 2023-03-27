# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 14:53:54 2023

@author: NelsonChunManTo
"""
## IP addresses:
# Mecademic meca500 robot - 192.168.0.100
# Omron Hawkeye Barcode Reader V430-F - 192.168.0.200, port 2001
# Keyence TM-X5000 - 192.168.0.201, port 8601

import mecademicpy.robot as mdr
import socket
import cv2
import time
import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

robot = mdr.Robot()

#initalize variables
tray = []
fixture=[]
for i in range(10):
    fixture.append({"fxnumber": 0, "wire1":[0], "wire2":[0], "wire3":[0], "wire4":[0]})


# connect to meca500
def connectRobot():
    robot.Connect(address='192.168.0.100', disconnect_on_exception=False, enable_synchronous_mode=True)
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
    robot.GripperOpen()
    initTrayPositions()

def initTrayPositions():
    global tray
    for i in range(10):
        tray.append(tuple((179.350006,-130.494995+(i*20.183333),142,0,90,0)))
    
def returnHome():
    robot.MoveJoints(0,0,0,0,0,0)
    print('Robot is zeroed.') 
    
def disconnectRobot():
    robot.WaitIdle()
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
    robot.MovePose(225,140,135,-90,0,90) #keyence measurement way point
    
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
    numSamples = 100    #Number of sampling points
    rawstring = ""
    for i in range(numSamples):
        rawstring = rawstring +",Raw"+str(i+1)
        
    headerFormat = "DateTime,OperatorID, EquipmentID, LotID,SensorNumber,FixtureID,SensorID,TipDiameter"+ rawstring +"\n"
    file = open ("Data\wireDiameter-" + time.strftime("%Y%m%d-%H%M%S") +"_" + fixture[i]["fxnumber"] + ".csv", 'w')
    file.write(headerFormat)
    
    for j in range (4):
        file.write(time.strftime('%m/%d/%y %H:%M,') + 'N/A'+ ',' + 'EQ-318 TMX,' + lotID.get() + ',' + str(i+1) + ',' + fixture[i]["fxnumber"] + ',' + fixture[i]["fxnumber"] + '-' + str(j+1) + ',' + 'TipDiameter,')
        file.write (fixture[i]["wire"+str(j)])
        file.write('\n')
    
    file.close()
    
def measureWires (i):
    global fixture
    moveMeasure()
#    robot.MoveLinRelTrf(0, 0, 0, 0, 0, 0)  ## move into first wire position
    for j in range (4):
        robot.MoveLinRelTrf(0, 0, 9.5, 0, 0, 0)
        fixture[i]["wire"+str(j)]=  print ("readKeyence") #readKeyence()
        robot.Delay(0.25)
    
    recordData(i);
#    robot.MoveLinRelTrf(0, 0, 0, 0, 0, 0)  ## return to keyence waypoint   
    
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

def endProgram():  
    if messagebox.askokcancel("Quit", "Robot Disconnected.\nAre you sure you want to quit?"):
        window.destroy()
        
    if (robot.GetStatusRobot().activation_state == 1):
        disconnectRobot()
    
    print ('Exiting')

def plotData(i):
    global fixture
    x = [[],[],[],[]]
    for i in range (100):
        x[i].append(0.03*i)
    
    figure.clear()
    plt = figure.add_subplot(111)

    plt.set_title('Wire Diameter - FX-' + fixture[i]["fxnumber"],color='black',fontsize=10)
    plt.plot(x[0],fixture[i]["wire1"],label="wire 1", color="red")
    plt.plot(x[1],fixture[i]["wire2"],label="wire 2", color="orange")
    plt.plot(x[2],fixture[i]["wire3"],label="wire 3", color="green")
    plt.plot(x[3],fixture[i]["wire4"],label="wire 4", color="blue")
    
    plt.set_xlabel('X (mm)')
    plt.set_ylabel('Diameter (mm)')
    plt.legend(loc="best")
    plt.grid(color = 'grey', linestyle = '-', linewidth = 0.5)
    
    figure.tight_layout()

    canvas.draw()
    canvas.flush_events()
    canvas.get_tk_widget().pack()
    toolbar.update()
    canvas.get_tk_widget().pack()
    

window = tk.Tk()
window.title('TM-X5006 Auto Wire Diameter Measurement')  
    
lotID=tk.StringVar()
wireType=tk.IntVar()

frmInput=tk.Frame()
frmGraph=tk.Frame()

frmInput.grid(row=1, column=0, sticky="nw",padx=5, pady=5)
frmGraph.grid(row=1, column=1, sticky="nw",padx=5, pady=5)

figure = Figure(figsize=(10, 8), dpi=100)
canvas = FigureCanvasTkAgg(figure, master = frmGraph)
toolbar = NavigationToolbar2Tk(canvas,frmGraph)
    
tk.Label(master=frmInput,text="Lot #:", font=('Arial',12), anchor="e", width= 10).grid(row=1, column=0, pady=(20,20))
entLOT = tk.Entry(master=frmInput, textvariable = lotID, font=('Arial',12), width=12)
entLOT.grid(row=1, column=1, pady=(20,20), padx=(5,5), ipady=5, ipadx=5)


##wireType 0 = working wire, 1 = reference wire
#tk.Label(master=frmInput,text="Reference Wire", anchor="e", width = 22).grid(row=3, column=0, pady=(0,15))
entTypeCheck = tk.Checkbutton(master=frmInput, text='Reference', font=('Arial',12), variable=wireType, onvalue=1, offvalue=0)
entTypeCheck.grid(row=3, column=1, sticky="w", pady=(0,15))

btnConnect = tk.Button(master=frmInput, command = init, text="Connect Robot", width = 17, height=2)
btnReset = tk.Button(master=frmInput, command = resetRobot, text="Reset Robot", width = 17, height=2)
btnMeasure = tk.Button(master=frmInput, command = pickNplace, text="Measure Wires", width = 17, height=2, bg="#FFEBB3")
btnExit= tk.Button(master=frmInput, command = endProgram, text="Disconnect & Exit", width = 17, height=2)

btnMeasure.grid(row=6, column=0, columnspan=2, sticky="e", pady=(0,10))
btnConnect.grid(row=7, column=0, columnspan=2, sticky="e", pady=(0,10))
btnReset.grid(row=8, column=0, columnspan=2, sticky="e", pady=(0,10))
btnExit.grid(row=9, column=0, columnspan=2, sticky="e", pady=(0,10))

window.protocol("WM_DELETE_WINDOW", endProgram)
window.mainloop()
