
## No USB devices available in VirtualBox

Make sure you have installed the extension for the virtualbox.
```shell
$ sudo usermod -aG vboxusers user_name
$ sudo gpasswd -a user_name vboxusers
```
logout then login again (**IMPORTANT**).

## Install driver for XSDK

```shell
$ cd /opt/Xilinx/SDK/2017.4/data/xicom/cable_drivers/lin64/install_script/install_drivers
$ sudo ./install_drivers
```