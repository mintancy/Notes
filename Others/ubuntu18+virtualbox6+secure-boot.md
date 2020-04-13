## My computer can not install the new version, can only install the old version virtualbox-5.2

# SAD


# Install Steps

```shell
$sudo apt update
$sudo apt-get install gcc make linux-headers-$(uname -r) dkms

$wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -
$wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | sudo apt-key add -

$sudo sh -c 'echo "deb [arch=amd64] http://download.virtualbox.org/virtualbox/debian $(lsb_release -sc) contrib" >> /etc/apt/sources.list.d/virtualbox.list'

$sudo apt remove virtualbox virtualbox-5.2

$sudo apt update
$sudo apt-get install virtualbox-6.0
```
# Errors

You may meet problems if you use EFI or Secure boot configuration.
> There were problems setting up VirtualBox.  To re-start the set-up process, run
  /sbin/vboxconfig
as root.  If your system is using EFI Secure Boot you may need to sign the
kernel modules (vboxdrv, vboxnetflt, vboxnetadp, vboxpci) before you can load
them. Please see your Linux system's documentation for more information.

# Assign the virtualbox module

```shell
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install mokutil

openssl req -new -x509 -newkey rsa:2048 -keyout MOK.priv -outform DER -out MOK.der -nodes -days 36500 -subj "/CN=VirtualBox/"

sudo /usr/src/linux-headers-$(uname -r)/scripts/sign-file sha256 ./MOK.priv ./MOK.der $(modinfo -n vboxdrv)
```
Register it for the Secure Boot.

**IMPORTANT!** That will ask you for a password, put the one you want, you will only have to use it once in the next reboot.
```
sudo mokutil --import MOK.der
```

Finally, restart the computer. A blue screen will appear with a keyboard wait, press the key that asks you to interrupt the boot.

> Enroll MOK -> Continue -> and it will ask you for the password

# Reference

https://websiteforstudents.com/virtualbox-6-0-is-out-heres-how-to-install-upgrade-on-ubuntu-16-04-18-04-18-10/

https://thedaneshproject.com/posts/n-skipping-acquire-of-configured-file-contrib-binary-i386-packages-as-repository-https-download-virtualbox-org-virtualbox-debian-bionic-inrelease-doesnt-support-architecture-i386/

https://superuser.com/questions/1438279/how-to-sign-a-kernel-module-ubuntu-18-04