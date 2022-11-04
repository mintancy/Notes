level1: NH2SXQwcBdpmTEzi3bvBHMM9H66vVXjL
level2: rRGizSaX8Mk1RTb1CNQoXTcYZWU6lgzi
level3: aBZ0W5EmUfAf7kHTQeOwd8bauFJ2lAiG
level4: 2EW7BBsr6aMMoJ2HjW067dm8EgX26xNe
level5: lrIWWI6bB37kxfiCQZqUdOIYfr6eEeqR
level6: P4L4vucdmLnm8I7Vl7jG1ApGSfjYKqJU

level6 - level7
```shell
level7: find / -size 33c -group bandit6 -user bandit7 -type f 2>/dev/null
z7WtoNQU2XfjmMtWA8u5rN4vzqu4v99S
```

level7 - level8
```shell
bandit7@bandit:~$ cat data.txt | grep "millionth"
millionth       TESKZC0XvTetK0S9xNwm25STk5iWrBvP
```

level8 - level9
```shell
bandit8@bandit:~$ sort data.txt | uniq -u
EN632PlfYiZbn3PhVK3XOGSlNInNE00t
```

level9 - level10
```shell
bandit9@bandit:~$ strings data.txt | grep "==="
========== the
bu========== password
4iu========== is
========== G7w8LIi6J3kTb8A7j9LgrywtEUlyyp6s
```

level10 - level11
```shell
bandit10@bandit:~$ base64 -d data.txt
The password is 6zPeziLdR2RKNdNYFNb6nVCKzphlXHBM
```

level11 - level12
```shell
bandit11@bandit:~$ cat data.txt | tr 'a-zA-Z' 'n-za-mN-ZA-M'
The password is JVNBBFSmZwKKOP0XbFXOoW8chDz5yVRv
```

level12 - level13
```shell
bandit12: wbWdlBxEir4CaE8LaPhauuOo6pwRmrDw
```

level13 - level14
```shell
bandit13@bandit:~$ ssh -i sshkey.private 
```

level14 - level15
```shell
bandit14@localhost -p 2220
bandit14@bandit:~$ cat /etc/bandit_pass/bandit14
fGrHPx402xGC7U7rXKDaxiWFTOiF0ENq
bandit14@bandit:~$ nc localhost 30000
fGrHPx402xGC7U7rXKDaxiWFTOiF0ENq
Correct!
jN2kgmIXJ6fShzhT2avhotn4Zcka6tnt
```
level15 - level16
```shell
bandit15@bandit:~$ openssl s_client -connect localhost:30001
CONNECTED(00000003)
......
---
read R BLOCK
jN2kgmIXJ6fShzhT2avhotn4Zcka6tnt
Correct!
JQttfApK4SeyHwDlI9SXGR50qclOAil1

closed
```

level16 - level17
```shell
bandit16@bandit:~$ nmap -p31000-32000 localhost
Starting Nmap 7.80 ( https://nmap.org ) at 2022-09-23 19:26 UTC
Nmap scan report for localhost (127.0.0.1)
Host is up (0.00014s latency).
Not shown: 996 closed ports
PORT      STATE SERVICE
31046/tcp open  unknown
31518/tcp open  unknown
31691/tcp open  unknown
31790/tcp open  unknown
31960/tcp open  unknown

bandit16@bandit:~$ openssl s_client -connect localhost:31790
CONNECTED(00000003)
....
---
read R BLOCK
JQttfApK4SeyHwDlI9SXGR50qclOAil1
Correct!
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAvmOkuifmMg6HL2YPIOjon6iWfbp7c3jx34YkYWqUH57SUdyJ
imZzeyGC0gtZPGujUSxiJSWI/oTqexh+cAMTSMlOJf7+BrJObArnxd9Y7YT2bRPQ
Ja6Lzb558YW3FZl87ORiO+rW4LCDCNd2lUvLE/GL2GWyuKN0K5iCd5TbtJzEkQTu
DSt2mcNn4rhAL+JFr56o4T6z8WWAW18BR6yGrMq7Q/kALHYW3OekePQAzL0VUYbW
JGTi65CxbCnzc/w4+mqQyvmzpWtMAzJTzAzQxNbkR2MBGySxDLrjg0LWN6sK7wNX
x0YVztz/zbIkPjfkU1jHS+9EbVNj+D1XFOJuaQIDAQABAoIBABagpxpM1aoLWfvD
KHcj10nqcoBc4oE11aFYQwik7xfW+24pRNuDE6SFthOar69jp5RlLwD1NhPx3iBl
J9nOM8OJ0VToum43UOS8YxF8WwhXriYGnc1sskbwpXOUDc9uX4+UESzH22P29ovd
d8WErY0gPxun8pbJLmxkAtWNhpMvfe0050vk9TL5wqbu9AlbssgTcCXkMQnPw9nC
YNN6DDP2lbcBrvgT9YCNL6C+ZKufD52yOQ9qOkwFTEQpjtF4uNtJom+asvlpmS8A
vLY9r60wYSvmZhNqBUrj7lyCtXMIu1kkd4w7F77k+DjHoAXyxcUp1DGL51sOmama
+TOWWgECgYEA8JtPxP0GRJ+IQkX262jM3dEIkza8ky5moIwUqYdsx0NxHgRRhORT
8c8hAuRBb2G82so8vUHk/fur85OEfc9TncnCY2crpoqsghifKLxrLgtT+qDpfZnx
SatLdt8GfQ85yA7hnWWJ2MxF3NaeSDm75Lsm+tBbAiyc9P2jGRNtMSkCgYEAypHd
HCctNi/FwjulhttFx/rHYKhLidZDFYeiE/v45bN4yFm8x7R/b0iE7KaszX+Exdvt
SghaTdcG0Knyw1bpJVyusavPzpaJMjdJ6tcFhVAbAjm7enCIvGCSx+X3l5SiWg0A
R57hJglezIiVjv3aGwHwvlZvtszK6zV6oXFAu0ECgYAbjo46T4hyP5tJi93V5HDi
Ttiek7xRVxUl+iU7rWkGAXFpMLFteQEsRr7PJ/lemmEY5eTDAFMLy9FL2m9oQWCg
R8VdwSk8r9FGLS+9aKcV5PI/WEKlwgXinB3OhYimtiG2Cg5JCqIZFHxD6MjEGOiu
L8ktHMPvodBwNsSBULpG0QKBgBAplTfC1HOnWiMGOU3KPwYWt0O6CdTkmJOmL8Ni
blh9elyZ9FsGxsgtRBXRsqXuz7wtsQAgLHxbdLq/ZJQ7YfzOKU4ZxEnabvXnvWkU
YOdjHdSOoKvDQNWu6ucyLRAWFuISeXw9a/9p7ftpxm0TSgyvmfLF2MIAEwyzRqaM
77pBAoGAMmjmIJdjp+Ez8duyn3ieo36yrttF5NSsJLAbxFpdlc1gvtGCWW+9Cq0b
dxviW8+TFVEBl1O4f7HVm6EpTscdDxU+bCXWkfjuRb7Dy9GOtt9JPsX8MBTakzh3
vBgsyi/sN3RqRBcGU40fOoZyfAMT8s1m/uYv52O6IgeuZ/ujbjY=
-----END RSA PRIVATE KEY-----

closed

sudo chmod 600 key
ssh -i key bandit17@bandit.labs.overthewire.org -p2220
```

level17 - level18
```shell
bandit17@bandit:~$ diff passwords.new passwords.old
42c42
< hga5tuuCLF6fFzUpnagiMN8ssu9LFrdg
---
> 09wUIyMU4YhOzl1Lzxoz0voIBzZ2TUAf

 t@LAPTOP-DM2STLUG  ~  ssh -t bandit18@bandit.labs.overthewire.org -p2220 'cat readme'
                         _                     _ _ _
                        | |__   __ _ _ __   __| (_) |_
                        | '_ \ / _` | '_ \ / _` | | __|
                        | |_) | (_| | | | | (_| | | |_
                        |_.__/ \__,_|_| |_|\__,_|_|\__|


                      This is an OverTheWire game server.
            More information on http://www.overthewire.org/wargames
```

level18 - level19
```shell
bandit18@bandit.labs.overthewire.org's password:
awhqfNnAbc1naukrpqDYcF95h7HoMTrC
Connection to bandit.labs.overthewire.org closed.
```

level19 - level20
```shell
bandit19@bandit:/tmp/bandit19$ ~/bandit20-do cat /etc/bandit_pass/bandit20
VxCazJaVykI6W36BkBU0mJTCM8rR95XT
```

level20 - level21
```shell
bandit20:
https://gist.github.com/MohamedAlaa/2961058
step1: use tmux to split the terminal
step2: pane1 start a nc server (nc -l 3000)
step3: pane2 run ./suconnet 2231
step4: pane1 input bandit20's passwd

pane1:
bandit20@bandit:~$ nc -l 3000
VxCazJaVykI6W36BkBU0mJTCM8rR95XT
NvEJF7oVjkddltPSrdKEFOllh9V1IBcq

pane2:
bandit20@bandit:~$ ./suconnect 3000       │
Read: VxCazJaVykI6W36BkBU0mJTCM8rR95XT    │
Password matches, sending next password
```

level21 - level22
```shell
bandit21@bandit:/etc/cron.d$ ls
cronjob_bandit15_root  cronjob_bandit23       e2scrub_all
cronjob_bandit17_root  cronjob_bandit24       otw-tmp-dir
cronjob_bandit22       cronjob_bandit25_root  sysstat
bandit21@bandit:/etc/cron.d$ cat cronjob_bandit22
@reboot bandit22 /usr/bin/cronjob_bandit22.sh &> /dev/null
* * * * * bandit22 /usr/bin/cronjob_bandit22.sh &> /dev/null
bandit21@bandit:/etc/cron.d$ cat /usr/bin/cronjob_bandit22.sh
#!/bin/bash
chmod 644 /tmp/t7O6lds9S0RqQh9aMcz6ShpAoZKF7fgv
cat /etc/bandit_pass/bandit22 > /tmp/t7O6lds9S0RqQh9aMcz6ShpAoZKF7fgv
bandit21@bandit:/etc/cron.d$ cat /tmp/t7O6lds9S0RqQh9aMcz6ShpAoZKF7fgv
WdDozAdTM2z9DiFEQ2mGlwngMfj4EZff
```

level22- level23
```shell
bandit22@bandit:~$ cd /etc/cron.d/
bandit22@bandit:/etc/cron.d$ ls
cronjob_bandit15_root  cronjob_bandit17_root  cronjob_bandit22  cronjob_bandit23  cronjob_bandit24  cronjob_bandit25_root  e2scrub_all  otw-tmp-dir  sysstat
bandit22@bandit:/etc/cron.d$ cat cronjob_bandit23
@reboot bandit23 /usr/bin/cronjob_bandit23.sh  &> /dev/null
* * * * * bandit23 /usr/bin/cronjob_bandit23.sh  &> /dev/null
bandit22@bandit:/etc/cron.d$ cat /usr/bin/cronjob_bandit23.sh
#!/bin/bash

myname=$(whoami)
mytarget=$(echo I am user $myname | md5sum | cut -d ' ' -f 1)

echo "Copying passwordfile /etc/bandit_pass/$myname to /tmp/$mytarget"

cat /etc/bandit_pass/$myname > /tmp/$mytarget
bandit22@bandit:/etc/cron.d$ echo I am user bandit23 | md5sum | cut -d ' ' -f 1
8ca319486bfbbc3663ea0fbe81326349
bandit22@bandit:/etc/cron.d$ cat /tmp/8ca319486bfbbc3663ea0fbe81326349
QYw0Y2aiA672PsMmh9puTQuhoz8SyR2G
```

level23 - level24
```shell
bandit23@bandit:/usr/bin$ cd /etc/cron.d/
bandit23@bandit:/etc/cron.d$ ls
cronjob_bandit15_root  cronjob_bandit17_root  cronjob_bandit22  cronjob_bandit23  cronjob_bandit24  cronjob_bandit25_root  e2scrub_all  otw-tmp-dir  sysstat
bandit23@bandit:/etc/cron.d$ cat cronjob_bandit24
@reboot bandit24 /usr/bin/cronjob_bandit24.sh &> /dev/null
* * * * * bandit24 /usr/bin/cronjob_bandit24.sh &> /dev/null
bandit23@bandit:/etc/cron.d$ cat /usr/bin/cronjob_bandit24.sh
#!/bin/bash

myname=$(whoami)

cd /var/spool/$myname/foo
echo "Executing and deleting all scripts in /var/spool/$myname/foo:"
for i in * .*;
do
    if [ "$i" != "." -a "$i" != ".." ];
    then
        echo "Handling $i"
        owner="$(stat --format "%U" ./$i)"
        if [ "${owner}" = "bandit23" ]; then
            timeout -s 9 60 ./$i
        fi
        rm -f ./$i
    fi
dones
```

The access permission of the tmp folder matters.
We need to give out the write permission for bandit24.

```shell
bandit23@bandit:/tmp/xi$ ls -al
total 2132
drwxrwxr-x 2 bandit23 bandit23    4096 Oct 28 20:01 .
drwxrwx-wt 1 root     root     2166784 Oct 28 20:03 ..
-rw-rw-r-- 1 bandit23 bandit23       0 Oct 28 20:01 bandit24_pass.txt
-rwxrwxrwx 1 bandit23 bandit23     102 Oct 28 19:55 test.sh
-rw-rw-r-- 1 bandit23 bandit23       0 Oct 28 20:01 test.txt
bandit23@bandit:/tmp/xi$ chmod 777 .
bandit23@bandit:/tmp/xi$ ls -al
total 2132
drwxrwxrwx 2 bandit23 bandit23    4096 Oct 28 20:01 .
drwxrwx-wt 1 root     root     2166784 Oct 28 20:03 ..
-rw-rw-r-- 1 bandit23 bandit23       0 Oct 28 20:01 bandit24_pass.txt
-rwxrwxrwx 1 bandit23 bandit23     102 Oct 28 19:55 test.sh
-rw-rw-r-- 1 bandit23 bandit23       0 Oct 28 20:01 test.txt
bandit23@bandit:/tmp/xi$ cp test.sh /var/spool/bandit24/foo
bandit23@bandit:/tmp/xi$ cat /var/spool/bandit24/foo/test.sh
#!/bin/bash
echo "test"  > /tmp/xi/test.txt
cat /etc/bandit_pass/bandit24 > /tmp/xi/bandit24_pass.txt
bandit23@bandit:/tmp/xi$ ls -l
total 12
-rwxrwxrwx 1 bandit23 bandit23  33 Oct 28 20:06 bandit24_pass.txt
-rwxrwxrwx 1 bandit23 bandit23 102 Oct 28 19:55 test.sh
-rwxrwxrwx 1 bandit23 bandit23   5 Oct 28 20:06 test.txt
bandit23@bandit:/tmp/xi$ cat bandit24_pass.txt
VAfGXJ1PBSsPSnvsjI8p759leLZ9GGar
```

level24 - level25
```shell
bandit24@bandit:/tmp/tmp.ezC2VPgMil$ ls
a.py  list.txt  result.log  result.txt
bandit24@bandit:/tmp/tmp.ezC2VPgMil$ cat a.py
bandit24_pass = "VAfGXJ1PBSsPSnvsjI8p759leLZ9GGar"
with open('list.txt', 'w') as file:
    for i in range(0, 9999):
        file.write('{} {}\n'.format(bandit24_pass, str(i).zfill(4)))
bandit24@bandit:/tmp/tmp.ezC2VPgMil$ python3 a.py
bandit24@bandit:/tmp/tmp.ezC2VPgMil$ cat list.txt | nc localhost 30002 > result.txt
bandit24@bandit:/tmp/tmp.ezC2VPgMil$ cat result.txt  | grep pass
I am the pincode checker for user bandit25. Please enter the password for user bandit24 and the secret pincode on a single line, separated by a space.
The password of user bandit25 is p7TaowMYrmu23Ol8hiZh9UvD0O9hpx8d
```

level25 - level26 - level27
Change the size of the terminal, go into the vim by typing `v`.
```shell
:set shell = /bin/bash
:terminal
bandit26@bandit:~$ ./bandit27-do cat /etc/bandit_pass/bandit27
YnQpBuifNMas1hcUFk70ZmqkhUU2EuaS
```

level27 - level28
```shell
bandit27@bandit:~$ mktemp -d
/tmp/tmp.cml7af08H3
bandit27@bandit:~$ cd /tmp/tmp.cml7af08H3
bandit27@bandit:/tmp/tmp.cml7af08H3$ git clone ssh://bandit27-git@localhost:2220/home/bandit27-git/repo
Cloning into 'repo'...
The authenticity of host '[localhost]:2220 ([127.0.0.1]:2220)' can't be established.
ED25519 key fingerprint is SHA256:C2ihUBV7ihnV1wUXRb4RrEcLfXC5CXlhmAAM/urerLY.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Could not create directory '/home/bandit27/.ssh' (Permission denied).
Failed to add the host to the list of known hosts (/home/bandit27/.ssh/known_hosts).
                         _                     _ _ _
                        | |__   __ _ _ __   __| (_) |_
                        | '_ \ / _` | '_ \ / _` | | __|
                        | |_) | (_| | | | | (_| | | |_
                        |_.__/ \__,_|_| |_|\__,_|_|\__|


                      This is an OverTheWire game server.
            More information on http://www.overthewire.org/wargames

bandit27-git@localhost's password:
remote: Enumerating objects: 3, done.
remote: Counting objects: 100% (3/3), done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
Receiving objects: 100% (3/3), done.
bandit27@bandit:/tmp/tmp.cml7af08H3$ ls
repo
bandit27@bandit:/tmp/tmp.cml7af08H3$ cd repo/
bandit27@bandit:/tmp/tmp.cml7af08H3/repo$ ls
README
bandit27@bandit:/tmp/tmp.cml7af08H3/repo$ cat README
The password to the next level is: AVanL161y9rsbcJIsFHuw35rjaOM19nR
```

level28 - level29
```shell
bandit28@bandit:/tmp/tmp.l9j1w7IqnX/repo$ git config --list
user.email=noone@overthewire.org
user.name=Ben Dover
core.repositoryformatversion=0
core.filemode=true
core.bare=false
core.logallrefupdates=true
remote.origin.url=ssh://bandit28-git@localhost:2220/home/bandit28-git/repo
remote.origin.fetch=+refs/heads/*:refs/remotes/origin/*
branch.master.remote=origin
branch.master.merge=refs/heads/master
bandit28@bandit:/tmp/tmp.l9j1w7IqnX/repo$ ls -al
total 16
drwxrwxr-x 3 bandit28 bandit28 4096 Nov  4 20:14 .
drwx------ 3 bandit28 bandit28 4096 Nov  4 20:14 ..
drwxrwxr-x 8 bandit28 bandit28 4096 Nov  4 20:22 .git
-rw-rw-r-- 1 bandit28 bandit28  111 Nov  4 20:14 README.md
bandit28@bandit:/tmp/tmp.l9j1w7IqnX/repo$ ls
README.md
bandit28@bandit:/tmp/tmp.l9j1w7IqnX/repo$ git log
commit 43032edb2fb868dea2ceda9cb3882b2c336c09ec (HEAD -> master, origin/master, origin/HEAD)
Author: Morla Porla <morla@overthewire.org>
Date:   Thu Sep 1 06:30:25 2022 +0000

    fix info leak

commit bdf3099fb1fb05faa29e80ea79d9db1e29d6c9b9
Author: Morla Porla <morla@overthewire.org>
Date:   Thu Sep 1 06:30:25 2022 +0000

    add missing data

commit 43d032b360b700e881e490fbbd2eee9eccd7919e
Author: Ben Dover <noone@overthewire.org>
Date:   Thu Sep 1 06:30:24 2022 +0000

    initial commit of README.md

bandit28@bandit:/tmp/tmp.l9j1w7IqnX/repo$ git log -p -1
commit 43032edb2fb868dea2ceda9cb3882b2c336c09ec (HEAD -> master, origin/master, origin/HEAD)
Author: Morla Porla <morla@overthewire.org>
Date:   Thu Sep 1 06:30:25 2022 +0000

    fix info leak

diff --git a/README.md b/README.md
index b302105..5c6457b 100644
--- a/README.md
+++ b/README.md
@@ -4,5 +4,5 @@ Some notes for level29 of bandit.
 ## credentials

 - username: bandit29
-- password: tQKvmcwNYcFS6vmPHIUSI3ShmsrQZK8S
+- password: xxxxxxxxxx
```

level29 - level30
```shell
bandit29@bandit:/tmp/tmp.tDhy5zyEVG/repo$ cat README.md
# Bandit Notes
Some notes for bandit30 of bandit.

## credentials

- username: bandit30
- password: <no passwords in production!>

bandit29@bandit:/tmp/tmp.tDhy5zyEVG/repo$ git log
commit 1748acec99ba66676acd551c2932fb9fc14a98a3 (HEAD -> master, origin/master, origin/HEAD)
Author: Ben Dover <noone@overthewire.org>
Date:   Thu Sep 1 06:30:26 2022 +0000

    fix username

commit c27fff763003bb1d57d311e6763211110b94cc87
Author: Ben Dover <noone@overthewire.org>
Date:   Thu Sep 1 06:30:26 2022 +0000

    initial commit of README.md
bandit29@bandit:/tmp/tmp.tDhy5zyEVG/repo$ git branch
* master
bandit29@bandit:/tmp/tmp.tDhy5zyEVG/repo$ git log -p -1
commit 1748acec99ba66676acd551c2932fb9fc14a98a3 (HEAD -> master, origin/master, origin/HEAD)
Author: Ben Dover <noone@overthewire.org>
Date:   Thu Sep 1 06:30:26 2022 +0000

    fix username

diff --git a/README.md b/README.md
index 2da2f39..1af21d3 100644
--- a/README.md
+++ b/README.md
@@ -3,6 +3,6 @@ Some notes for bandit30 of bandit.

 ## credentials

-- username: bandit29
+- username: bandit30
 - password: <no passwords in production!>

bandit29@bandit:/tmp/tmp.tDhy5zyEVG/repo$ git branch -r
  origin/HEAD -> origin/master
  origin/dev
  origin/master
  origin/sploits-dev
bandit29@bandit:/tmp/tmp.tDhy5zyEVG/repo$ git checkout dev
Branch 'dev' set up to track remote branch 'dev' from 'origin'.
Switched to a new branch 'dev'
bandit29@bandit:/tmp/tmp.tDhy5zyEVG/repo$ git branch
* dev
  master
bandit29@bandit:/tmp/tmp.tDhy5zyEVG/repo$ git log
commit 2b1395f00cfb986163082c50100be5be8f249f64 (HEAD -> dev, origin/dev)
Author: Morla Porla <morla@overthewire.org>
Date:   Thu Sep 1 06:30:26 2022 +0000

    add data needed for development

commit 989df8073e16b5f7ec337f51bc1f60bd2f6b7e0b
Author: Ben Dover <noone@overthewire.org>
Date:   Thu Sep 1 06:30:26 2022 +0000

    add gif2ascii

commit 1748acec99ba66676acd551c2932fb9fc14a98a3 (origin/master, origin/HEAD, master)
Author: Ben Dover <noone@overthewire.org>
Date:   Thu Sep 1 06:30:26 2022 +0000

    fix username

commit c27fff763003bb1d57d311e6763211110b94cc87
Author: Ben Dover <noone@overthewire.org>
Date:   Thu Sep 1 06:30:26 2022 +0000

    initial commit of README.md
bandit29@bandit:/tmp/tmp.tDhy5zyEVG/repo$ git log -p -1
commit 2b1395f00cfb986163082c50100be5be8f249f64 (HEAD -> dev, origin/dev)
Author: Morla Porla <morla@overthewire.org>
Date:   Thu Sep 1 06:30:26 2022 +0000

    add data needed for development

diff --git a/README.md b/README.md
index 1af21d3..a4b1cf1 100644
--- a/README.md
+++ b/README.md
@@ -4,5 +4,5 @@ Some notes for bandit30 of bandit.
 ## credentials

 - username: bandit30
-- password: <no passwords in production!>
+- password: xbhV3HpNGlTIdnjUrdAlPzc2L6y9EOnS
```

level30 - level31
```shell
bandit30@bandit:/tmp/tmp.9BKF1Bcoie$ ls
repo
bandit30@bandit:/tmp/tmp.9BKF1Bcoie$ cd repo/
bandit30@bandit:/tmp/tmp.9BKF1Bcoie/repo$ ls
README.md
bandit30@bandit:/tmp/tmp.9BKF1Bcoie/repo$ cat README.md
just an epmty file... muahaha
bandit30@bandit:/tmp/tmp.9BKF1Bcoie/repo$ git log
commit a325f29e1cc26b0f0dc5f89b4348e389b408cc87 (HEAD -> master, origin/master, origin/HEAD)
Author: Ben Dover <noone@overthewire.org>
Date:   Thu Sep 1 06:30:28 2022 +0000

    initial commit of README.md
bandit30@bandit:/tmp/tmp.9BKF1Bcoie/repo$ git branch -r
  origin/HEAD -> origin/master
  origin/master
bandit30@bandit:/tmp/tmp.9BKF1Bcoie/repo$ git tag
secret
bandit30@bandit:/tmp/tmp.9BKF1Bcoie/repo$ git show secret
OoffzGDlzhAlerFJ2cAiz1D41JW1Mhmt
```

level31 - level32
```shell
bandit31@bandit:/tmp/tmp.dueSKYQYba/repo$ git add -f key.txt
bandit31@bandit:/tmp/tmp.dueSKYQYba/repo$ git commit -m "test"
[master 5a015fb] test
 1 file changed, 1 insertion(+), 1 deletion(-)
bandit31@bandit:/tmp/tmp.dueSKYQYba/repo$ git push origin master
The authenticity of host '[localhost]:2220 ([127.0.0.1]:2220)' can't be established.
ED25519 key fingerprint is SHA256:C2ihUBV7ihnV1wUXRb4RrEcLfXC5CXlhmAAM/urerLY.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Could not create directory '/home/bandit31/.ssh' (Permission denied).
Failed to add the host to the list of known hosts (/home/bandit31/.ssh/known_hosts).
                         _                     _ _ _
                        | |__   __ _ _ __   __| (_) |_
                        | '_ \ / _` | '_ \ / _` | | __|
                        | |_) | (_| | | | | (_| | | |_
                        |_.__/ \__,_|_| |_|\__,_|_|\__|


                      This is an OverTheWire game server.
            More information on http://www.overthewire.org/wargames

bandit31-git@localhost's password:
Enumerating objects: 7, done.
Counting objects: 100% (7/7), done.
Delta compression using up to 2 threads
Compressing objects: 100% (4/4), done.
Writing objects: 100% (6/6), 527 bytes | 527.00 KiB/s, done.
Total 6 (delta 1), reused 0 (delta 0), pack-reused 0
remote: ### Attempting to validate files... ####
remote:
remote: .oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.
remote:
remote: Well done! Here is the password for the next level:
remote: rmCBvG56y58BXzv98yZGdO7ATVL5dW8y
remote:
remote: .oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.
remote:
remote:
remote: .oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.
remote:
remote: Wrong!
remote:
remote: .oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.
remote:
To ssh://localhost:2220/home/bandit31-git/repo
 ! [remote rejected] master -> master (pre-receive hook declined)
error: failed to push some refs to 'ssh://localhost:2220/home/bandit31-git/repo'
bandit31@bandit:/tmp/tmp.dueSKYQYba/repo$ cat key.txt
May I come in?
```

level32 - level33
```shell
WELCOME TO THE UPPERCASE SHELL
>> ls
sh: 1: LS: not found
>> LS
sh: 1: LS: not found
>> $0
$ pwd
/home/bandit32
$ cat /etc/bandit_passwd/bandit33
cat: /etc/bandit_passwd/bandit33: No such file or directory
$ cat /etc/bandit_pass/bandit33
odHo63fHiFqcWWJG9rLiLDtPm45KzUKy
$
```

level33 - level34
```shell
bandit33@bandit:~$ ls
README.txt
bandit33@bandit:~$ cat README.txt
Congratulations on solving the last level of this game!

At this moment, there are no more levels to play in this game. However, we are constantly working
on new levels and will most likely expand this game with more levels soon.
Keep an eye out for an announcement on our usual communication channels!
In the meantime, you could play some of our other wargames.

If you have an idea for an awesome new level, please let us know!
```