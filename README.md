# minimalistic_sailing_drone
Files for a minimalistic robotic sailingboat

Concept is:
- to have a simple 3d printed hull
- 1 sail with actuator (reel with sheet)
- 1 actuated rudder
- wifi + ros2 compatible controller
- Probably powered by replacable batteries (e.g. some 9v, or AA) with some power regulation hardware

With optionally:
- Heading/ inertial measurement units (on mast?)
- Wind direction sensing




![image](https://github.com/RAS-Delft/minimalistic_sailing_drone/assets/5917472/4a7ec0de-a389-489c-baab-60544179be82)

![image](https://github.com/RAS-Delft/minimalistic_sailing_drone/assets/5917472/f523755f-b242-4b97-8b70-36a9a4a7db1a)

![image](https://github.com/RAS-Delft/minimalistic_sailing_drone/assets/5917472/93dcb994-41c7-44ea-9bcd-937ab0346aa9)

![image](https://github.com/RAS-Delft/minimalistic_sailing_drone/assets/5917472/3a437bd4-fc68-4519-ab79-1486947a6fba)




## Control system setup
- Raspberry pi 3 with ubuntu 24 server
- Connect to wifi. Enable SSH
- (optionally) Disable USB and HDMI for power saving
- Install ROS2 Jammy
- Install RPI GPIO libraries
```shell
sudo apt-get install python3-rpi.gpio
```

