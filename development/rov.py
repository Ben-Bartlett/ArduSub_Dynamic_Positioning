# imports
from collections import OrderedDict
from pymavlink import mavutil
from pymavlink.quaternion import QuaternionBase #needs Numpy
import math
import time
import csv
from datetime import datetime
import os


# commands dictionary, Ordered Dict as only from python 3.6/3.7 is kwargs ordered
commands = OrderedDict([
    ("HELP","commands.iteritems()"), # python 2.7 uses iteritems(), 3+ uses items()
    ("ARM","arm_rov()"),
    ("DISARM","disarm_rov()"),
    ("TEST","test_motors()"),
    ("SET MODE", "change_mode()"),
    ("SET DEPTH","set_depth()"),
    ("SET YAW","set_yaw()"),
    ("SET XY","set_xy()"),
    ("READ POS","read_pos()"),
    ("READ DEPTH","read_depth()"),
    ("READ ALL","read_all()"),
    ("X","set_x()"),
    ("Y","set_y()"),
    ("Z","set_z()"),
])


# functions
# not sure each one requires heartbeat wait, testing appears it doesn't
def arm_rov():
    #master.wait_heartbeat()
    master.arducopter_arm()
    print('ROV ARMED')
    

def disarm_rov():
    #master.wait_heartbeat()
    master.arducopter_disarm()
    print('ROV DISARMED')

def test_motors():
    # runs only for one cycle as it needs to be sent at a constant rate like
    # the heartbeat to continually run
    #master.wait_heartbeat()
    print('TEST MOTORS')
    master.mav.manual_control_send(
    master.target_system,
    500,
    -500,
    250,
    500,
    0)
    
def change_mode():
    #master.wait_heartbeat()
    
    # modes from pymavlink/mavutil.py
    modes = master.mode_mapping()
    
    # ^ will not have DYNA_POS unless added manually. Was added to the ardupilot
    # modules pymavlink/mavutil.py before build and to the local pymavlink/mavutil.py in my virtualenv
    if 'DYNA_POS' not in modes:
        modes['DYNA_POS']=24
        
    print('MODES : {}'.format(modes.keys()))
    print ('CHOOSE MODE OR "CANCEL"')
    
    mode_valid = False
    while (mode_valid == False):
        # Choose a mode
        mode = raw_input("> ")
        
        if mode =='CANCEL':
            break
        
        # Check if valid
        if mode not in modes:
            print('UNKNOWN MODE, TRY : {}'.format(modes.keys()))
        else:
            mode_valid=True
            # Get id of mode 
            mode_id = modes.get(mode)
            # Send command to set mode
            master.mav.set_mode_send(
     master.target_system,
     mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
     mode_id)
        
def set_depth():
    # althold
    #master.set_mode('ALT_HOLD')
    #print('Mode depth hold must be active (activated)')
    #master.set_mode('DYNA_POS')
    #print('TESTING DYNA_POS MODE SET DEPTH')
    
    # arm
    #master.arducopter_arm()
    
    print('Set a depth')
    depth = float(raw_input('>'))
    
    if depth > 0:
        depth *= -1
    
    # MAV ID: 86
    master.mav.set_position_target_global_int_send(
        0,     
        0, 0,   
        mavutil.mavlink.MAV_FRAME_GLOBAL_INT, # frame
        0b0000111111111000, # mask to use only depth
        0,0, depth,
        0 , 0 , 0 , # x , y , z velocity in m/ s ( not used )
        0 , 0 , 0 , # x , y , z acceleration ( not supported yet , ignored in GCS Mavlink )
        0 , 0 ) # yaw , yawrate ( not supported yet , ignored in GCS Mavlink )

    
    
def set_yaw():
    
    roll = 0
    pitch = 0
    yaw = 0
    
    control_yaw = True
    
    print('SET YAW') # or EXIT')
    
    #valid_command = False
    
    #while (valid_command == False):
        
    #    command = raw_input("> ")
        
    #    if command == 'EXIT':
    #        return
    #    elif command == 'ROLL' or command == 'PITCH' or command == 'YAW'
    #        valid_command = True
    #    else:
    #        print('INVALID, EXIT or try again')
     
    #if command == 'ROLL':
    #    print('How much ROLL')
    #    roll = float(raw_input("> "))
    #elif command == 'PITCH':
    #    print('How much PITCH')
    #    pitch = float(raw_input("> "))
    #elif command == 'YAW':
    #    print('How much YAW')
    #    yaw = float(raw_input("> "))
    
    yaw = float(raw_input("> "))
    
    bitmask = (1<<6 | 1<<3)  if control_yaw else 1<<6

    master.mav.set_attitude_target_send(
        0,     
        0, 0,   
        bitmask,
        QuaternionBase([math.radians(roll), math.radians(pitch), math.radians(yaw)]), # -> attitude quaternion (w, x, y, z | zero-rotation is 1, 0, 0, 0)
        0, #roll rate
        0, #pitch rate
        0, 0)    # yaw rate, thrust 

    
def set_xy():
    
    X = 0 # + is north
    Y = 0 # + is east
    
    print("X, Y or EXIT")
    
    valid_command = False
    
    while (valid_command == False):
        
        command = raw_input("> ")
        
        if command == 'EXIT':
            return
        elif command == 'X' or command == 'Y':
            valid_command = True
        else:
            print('INVALID, EXIT or try again')
     
    if command == 'X':
        print('How much X')
        X = float(raw_input("> "))
    elif command == 'Y':
        print('How much Y')
        Y = float(raw_input("> "))
        
        
    master.mav.set_position_target_local_ned_send(
                0, # timestamp
                0, 0, # target system_id # target component id
                mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # offset to current position and heading
                0b110111111000, # mask specifying use-only-x-y-z
                X, Y, 0, # x y z 
                0, 0, 0, #vx vy vz
                0, 0, 0, # afx afy afz
                0, 0) # yaw # yawrate
             
def set_x():
    X = 0 # + is north
    print("How much X")
    X = float(raw_input("> "))
        
    master.mav.set_position_target_local_ned_send(
                0, # timestamp
                0, 0, # target system_id # target component id
                mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # offset to current position and heading
                0b110111111000, # mask specifying use-only-x-y-z
                X, 0, 0, # x y z 
                0, 0, 0, #vx vy vz
                0, 0, 0, # afx afy afz
                0, 0) # yaw # yawrate

def set_y():
    Y = 0 # + is north
    print("How much Y")
    Y = float(raw_input("> "))
        
    master.mav.set_position_target_local_ned_send(
                0, # timestamp
                0, 0, # target system_id # target component id
                mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # offset to current position and heading
                0b110111111000, # mask specifying use-only-x-y-z
                0, Y, 0, # x y z 
                0, 0, 0, #vx vy vz
                0, 0, 0, # afx afy afz
                0, 0) # yaw # yawrate
    
def set_z():
    Z = 0 # + is north
    print("How much Z")
    Z = float(raw_input("> "))
        
    master.mav.set_position_target_local_ned_send(
                0, # timestamp
                0, 0, # target system_id # target component id
                mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # offset to current position and heading
                0b110111111000, # mask specifying use-only-x-y-z
                0, 0, Z, # x y z 
                0, 0, 0, #vx vy vz
                0, 0, 0, # afx afy afz
                0, 0) # yaw # yawrate

def read_pos():
    
    #f = open('params.csv','w')
      
    def update():
    # Get all messages
        msgs = []
        while True:
            msg = master.recv_match()
            if msg == None:
                break
            msgs.append(msg)
 
        # Create dict
        data = {}
        for msg in msgs:
            data[msg.get_type()] = msg.to_dict()
        # Return dict
        return data
 
    try:
        while True:
            data = update()
            #if 'VFR_HUD' in data:
            #    row = 'Depth, Heading: ,'+ str(data['VFR_HUD']['alt']) + ', ' + str(data['VFR_HUD']['heading'])
                #row_n = row + '\n'
            #    print(row)
                #f.write(row_n)
            if 'LOCAL_POSITION_NED' in data:
                row_p = 'Position: x, y, z ,' + str(data['LOCAL_POSITION_NED']['x']) + ', ' + str(data['LOCAL_POSITION_NED']['y']) + ', ' + str(data['LOCAL_POSITION_NED']['z'])
                print(row_p)
          
    # CTRL + C TO STOP
    except KeyboardInterrupt:
        print("\nstopped")
        data = {}
        #f.close()

def update():
    # Get all messages
        msgs = []
        while True:
            msg = master.recv_match()
            if msg == None:
                break
            msgs.append(msg)
 
        # Create dict
        data = {}
        for msg in msgs:
            data[msg.get_type()] = msg.to_dict()
        # Return dict
        return data
    
def read_depth():
    
    # datetime object containing current date and time for file name
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
    
    # if folder doesn't exist create it , keeps all data in one folder rather than base folder
    if not os.path.exists('depth_data'):
        os.makedirs('depth_data')
            
    filename = 'depth_data/depth_' + dt_string + '.csv'
    f = open(filename,'w')
 
    try:
        while True:
            data = update()
            if 'VFR_HUD' in data:
                row = 'VFR_HUD Depth: ,' + str(data['VFR_HUD']['alt'])
                row_n = row + '\n'
                print(row)
                f.write(row_n)
          
    # CTRL + C TO STOP
    except KeyboardInterrupt:
        print(" stopped")
        data = {}
        f.close()


def read_all():
    try:
        while True:
            try:
                message = master.recv_match().to_dict()
                if 'VFR_HUD' in str(message):
                    print(message)
                    print('\n DIVIDER \n')
                else:
                    print(message)
            except:
                pass
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print(" stopped")

       

# Create the connection
# default port 14550
# new port for this program is 14777 (found number on forums, so assuming it is unused)
    # To add this port connect to PI on ROV
    # ssh pi@192.168.2.2 
    # password: companion
    # edit mavproxy.param file in home directory, can run sudo nano mavproxy.param
    # add --out udpbcast:192.168.2.1:14777 below 
    # ctrl + o to save, ctrl + x to exit
    # restart companion, sudo reboot
     
master = mavutil.mavlink_connection('udpin:0.0.0.0:14777')

master.wait_heartbeat()

#main loop to input commands
run = True

print('Turn on Cap locks, Type HELP for full list of commands')

while (run == True):
    # Had to use raw_input for python 2 as input fails
    command = raw_input(">>>>> ")
    
    #check if exit command is given
    if command == 'EXIT':
        run = False
    
    #check if command is valid
    if command in commands:
        #help case lists all command names
        if command == "HELP":
            execute_command = commands.get(command)
            print("Commands \n")
            print("EXIT")
            for key, value in (eval(execute_command)):
                if key != "HELP":
                    print(key)
            
        #run command
        else:
            execute_command = commands.get(command)
            eval(execute_command)
        
    else:
        #check so if exit command was given it doesn't also say invalid upon exiting
        if command!='EXIT':
            print("command invalid")


            
            
            

