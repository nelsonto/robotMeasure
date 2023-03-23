# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 14:53:54 2023

@author: NelsonChunManTo
"""

import mecademicpy.robot as mdr
import socket
import cv2

robot = mdr.Robot()

tray = []
for i in range(10):
    tray.append(tuple((179.350006,-130.494995+(i*20.183333),142,0,90,0)))
        
def connectRobot():
    robot.Connect(address='192.168.0.100', disconnect_on_exception=False, enable_synchronous_mode=True)
    print('Connected to robot')  
def init():
    connectRobot()
    print('Initalizing Robot: Activate, home, set limits...')
    robot.ActivateRobot()
    robot.Home()
    
    # Pause execution until robot is homed.
    robot.WaitHomed()
    print('Robot is homed and ready.')
    
    returnHome()
    robot.SetGripperForce(30)
    robot.SetGripperRange(0,8)
    robot.GripperOpen()   
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
    movePickupWaypoint()
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
    moveMeasure()
    for i in range(4):
        robot.MoveLinRelTrf(0, 0, 9.5, 0, 0, 0)
        print(i)
        robot.Delay(0.25)
    
def pickFx(i):
    robot.MovePose(*(tray[i]))
    robot.MoveLinRelTrf(60, 0, 0, 0, 0, 0)
    robot.GripperClose()
    robot.MoveLinRelTrf(-65, 0, 0, 0, 0, 0)
    moveTrayWaypoint()
    
def placeFx(i):
    robot.MovePose(*(tray[i]))
    robot.MoveLinRelTrf(55, 0, 0, 0, 0, 0)
    robot.GripperOpen()
    robot.MoveLinRelTrf(-55, 0, 0, 0, 0, 0)
    moveTrayWaypoint()
    
def pickNplace():
    for i in range(3):
        pickFx(i)
        readBarcode()
        placeFx(i)
        
    
# Pos 1 [179.350006,-130.494995,142,0,90,0]
# Pos 10 [179.350006,51.154999,142,0,90,0]
