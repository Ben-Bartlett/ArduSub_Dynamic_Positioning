# imports
from collections import OrderedDict
from pymavlink import mavutil
from pymavlink.quaternion import QuaternionBase #needs Numpy
import math
import time
import csv
from datetime import datetime
import os
from tkinter import *
import tkinter.font as font
from PIL import Image,ImageTk
from threading import *

# Global
DYNA_POS = 24

######################################################################
# Functions, looked at moving these to separte file but then global 
# var issue with master needing to be an argument for each funtion 
# which is doable else moving the connection code to the functions file
######################################################################

# ARM, DISARM, CHECK FUNCTIONS
def is_armed():
    # check for whether or not ROV is armed before trying to arm/disarm
    # not strcitly neccesasry 
    try:
        return bool(master.wait_heartbeat().base_mode & 0b10000000)
    except:
        return False
    
def arm_rov():
 
        X = 0
        Y = 0
        reading_gotten = False
        while reading_gotten == False:
            data = update()
            #doubled up as there is some caching issue. 
            data = update()
            if 'VFR_HUD' in data:
                current_depth = data['VFR_HUD']['alt']
                current_heading = data['VFR_HUD']['heading']
                reading_gotten =  True
        
        master.mav.set_position_target_local_ned_send(
                0, # timestamp
                0, 0, # target system_id # target component id
                mavutil.mavlink.MAV_FRAME_LOCAL_OFFSET_NED, #MAV_FRAME_BODY_OFFSET_NED, # offset to current position and heading, MAV_FRAME_LOCAL_OFFSET_NED for testing recording as it only gives position in NED
                0b110111111000, # mask specifying use-only-x-y-z
                X, Y, float(current_depth), # x y z 
                0, 0, 0, #vx vy vz
                0, 0, 0, # afx afy afz
                0, 0) # yaw # yawrate
        
        # set attitude to current attitude too
        roll = 0
        pitch = 0
        master.mav.set_attitude_target_send(
        0,     
        0, 0,   
        (1<<6 | 1<<3),
        QuaternionBase([math.radians(roll), math.radians(pitch), math.radians(current_heading)]), # -> attitude quaternion (w, x, y, z | zero-rotation is 1, 0, 0, 0)
        0, #roll rate
        0, #pitch rate
        0, 0)    # yaw rate, thrust 
        
        # cannot arm while logging data given the heartbeat wait
        master.arducopter_arm()


def disarm_rov():
    #while is_armed():
    master.arducopter_disarm()

# MODE, MODE CHECK FUNCTIONS        
def mode_is(mode):
    try:
        master.wait_heartbeat() # needed else mode returned is recalled as 24 still even after changing in QGC
        return bool(master.wait_heartbeat().custom_mode == mode)
    except:
        return False

def change_mode_dyna():
        # Send command to set mode
	#master.mav.command_long_send(
	 #master.target_system, master.target_component,
	 #mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
 	 #0, 24, 0, 0, 0, 0, 0)
	master.mav.set_mode_send(
         master.target_system,
         mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
         DYNA_POS)
        
# YAW / HEADING    
def set_yaw(direction=1):
    # direction -1 or +1 left or right
    
    set_yaw.heading = 0
    
    roll = 0
    pitch = 0

    if heading_ref_var.get()=="ABSOLUTE":
	# catch letters etc
        try:
            yaw = abs(float(txt_set_heading.get()))
            set_yaw.heading = yaw
        except:
            return

    elif heading_ref_var.get()=="RELATIVE":
        try:
            offset_yaw = abs(float(txt_set_heading.get()))
        except:
            return

	# check for heading greater than single revolution just set to 0
	if abs(float(offset_yaw)) > 360:
	    offsetyaw=0
	# get current heading
        reading_gotten = False
        while reading_gotten == False:
            data = update()
            #doubled up as there is some caching issue. 
            data = update()
            if 'VFR_HUD' in data:
                current_yaw = data['VFR_HUD']['heading']
                reading_gotten =  True        
	yaw = current_yaw + (direction)*offset_yaw
	if yaw > 359:
	    yaw-=360
	if yaw < 0:
	    yaw+=360
        set_yaw.heading = yaw
    else:
        return

    control_yaw = True
    
    
    
    bitmask = (1<<6 | 1<<3)  if control_yaw else 1<<6

    master.mav.set_attitude_target_send(
        0,     
        0, 0,   
        bitmask,
        QuaternionBase([math.radians(roll), math.radians(pitch), math.radians(yaw)]), # -> attitude quaternion (w, x, y, z | zero-rotation is 1, 0, 0, 0)
        0, #roll rate
        0, #pitch rate
        0, 0)    # yaw rate, thrust 

def read_heading():
    
    # datetime object containing current date and time for file name
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    
    # if folder doesn't exist create it , keeps all data in one folder rather than base folder
    if not os.path.exists('heading_data'):
        os.makedirs('heading_data')
        print('Directory "heading_data" created')
            
    filename = 'heading_data/heading_' + dt_string + '.csv'
    f = open(filename,'w')
    print('File created %s' % filename)
    
    latch = False
    # function paramter used to loop   
    while start_stop_read_heading.Record == True:
        data = update()
        try:
            if start_stop_read_heading.stopped == True and latch == False:
                # if record was stopped update again to make sure old value is skipped
                data = update()
                skip_row_1 = True
                # to only run this once and prevent data rate being halfed
                latch = True
        except:
            # else if it is the first run of record, recording the first row is ok
            skip_row_1 = True
        
        if skip_row_1 == True:
            if 'VFR_HUD' in data:
                current_heading_reading = 'VFR_HUD Heading: ,' + str(data['VFR_HUD']['heading']) 
                try:
                    # has a depth target been set, if so print it, take depth value from time the ROV was commanded
                    # eg at -10,-10, recording, set depth goto -20, records -10, -20, but increments -11, -21 ..etc
                    current_set_heading = ', Heading Commanded: ,' + str(set_yaw.heading)
                except:
                    # if not, just use the current depth for no commanded depth so far
                    current_set_heading = ', Heading Commanded: ,' + str(data['VFR_HUD']['heading'])
                
                heading_data = current_heading_reading + current_set_heading
                row = heading_data + '\n'
                print(heading_data)
                f.write(row)
                   
    print("stopped")
    data = {}
    f.close()
    
def start_stop_read_heading(start_stop):  
    init = 0
    start = 1
    stop = 0
     
    start_stop_read_heading.Record = False
    if start_stop == start:
        start_stop_read_heading.Record = True
        # separte thread for reading data
        thread_read_heading = Thread(target=read_heading) 
        thread_read_heading.daemon = True
        thread_read_heading.start()
    elif start_stop == stop:
        start_stop_read_heading.Record = False
        # added function property as first row of subsequent runs of reading data prints the last value
        # e.g read depth start at depth -10, stop read. move to -20. read depth prints -10 first row then -20
        # resetting data to {} doesn't solve
        start_stop_read_heading.stopped = True
    else:
        return    
    
    
    
# SURGE / SWAY     
def set_xy(x_y, forward_back_left_right):
    # function parameter for printing, probably should be using classes
    set_xy.X = 0
    set_xy.Y = 0
    # x or y commanded
    set_xy.X_Y = str(x_y)
    
    # local NED reference
    forward = 1
    right = 1
    back = -1 
    left = -1
    X=0
    Y=0
    
    # get a current reading
    reading_gotten = False
    while reading_gotten == False:
            data = update()
            #doubled up as there is some caching issue. 
            data = update()
            # fixed NED orientation not body relative
            if 'LOCAL_POSITION_NED' in data:
                # was updating y go to values(which are pseudo for graphing only) on x commands and viceversa
                if x_y == 'x':
                    set_xy.current_x = data['LOCAL_POSITION_NED']['x']
                elif x_y == 'y':
                    set_xy.current_y = data['LOCAL_POSITION_NED']['y']
                reading_gotten =  True
    # sanity check on else as same function call for forward/back/left/right
    if x_y == 'x':
        if forward_back_left_right == forward or forward_back_left_right == back:
            # catch letters etc
            try:
                X = abs(float(txt_set_xy.get())) * forward_back_left_right
                set_xy.X = X
            except:
                return
    elif x_y == 'y':
        if forward_back_left_right == left or forward_back_left_right == right:
            try:
                Y = abs(float(txt_set_xy.get())) * forward_back_left_right
                set_xy.Y = Y
            except:
                return
    else:
        return

    # using if else as a variable can't be used to take MAV_FRAME_LOCAL_OFFSET_NED for xy_frame.get() within set_position_target_local_ned_send
    if xy_frame.get() == "body":
        master.mav.set_position_target_local_ned_send(
                0, # timestamp
                0, 0, # target system_id # target component id
                mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, #MAV_FRAME_BODY_OFFSET_NED, # offset to current position and heading, MAV_FRAME_LOCAL_OFFSET_NED for testing recording as it only gives position in NED
                0b110111111000, # mask specifying use-only-x-y-z
                X, Y, 0, # x y z 
                0, 0, 0, #vx vy vz
                0, 0, 0, # afx afy afz
                0, 0) # yaw # yawrate

    elif xy_frame.get() == "NED":
        master.mav.set_position_target_local_ned_send(
                0, # timestamp
                0, 0, # target system_id # target component id
                mavutil.mavlink.MAV_FRAME_LOCAL_OFFSET_NED, #MAV_FRAME_BODY_OFFSET_NED, # offset to current position and heading, MAV_FRAME_LOCAL_OFFSET_NED for testing recording as it only gives position in NED
                0b110111111000, # mask specifying use-only-x-y-z
                X, Y, 0, # x y z 
                0, 0, 0, #vx vy vz
                0, 0, 0, # afx afy afz
                0, 0) # yaw # yawrate
    
    else:
        return

def read_xy():
    
    # datetime object containing current date and time for file name
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    
    # if folder doesn't exist create it , keeps all data in one folder rather than base folder
    if not os.path.exists('xy_data'):
        os.makedirs('xy_data')
        print('Directory "xy_data" created')
            
    filename = 'xy_data/xy_' + dt_string + '.csv'
    f = open(filename,'w')
    print('File created %s' % filename)
    
    latch = False
    # function paramter used to loop   
    while start_stop_read_xy.Record == True:
        data = update()
        try:
            if start_stop_read_xy.stopped == True and latch == False:
                # if record was stopped update again to make sure old value is skipped
                data = update()
                skip_row_1 = True
                # to only run this once and prevent data rate being halfed
                latch = True
        except:
            # else if it is the first run of record, recording the first row is ok
            skip_row_1 = True
        
        if skip_row_1 == True:
            if 'LOCAL_POSITION_NED' in data:
                # Taken from home position, which resets on arm/disarm sequence
                current_x_reading = str(data['LOCAL_POSITION_NED']['x'])
                current_y_reading = str(data['LOCAL_POSITION_NED']['y'])
                current_xy_reading = 'LOCAL_POSITION_NED X Y: ,' + current_x_reading + ',' + current_y_reading
                
                try:
                    # if command is an x command set the Commanded value (which is relative to current position not absolute) shouldn't be an issue for Z recording as it is just Z so one block works fine
                    if set_xy.X_Y == 'x':
                        current_set_x = ', X Commanded: ,' + str(set_xy.current_x + set_xy.X)
    
                except:
                    # no command run yet so can't print a commanded value
                    current_set_x = ', X Commanded: ,' + current_x_reading
                try:
                    if set_xy.X_Y == 'y':
                        current_set_y = ', Y Commanded: ,' + str(set_xy.current_y + set_xy.Y)
                except:
                    current_set_y = ', Y Commanded: ,' + current_y_reading
                    
                #could do Z the same but absolute depth is better in this case as there is no absolute x/y without GPS
                # try block for subsequent plotting calls as it may(more likely will have a call run already) so there wont be a current_set_x/y evaluated
                try:
                    xy_data = current_xy_reading + current_set_x + current_set_y
                except:
                    # will run once taking the last value reading
                    if set_xy.X_Y == 'y':
                        exception_current_set_x = ', X Commanded: ,' + current_x_reading
                        xy_data = current_xy_reading + exception_current_set_x + current_set_y
                    if set_xy.X_Y == 'x':
                        exception_current_set_y = ', Y Commanded: ,' + current_y_reading
                        xy_data = current_xy_reading + current_set_x + exception_current_set_y
                        
                row = xy_data + '\n'
                print(xy_data)
                f.write(row)
                   
    print("stopped")
    data = {}
    f.close()
 
        
                
def start_stop_read_xy(start_stop):  
    init = 0
    start = 1
    stop = 0
     
    start_stop_read_xy.Record = False
    if start_stop == start:
        start_stop_read_xy.Record = True
        # separte thread for reading data
        thread_read_xy = Thread(target=read_xy) 
        thread_read_xy.daemon = True
        thread_read_xy.start()
    elif start_stop == stop:
        start_stop_read_xy.Record = False
        # added function property as first row of subsequent runs of reading data prints the last value
        # e.g read depth start at depth -10, stop read. move to -20. read depth prints -10 first row then -20
        # resetting data to {} doesn't solve
        start_stop_read_xy.stopped = True
    else:
        return

    
# HEAVE / DEPTH 
def set_depth(up_down):
    # function parameter for printing, probably should be using classes
    set_depth.Z = 0
    # local NED reference, + goes down and - goes up
    up = -1 
    down = 1
    # sanity check as same function call for up/down
    if (up_down != up) & (up_down != down):
        return
    # get a current reading
    reading_gotten = False
    while reading_gotten == False:
            data = update()
            #doubled up as there is some caching issue. 
            data = update()
            if 'VFR_HUD' in data:
                set_depth.current_depth = data['VFR_HUD']['alt']
                reading_gotten =  True


    # catch letters etc
    try:
        Z = up_down * abs(float(txt_set_depth.get()))
        set_depth.Z = Z
    except:
        return
    
    # read current depth and see if ROV will try to fly, i.e depth >0 (not sure if this is checked in the autopilot)
    master.mav.set_position_target_local_ned_send(
                0, # timestamp
                0, 0, # target system_id # target component id
                mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # offset to current position and heading, down is always down
                0b110111111000, # mask specifying use-only-x-y-z
                0, 0, Z, # x y z 
                0, 0, 0, #vx vy vz
                0, 0, 0, # afx afy afz
                0, 0) # yaw # yawrate

# update function used by read data functions    
def update():
    # Get all messages
    msgs = []
    while True:
        # keeps throwing internal errors on recv_match on data lengths etc so just a continue in the case of any error on recv.match
        try:
            msg = master.recv_match()
            if msg == None:
                break
            msgs.append(msg)
        except:
            continue
 
    # Create dict
    data = {}
    for msg in msgs:
        data[msg.get_type()] = msg.to_dict()
    # Return dict
    return data    
    
def read_depth():
    
    # datetime object containing current date and time for file name
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    
    # if folder doesn't exist create it , keeps all data in one folder rather than base folder
    if not os.path.exists('depth_data'):
        os.makedirs('depth_data')
        print('Directory "depth_data" created')
            
    filename = 'depth_data/depth_' + dt_string + '.csv'
    f = open(filename,'w')
    print('File created %s' % filename)
    
    latch = False
    # function paramter used to loop   
    while start_stop_read_depth.Record == True:
        data = update()
        try:
            if start_stop_read_depth.stopped == True and latch == False:
                # if record was stopped update again to make sure old value is skipped
                data = update()
                skip_row_1 = True
                # to only run this once and prevent data rate being halfed
                latch = True
        except:
            # else if it is the first run of record, recording the first row is ok
            skip_row_1 = True
        
        if skip_row_1 == True:
            if 'VFR_HUD' in data:
                current_depth_reading = 'VFR_HUD Depth: ,' + str(data['VFR_HUD']['alt']) 
                try:
                    # has a depth target been set, if so print it, take depth value from time the ROV was commanded
                    # eg at -10,-10, recording, set depth goto -20, records -10, -20, but increments -11, -21 ..etc
                    current_set_depth = ', Z Commanded: ,' + str(set_depth.current_depth - set_depth.Z)
                except:
                    # if not, just use the current depth for no commanded depth so far
                    current_set_depth = ', Z Commanded: ,' + str(data['VFR_HUD']['alt'])
                
                depth_data = current_depth_reading + current_set_depth
                row = depth_data + '\n'
                print(depth_data)
                f.write(row)
                   
    print("stopped")
    data = {}
    f.close()
 
        
                
def start_stop_read_depth(start_stop):  
    init = 0
    start = 1
    stop = 0
     
    start_stop_read_depth.Record = False
    if start_stop == start:
        start_stop_read_depth.Record = True
        # separte thread for reading data
        thread_read_depth = Thread(target=read_depth) 
        thread_read_depth.daemon = True
        thread_read_depth.start()
    elif start_stop == stop:
        start_stop_read_depth.Record = False
        # added function property as first row of subsequent runs of reading data prints the last value
        # e.g read depth start at depth -10, stop read. move to -20. read depth prints -10 first row then -20
        # resetting data to {} doesn't solve
        start_stop_read_depth.stopped = True
    else:
        return


def test_routine():
    # 1 m movements, manually start recording data then run test routine
    # used by set_xy function so setting entry value to allow code to be reused
    
    # doesnt work while recording due to wait heartbeat
    #armed = is_armed()
    #if armed != True:
    #    return
    time_sleep = 5
    test_x = txt_test_x.get()
    test_y = txt_test_y.get()
    if test_x == 'Y':
        txt_set_xy.delete(0,END)
        txt_set_xy.insert(0,'0.5')
    
        forward_back_left_right = -1
        # 4 iterations of x commands
        for i in range(4):
            forward_back_left_right *= -1 # loop one, 1 m NORTH, loop 2 -1, 1m SOUTH
            set_xy('x', forward_back_left_right)
            #x second delay but hangs display as there isn't a separte thread, still can exit with ctrl + c command line and disarm in QGC in the event of issue while running routine
            time.sleep(time_sleep)

    if test_y == 'Y':
        txt_set_xy.delete(0,END)
        txt_set_xy.insert(0,'0.5')
  	forward_back_left_right = -1
        # 4 iterations of x commands
        for j in range(4):
            forward_back_left_right *= -1 # loop one, 1 m EAST, loop 2 -1, 1m WEST
            set_xy('y', forward_back_left_right)
            time.sleep(time_sleep)
    
    test_depth = txt_test_z.get()
    
    if test_depth == 'Y':
        txt_set_depth.delete(0,END)
        txt_set_depth.insert(0,'0.5')
        up_down = -1;
        
        for k in range(4):
            up_down *= -1 # loop one, 1 m DOWN, loop 2 -1, 1m UP
            set_depth(up_down)
            time.sleep(time_sleep)
    
    test_heading = txt_test_heading.get()
    
    if test_heading == 'Y':
        # was going 315 to 45 but the graphs are not nice jumping through 0 to 360
        degree = 90
        gain = -1
        for k in range(4):
            gain *= -1
            degree = degree - (45 * gain) #back and forth between 45 and 90
            txt_set_heading.delete(0,END)
            txt_set_heading.insert(0,str(degree))
            set_yaw()
            time.sleep(time_sleep)
       
######################################################################
# Function but for GUI
######################################################################   
    
def change_buttons(show_hide):
    if show_hide == "hide":
        button_set_heading_left.grid_remove()
        button_set_heading_right.grid_remove()
    elif show_hide == "show":
	button_set_heading_left.grid(column=2, row=0)
	button_set_heading_right.grid(column=3, row=0)

def change_text(body_NED):
    if body_NED == "body":
        label_x_frame['text'] = "Forward"
        label_y_frame['text'] = "Left"
    elif body_NED == "NED":
	label_x_frame['text'] = "North"
        label_y_frame['text'] = "West"
    
######################################################################
# Setup Connection and GUI 
######################################################################
# Create the connection
# default port 14550
# new port for this program is 14777 
    # To add this port connect to PI on ROV
    # ssh pi@192.168.2.2 
    # password: companion
    # edit mavproxy.param file in home directory, can run sudo nano mavproxy.param
    # add --out udpbcast:192.168.2.1:14777 below 
    # ctrl + o to save, ctrl + x to exit
    # restart companion, sudo reboot

# CONNECT
master = mavutil.mavlink_connection('udpin:0.0.0.0:14777')
# WAIT FOR HEARTBEAT BEFORE SENDING ANY COMMANDS
master.wait_heartbeat()
# CHANGE TO FLIGHT MODE DYNAMIC POSITIONING 
change_mode_dyna()

# DEFINING GUI
# Main Window
window = Tk()
window.title("Dynamic Positioning")
window.geometry('760x480')

# Managing colomn row sizes
window.rowconfigure(3, {'minsize': 60}) #spacer for XY control area
window.rowconfigure(12, {'minsize': 10}) #spacer for x back arrow
window.rowconfigure(0, {'minsize': 80}) #adds a space around items in row so theyre not on top of each other
window.columnconfigure(0, {'minsize': 60})# ''
window.columnconfigure(1, {'minsize': 100})# ''
window.columnconfigure(2, {'minsize': 160})# ''
window.columnconfigure(4, {'minsize': 15})# ''



# ARM/DISARM
frame_arm_disarm = Frame(window) # to hold both buttons in same column of window
frame_arm_disarm.grid(column=6, row=0)
button_arm = Button(frame_arm_disarm, text="ARM", command=arm_rov)
button_arm.pack(side=LEFT, padx=2)

button_disarm = Button(frame_arm_disarm, text="DISARM", command=disarm_rov) 
button_disarm.pack(side=RIGHT)


# CHANGE MODE
button_change_mode_to_dyna = Button(window, text="CHANGE TO\nDYNAMIC POSITIONING\nFLIGHT MODE", command=change_mode_dyna) 
button_change_mode_to_dyna['font'] = font.Font(size=8)
button_change_mode_to_dyna.grid(column=6, row=1)


# HEADING/YAW
frame_yaw_toggle = Frame(window) 
frame_yaw_toggle.grid(column=0, row=0)
 
image_heading = Image.open("gui_pics/heading.png")
image_heading = image_heading.resize((50,50),Image.ANTIALIAS) 
photoImg_heading = ImageTk.PhotoImage(image_heading)

label_heading = Label(frame_yaw_toggle, text="HEADING")
label_heading['font'] = font.Font(size=15)
label_heading.pack(side=TOP, pady = (15,0))

txt_set_heading = Entry(window,width=10)
txt_set_heading.grid(column=1, row=0)

button_set_heading = Button(window, text="SET", command=set_yaw, image=photoImg_heading, compound=LEFT) 
button_set_heading.grid(column=2, row=0)

# Relative YAW

image_heading_left = Image.open("gui_pics/rel_heading_left.png")
image_heading_left = image_heading_left.resize((50,50),Image.ANTIALIAS) 
photoImg_heading_left = ImageTk.PhotoImage(image_heading_left)

image_heading_right = Image.open("gui_pics/rel_heading_right.png")
image_heading_right = image_heading_right.resize((50,50),Image.ANTIALIAS) 
photoImg_heading_right = ImageTk.PhotoImage(image_heading_right)

button_set_heading_left = Button(window, text="SET", command=lambda: set_yaw(-1), image=photoImg_heading_left, compound=LEFT) 
#commented out as they are shown on starting program bt shouldn't until relative raiod button is picked
#button_set_heading_left.grid(column=2, row=0)

button_set_heading_right = Button(window, text="SET", command=lambda: set_yaw(1), image=photoImg_heading_right, compound=LEFT) 
#button_set_heading_right.grid(column=3, row=0)

# Depth/Heave
image_depth_down = Image.open("gui_pics/down.png")
image_depth_down = image_depth_down.resize((50,50),Image.ANTIALIAS) 
photoImg_depth_down = ImageTk.PhotoImage(image_depth_down)

image_depth_up = Image.open("gui_pics/up.png")
image_depth_up = image_depth_up.resize((50,50),Image.ANTIALIAS) 
photoImg_depth_up = ImageTk.PhotoImage(image_depth_up)

label_depth = Label(window, text="HEAVE")
label_depth['font'] = font.Font(size=15)
label_depth.grid(column=0, row=1)

txt_set_depth = Entry(window,width=10)
txt_set_depth.grid(column=1, row=1)

button_set_depth_down = Button(window, text="SET", command=lambda: set_depth(1), image=photoImg_depth_down, compound=LEFT) 
button_set_depth_down.grid(column=2, row=1)

button_set_depth_up = Button(window, text="SET", command=lambda: set_depth(-1), image=photoImg_depth_up, compound=LEFT) 
button_set_depth_up.grid(column=3, row=1)

# X, Foward/Back /Surge
# Y, Left/Right /Sway
image_x_forward = Image.open("gui_pics/up.png")
image_x_forward = image_x_forward.resize((50,50),Image.ANTIALIAS) 
photoImg_x_forward = ImageTk.PhotoImage(image_x_forward)

image_x_back = Image.open("gui_pics/down.png")
image_x_back = image_x_back.resize((50,50),Image.ANTIALIAS) 
photoImg_x_back = ImageTk.PhotoImage(image_x_back)

image_y_left = Image.open("gui_pics/left.png")
image_y_left = image_y_left.resize((50,50),Image.ANTIALIAS) 
photoImg_y_left = ImageTk.PhotoImage(image_y_left)

image_y_right = Image.open("gui_pics/right.png")
image_y_right = image_y_right.resize((50,50),Image.ANTIALIAS) 
photoImg_y_right = ImageTk.PhotoImage(image_y_right)

frame_distance = Frame(window) # to hold both txt box and txt in same row of window
frame_distance.grid(column=2, row=11)

label_distance = Label(frame_distance, text="DISTANCE (m)")
label_distance.pack(side=TOP)

txt_set_xy = Entry(frame_distance,width=10)
txt_set_xy.pack(side=BOTTOM, pady=5)

button_set_x_forward = Button(window, text="SET", command=lambda: set_xy('x',1), image=photoImg_x_forward, compound=LEFT) 
button_set_x_forward.grid(column=2, row=9, pady=10)

button_set_x_back = Button(window, text="SET", command=lambda: set_xy('x',-1), image=photoImg_x_back, compound=LEFT) 
button_set_x_back.grid(column=2, row=12, pady=10)

button_set_y_left = Button(window, text="SET", command=lambda: set_xy('y',-1), image=photoImg_y_left, compound=LEFT) 
button_set_y_left.grid(column=1, row=11)

button_set_y_right = Button(window, text="SET", command=lambda: set_xy('y',1), image=photoImg_y_right, compound=LEFT) 
button_set_y_right.grid(column=3, row=11)

frame_x = Frame(window) 
frame_x.grid(column=2, row=8, padx=15)

label_x = Label(frame_x, text="SURGE")
label_x['font'] = font.Font(size=15)
label_x.pack(side=LEFT)
label_x_frame = Label(frame_x, text="forward")
label_x_frame['font'] = font.Font(size=8)
label_x_frame.pack(side=RIGHT)


frame_y = Frame(window) 
frame_y.grid(column=0, row=11, padx=(40,0))

label_y = Label(frame_y, text="SWAY")
label_y['font'] = font.Font(size=15)
label_y.pack(side=TOP)
label_y_frame = Label(frame_y, text="left")
label_y_frame['font'] = font.Font(size=8)
label_y_frame.pack(side=BOTTOM)

# heading absolute or relative
heading_ref_var = StringVar()
heading_ref_var.set("ABSOLUTE")
Radio_Button_heading_abs = Radiobutton(frame_yaw_toggle, text="ABSOLUTE", value="ABSOLUTE", variable=heading_ref_var, command=lambda: change_buttons("hide")).pack(side=LEFT)
Radio_Button_heading_rel = Radiobutton(frame_yaw_toggle, text="RELATIVE", value="RELATIVE", variable=heading_ref_var, command=lambda: change_buttons("show")).pack(side=RIGHT)

# surge/sway body or NED frame reference
frame_frame_toggle = Frame(window) 
frame_frame_toggle.grid(column=6, row=12)

xy_frame = StringVar()
xy_frame.set("body")
Radio_Button_frame_body = Radiobutton(frame_frame_toggle, text="Body Frame", value="body", variable=xy_frame, command=lambda: change_text("body")).pack(side=TOP)
Radio_Button_heading_rel = Radiobutton(frame_frame_toggle, text="NED Frame", value="NED", variable=xy_frame, command=lambda: change_text("NED")).pack(side=BOTTOM)
window.mainloop()
            
