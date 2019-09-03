## Introduction
I just found that there is no need to install vnc server for some remote uses. So this is the screen sharing function that ubuntu18.04 already set for us. 

Easy to start.

## Step1: Open the Screen Sharing function
Open the Screen Sharing function from Ubuntu:

https://help.ubuntu.com/stable/ubuntu-help/sharing-desktop.html.en

https://websiteforstudents.com/access-ubuntu-18-04-lts-beta-desktop-via-vnc-from-windows-machines/

You may get some errors when you try to connect your remote desktop. And there are some security policies from Ubuntu18.04 we need to change:

https://dev.idoseek.com/vncview-remote-desktop-to-ubuntu/

## Step2: Connect via Vnc Viewer from Your Own Computer
If your remote system has some security policies that you can not direct access your remote desktop by using 
```
IP: port(default we use 5900, you can use other ports if you like)
```
You may need to log in your remote system via ssh first using this command:
```
ssh -L 5900:127.0.0.1:5900 username@IP
```
This maps the ports of your remote computer to the local and performs vnc access in a safer way. I guess.

Then go to vnc viewer connect the remote screen by typing: 
```
127.0.0.1:5900
```