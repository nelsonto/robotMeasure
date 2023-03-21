# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 14:53:54 2023

@author: NelsonChunManTo
"""

import mecademicpy.robot as mdr
import socket
import cv2

def init():
    robot.ActivateRobot()
    robot.Home()
    robot.SetGripperForce(5)
    robot.SetGripperRange(5,15)
    

with mdr.Robot() as robot:

    # Check IP address connection
    try:
        robot.Connect(address='192.168.0.100', disconnect_on_exception=False, enable_synchronous_mode=True)
        print('Connected to robot')
    except mdr.CommunicationError as e:
        print(f'Robot failed to connect. Is the IP address correct? {e}')
        raise e

    try:
        # Send the commands to get the robot ready for operation.
        print('Initalizing Robot: Activate, home, set limits...')
        init();
        
        # Pause execution until robot is homed.
        robot.WaitHomed()
        print('Robot is homed and ready.')

        # Send motion commands to have the robot draw out a square.
        robot.MovePose(200, 0, 300, 0, 90, 0)
        
        print('Waiting for robot to finish moving...')
        robot.WaitIdle(60)
        print('Robot finished drawing square.')

    except Exception as exception:
        # Attempt to clear error if robot is in error.
        if robot.GetStatusRobot().error_status:
            print(exception)
            print('Robot has encountered an error, attempting to clear...')
            robot.ResetError()
            robot.ResumeMotion()
        else:
            raise
            
    # Deactivate the robot.
    robot.DeactivateRobot()
    print('Robot is deactivated.')

# At the end of the "with" block, robot is automatically disconnected
print('Now disconnected from the robot.')




def returnHome ():
    robot.MoveJoints(0,0,0,0,0,0)
    robot.Delay(2)
    
def disconnectRobot():
    returnHome();
    robot.Delay(5)
    robot.DeactivateRobot()
    robot.Disconnect()
    
def moveCircle (): 
    robot.MovePose(223.100006,-37.849998,140.774994,0,90,0) #pickup waypoint
    robot.Delay(0.25)
    robot.MoveLin(180,-127,95,0,90,0) #top left
    robot.Delay(0.25)
    robot.MoveLin(180,56.5,95,0,90,0) #top right
    robot.Delay(0.25)
    robot.MoveLin(260,56.5,95,0,90,0) #bottom right
    robot.Delay(0.25)
    robot.MoveLin(260,-127,95,0,90,0) #bottom left
    robot.Delay(0.25)

def moveMeasure ():
    robot.MovePose(182.200012,171.25,140.774994,0,90,0) #keyence measure way point
    
def measureWires ():
    for i in range(4):
        robot.MoveLinRelTrf(0, 9.5, 0, 0, 0, 0)
        print(i)
        robot.Delay(3)
    
def pick ():
    robot.MoveLinRelTrf(10, 0, 0, 0, 0, 0)
    robot.Delay(1)
    robot.GripperClose()
    robot.MoveLinRelTrf(-50, 0, 0, 0, 0, 0)
    robot.Delay(2)
    robot.MovePose(223.100006,-37.849998,140.774994,0,90,0) #pickup waypoint
    
def drop ():
    robot.MoveLinRelTrf(10, 0, 0, 0, 0, 0)
    robot.Delay(1)
    robot.GripperOpen()
    robot.Delay(0.25)
    robot.MoveLinRelTrf(-50, 0, 0, 0, 0, 0)
    robot.MovePose(223.100006,-37.849998,140.774994,0,90,0) #pickup waypoint
    

    