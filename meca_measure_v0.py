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
import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

robot = mdr.Robot()

#initalize variables
wireDiameter = []
tray = []

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
    returnHome()
    robot.DeactivateRobot()
    robot.Disconnect()
    print('Now disconnected from the robot.')
    
def resetRobot():
    robot.ResetError()
    robot.ResumeMotion()
    
def readBarcode():
    moveBarcode ()
    s = socket.socket()
    s.connect(('192.168.0.200', 2001))
    s.send('< >'.encode())
    print (s.recv(1024).decode())
    s.close()
    
def moveCircle (): 
    moveTrayWaypoint()
    robot.Delay(0.25)
    robot.MoveLin(180,-127,140,0,90,0) #top left
    robot.Delay(0.25)
    robot.MoveLin(180,56.5,140,0,90,0) #top right
    robot.Delay(0.25)
    robot.MoveLin(260,56.5,140,0,90,0) #bottom right
    robot.Delay(0.25)
    robot.MoveLin(260,-127,140,0,90,0) #bottom left
    robot.Delay(0.25)

def moveMeasure ():
    robot.MovePose(225,140,135,-90,0,90) #keyence measurement way point
    
def moveBarcode ():
    robot.MovePose(225,17.5,170,-90,0,90) #keyence measurement way point

def moveTrayWaypoint ():
    robot.MovePose(225,-38,150,0,90,0) #pickup waypoint
    
def measureWires ():
    global wireDiameter 
    
    #moveMeasure()
    s = socket.socket()
    s.connect(('192.168.0.201', 8601))
    s.send("GM,0,0\r".encode())
    rawDiameter = s.recv(2048).decode("utf-8")
    print("raw measurement is:", rawDiameter)
    
    wireDiameter = rawDiameter.split(',')
    wireDiameter = wireDiameter [2:]
    wireDiameter = [float(i) for i in wireDiameter]    #convert all strings to floats
    wireDiameter = [i for i in wireDiameter if i > 0]  #filter out negative values (no measure from keyences shows up as -9999.99999 mm)
    
    print("Wire diameters are:", wireDiameter)
    s.close()
    
    # for i in range(4):
    #     robot.MoveLinRelTrf(0, 0, 9.5, 0, 0, 0)
    #     print(i)
    #     robot.Delay(0.25)
    
def pickFx(i):
    robot.MovePose(*(tray[i]))
    robot.MoveLinRelTrf(59, 0, 0, 0, 0, 0)
    robot.GripperClose()
    robot.MoveLinRelTrf(-65, 0, 0, 0, 0, 0)
    moveTrayWaypoint()
    
def placeFx(i):
    robot.MovePose(*(tray[i]))
    robot.MoveLinRelTrf(57, 0, 0, 0, 0, 0)
    robot.GripperOpen()
    robot.MoveLinRelTrf(-57, 0, 0, 0, 0, 0)
    moveTrayWaypoint()
    
def pickNplace():
    for i in range(10):
        pickFx(i)
        readBarcode()
        placeFx(i)


connectRobot()    
init()
x=0

while x == 0:
    pickNplace()