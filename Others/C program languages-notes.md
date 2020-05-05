# Chapter 1

'stdio.h' is a standard input/output library from ANSI, not a part of the C language.

'#' defines symbolic constants

```c
#include <stdio.h>

main()
{
    int c;
    int c = getchar();
    while (c != EOF) {
        putchar(c);
        c = getchar();
    }
}
```

'EOF' is an integer defined in `<stdio.h>`

An assignment can appear as part of a larger expression:

```c
#include <stdio.h>

main()
{
    int c;
    while ((c = getchar()) != EOF) {
        putchar(c);
    }
}
```

The precedence of `!=` is higher than that of `=`