# level0-level1

https://r4stl1n.github.io/2014/12/21/OverTheWire-Utumno0.html

first, we try to run it:

```shell
utumno0@utumno:/utumno$ ./utumno0
Read me! :P
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

# level1-level2









































