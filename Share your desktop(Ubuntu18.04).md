
## Open the Screen Sharing function
Open the Screen Sharing function from Ubuntu:

https://help.ubuntu.com/stable/ubuntu-help/sharing-desktop.html.en

https://websiteforstudents.com/access-ubuntu-18-04-lts-beta-desktop-via-vnc-from-windows-machines/

You may get some errors when you try to connect your remote desktop. And there are some security policies from Ubuntu18.04 we need to change:

https://dev.idoseek.com/vncview-remote-desktop-to-ubuntu/

## Connect via Vnc Viewer from Your Own Computer
If your remote system has some security policies that you can not direct link your remote desktop by using 

IP: port(default we use 5900, you can use other ports if you like)

You may need to log in your remote system via ssh first using this command:

ssh -L 5900:127.0.0.1:5900 username@IP

Then go to vnc viewer connect the remote screen by typing: 

127.0.0.1:5900
