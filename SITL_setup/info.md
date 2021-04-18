# SITL useage of GUI

Once you have SITL working as per [link](https://ardupilot.org/dev/docs/SITL-setup-landingpage.html)

Having cloned this [repo](https://github.com/Ben-Bartlett/ardupilot/tree/dvl_ben).

You can simulate the ROV, [link](https://www.ardusub.com/developers/sitl.html) and run this program with the following 
```
$ cd ardupilot/ArduSub
$ sim_vehicle.py -L RATBeach --out=udp:0.0.0.0:14550 --out=udp:0.0.0.0:14777 --map --console
```
