# Dynamic Positioning

The rov_gui.py file can be run in parallel to QGroundControl to control a BlueROV2 or similar underwater submersible utilising ArduSub and Water Linked's DVL-A50 or other means of positional feedback. To note this will only work when the ROV is near the seabed in theory (50m for DVL-A50)

Feel free to contact me at ben.bartlett@ul.ie 

Assuming all of the below is setup correctly the file can be run as
```
$ python rov_gui.py
```

![GUI image alt text](/gui_pics/GUI.png)

Heading can be set in absolute terms 0-360, or relative from current heading + or - (with added buttons that appear when relative radio button is selected)

Heave(Z), Sway(Y) and Surge(X) are relative and can be relative to body frame i.e ROV's orientation or NED frame i.e locked to North, South, East, West

QGroundControl does not fully support the flight mode. It appears as an Unknown mode and can only be changed into via the interface. (Unless you build QGroundControl from scratch to add the mode name)

The ROV can be armed and disarmed via the interface.

New Velocity mode being developed

## Setup

The following is aimed at Linux (Ubuntu 18.04 was used) no guarantee for Windows/Mac but should work with anaconda or similar for python setup 


## Update
### The simplest way to use this code is now as follows

1. Have a BlueROV2 with the WaterLinked DVL-A50 physically integrated as per [link](https://waterlinked.github.io/dvl/bluerov-integration/)
   * The assumption for now is that you are using the original pixhawk and raspberry pi companion system and not the new blueos and navigator.
   * Update to come for new hardware
   * I would recommend a firmware of no greater than 2.0.8 which can be downloaded by https://update.waterlinked.com/api/v1/download/CHIPID/SOFTWAREVERSION
   * ChipID can be found on the DVL web GUI, software version is 2.0.8. 2.2.1 does not work with this companion image
   
2. Remove the SD card from the Comapanion Raspberry Pi PC and etch it with the image file I have create [here]()
    * This was created with the command 
       ```
       $ sudo dd bs=4M if=/dev/mccblk0 of=/home/desired_directory/image_name.img
       ```
    * I would recommend you do this with your own version of Companion software as a backup before etching the sd card with my image
    * Etch the sd card with [link](https://www.balena.io/etcher/)
    
3. Flash the Pixhawk with the binary file found [here](https://github.com/Ben-Bartlett/ArduSub_Dynamic_Positioning/blob/main/binary/ardusub.apj) as per [link](https://www.ardusub.com/developers/developers.html#flashing-via-web-interface)

4. Recommended Parameters to setup in QGroundControl

    ```
    SERIAL0_PROTOCOL 2
    AHRS_EKF_TYPE 3
    EK2_ENABLE 0
    EK3_ENABLE 1
    VISO_TYPE 1
    EK3_GPS_TYPE 3 
    PSC_POSXY_P 2.5
    PSC_POSZ_P  1.0
    PSC_VELXY_D 0.8
    PSC_VELXY_I 0.5
    PSC_VELXY_P 5.0
    PSC_VELZ_P  5.0
    ```

5. Create the python environment to run the rov_gui.py file
    
  * Make sure python 2 and pip is installed on machine (python 2.7.17 was used)
     ```
     $ python --version
     $ pip --version
     ```
  * Install virtualenv (unless you are fine running python 2.7 as standard) skip to 5
     ```
     $ pip install virtualenv
     $ virtual env --version
     ```
     Version used was 20.4.0

   * Create Virtual Environment 
     ```
     $ virtualenv -p /usr/bin/python2.7 rov
     ```
     You can select any name for the environment instead of rov

   * Activate Environment 
     ```
     $ source rov/bin/activate
     ```
     I setup an alias for quickly setting up the environment when wanting to run the program
     Added to top of /.bashrc
 
        ```
        # setup virtualenv for rov
        alias dyna="cd ~; source rov/bin/activate; cd ~/Documents/rov"
        ```
    
   * Install Packages, made easy with requirements.txt file
     ```
     $ pip install -r requirements.txt
     ```




______
________
______










LEFT HERE IN CASE YOU WANT TO DO IT THE OLD WAY BUT THIS IS NOT RECOMMENDED


1. Standard BlueROV2 setup
   1. Having the appropriate hardware, (BlueROV2 and Water Linked DVL-A50). Other sensors may work
   2. Having QGroundControl running on PC and manual control established. [link](https://www.ardusub.com/reference/qgc-configuration.html) [link](https://bluerobotics.com/learn/bluerov2-software-setup/)
2. Additional ROV setup
   1. Installing Water Linked DVL-A50 drivers and have position hold mode working. [link](https://github.com/bluerobotics/companion/pull/355)
   3. **Flashing the ROV with the required binary.** 
   4. **Adding the extra communications port**
3. Additional PC setup
   1. **Having a python 2.7 environment setup on PC to run file**

___

### 2.2 Flashing ROV with Required Binary 

The binary can be found here [link](https://github.com/Ben-Bartlett/ArduSub_Dynamic_Positioning/blob/main/binary/ardusub.apj) or built from here [repo](https://github.com/Ben-Bartlett/ardupilot/tree/dvl_ben)

Binary can be flashed as follows [link](https://www.ardusub.com/developers/developers.html#flashing-via-web-interface)

### 2.3 Adding extra communication port

To add the extra port for the program to run in parallel to QGroundControl the steps are as follows:
* The new port for this program is 14777 (but can be changed if desired, but must be changed to match in the rov_gui.py file
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
   NOTE: Tested but wasn't found to work very well. Only packages needed are
    ```
    $ pip install pymavlink
    $ pip install numpy
    $ pip install pillow
    ```  
   
6. You can deactivate the environment as follows
    ```
    $ deactivate
    ```
___

DISCLAIMER: No guarantees or warranties with this project. Use at your own risk. If she crash, she crash.
