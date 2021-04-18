# Dynamic Positioning

The rov_gui.py file can be run in parralel to QGroundControl to control a BlueROV2 or similar underwater submersible utilising ArduSub and WaterLinked's DVL-A50 or other means of positonal feedback. To note this will only work when the ROV is near the seabed (50m for DVL-A50)

Assuming all of the below is setup correctly the file can be run as
    $ python rov_gui.py

![GUI image alt text](/gui_pics/GUI.png)

Heading can be set in absolute terms 0-360, or relative from current heading + or - with added buttons

Heave(Z), Sway(Y) and Surge(X) are relative and can be relative to body frame i.e ROVs oreintation or NED frame i.e locked to North, South, East, West

QGroundControl does not fully support the flight mode. It appears as an Unknown mode and can only be changed into via the interface.

The ROV can be armed and disarmed via the interaface.

The development interaface also has recording functions and a test routine

## Setup

The following is aimed at Linux (Ubuntu 18.04.4 was used) no guarantee for Windows/Mac but potetnially anaconda or similar for python setup

Setup involves a few steps (project specific in bold):

1. Standard BlueROV2 setup
   1. Having the appropriate hardware, (BlueROV2 and WaterLinked DVL-A50). Other sensors may work
   2. Having QGroundControl running on PC and manual control established. link
2. Additional ROV setup
   1. Installing WaterLinked DVL-A50 drivers and have position hold mode working. link 
   2. **Flashing the ROV with the required binary.** link link
   3. **Adding the extra communications port**
3. Additional PC setup
   1. **Having a python 2.7 environment setup on PC to run file**

___

### 2.2 Flashing ROV with Required Binary 

The binary can be found here link or built from here link

Binary can be flashed as follows link

### 2.3 Adding extra communication port

To add the extra port for the program to run in parrallel to QGroundControl the steps are as follows:
* The new port for this program is 14777 (but can be changesd if desired, but must be changed to match in the rov_gui.py file
* To add this port connect to PI on ROV possible via 
    ```
    $ ssh pi@192.168.2.2 
    ```
* Password: **companion**
* Edit mavproxy.param file in home directory, can run 
    ```
    $ sudo nano mavproxy.param
    ```
* Add the following below the other port 14550
    ```
    $ --out udpbcast:192.168.2.1:14777
    ```
* ctrl + o to save, ctrl + x to exit
* restart companion, 
    ```
    $ sudo reboot
    ```
    
### 3.1 Virtual Environment Setup

1. Make sure python 2 and pip is installed on machine (python 2.7.17 was used)
    ```
    $ python --version
    $ pip --version
    ```
2. Install virtualenv (unless you are fine running python 2.7 as standard) skip to 5
    ```
    $ pip install virtualenv
    $ virtual env --version
    ```
 Version used was 20.4.0

3. Create Virtual Environment 
    ```
    $ virtualenv -p /usr/bin/python2.7 rov
    ```
 You can select any name for the environment instead of rov

4. Activate Environment 
    ```
    $ source rov/bin/activate
    ```
 I setup an alias for quickly setting up the environment when wanting to run the program
 
 Added to top of /.bashrc
    ```
    # setup virtualenv for rov
    alias dyna="cd ~; source rov/bin/activate; cd ~/Documents/rov"
    ```
5. Install Packages, made easy with requirements.txt file
    ```
    $ pip install -r requirements.txt
    ```
    
6. You can deactivate the environment as follows
    ```
    $ deactivate
    ```
___

DISCLAIMER: No guarantees or warranties with this project. Use at your own risk. If she crash, she crash.
