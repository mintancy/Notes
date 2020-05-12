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
There is no input will be `EOF` except in the file, so should use the keyboard `Ctrl+D`

The precedence of `!=` is higher than that of `=`

For test at the top of the loop, before proceeding with the body.

extern is used when different files want to call the same variable.

"Definition" refers to the place where the variable is created or assigned storage; "declaration" refers to places where the nature of the variable is
stated but no storage is allocated.

# Chapter 2

Lower case for variable names, and all upper case for symbolic canstants.

`int`: an integer, typically reglecting the natural size of integers on the host machines.

> short int --> short
> long int --> long

The word int can be omitted in such declarations.

A constant expression is an expression that involves only constants. Such expressions may be evaluated dt during compilation rather than run-time, and according may be used in any place that a constant can occur, as in:
```c
#define MAXLINE 1000
char line[MAXLINE+1];
``` 

`'x'`: is a integer, used to produce the numberic value of the letter x in the machine's character set.

`"x"`: is an array of characters that contains one character and a '\0'.

The qualifier const can be applied to the declaration of any variable to specify that its value will not be changed. For an array, the const qualifier says that the elements will not be altered.

```c
n = 5;
a = n++;
a equals to 5;
n = 5;
b = ++n;
b equals to 6;
both n equals to 6.
```

## Bitwise Operators
```c
&   bitwise AND
|   bitwise inclusive OR
^   bitwise exclusive OR
<<  left shift
>>  right shift
~   one's complement (unary)
```

The bitwise AND operator & is often used to mask off some set of bits, for example `n = n & 0177;` sets to zero all but low-order 7 bits of n.

The bitwise OR operator | is used to turn bits on: `x = x | SET_ON;` sets to one in x the bits that are set to one in SET_ON.

The bitwise exclusive OR operator ^ sets a one in each bit position where its operands have different bits, and zero where they are the same.

The unary operator ~ yields the one's complement of an integer; that is, it converts each 1-bit into a 0-bit and vice versa. For example `x = x & ~077` sets the last six bits of x to zero.

```c
/* getbits: get n bits from position p */
unsigned getbits (unsigned x, int p, int n){
    return (x >> (p+1-n)) & ~(~0 << n);
}
```

**Exercise** 2-6. Write a function setbits(x, p, n, y) that returns x with the n bits that begin at position p set to the rightmost n bits of y, leaving the other bits unchanged.
```c
#include <stdio.h>

int setbits(int, int, int, int);

main()
{
	int a = setbits(255, 0, 4, 0);
	printf("%d\n", a);

	int b = setbits(1, 1, 3, 4);
	printf("%d\n", b);

	int c = setbits(218, 2, 4, 9);
	printf("%d\n", c);
}

int setbits(int x, int p, int n, int y)
{
	x = x & (~((~(~0 << n)) << p));
	y = (y & (~(~0 << n))) << p;

	return x | y;
}
```

**Exercise** 2-7. Write a function invert(x,p,n) that returns x with the n bits that begin at position p inverted (i.e., 1 changed into 0 and vice versa), leaving the others unchanged.
```c
#include <stdio.h>

int invert(int, int, int);

main()
{
	int a = invert(255, 0, 4);
	printf("%d\n", a);

	int b = invert(0, 4, 4);
	printf("%d\n", b);
	
	int c = invert(15, 4, 4);
	printf("%d\n", c);
}

int invert(int x, int p, int n)
{
	return x ^ (~(~0 << n) << p);
}
```

**Exercise** 2-8. Write a function rightrot(x,n) that returns the value of the integer x rotated to the right by n positions.
```c
#include <stdio.h>

unsigned rightrot(unsigned, unsigned);

main()
{
	int a = rightrot(255, 32);
	printf("%d\n", a);

	int b = rightrot(1, 30);
	printf("%d\n", b);
}

unsigned rightrot(unsigned x, unsigned n)
{
	while (n-- > 0) {
		if (x & 1 == 1) {
			x = (x >> 1) | ~(~0U >> 1);
		} else {
			x = x >> 1;
		}
	}

	return x;
}
```

## Assignment Operators and Expressions

`expr1 op= expr2` is equivalent to `expr1 = (expr1) op (expr2)` except that expr1 is computed only once.

**Exercise** 2-9. In a two's complement number system, x &= (x-1) deletes the rightmost 1-bit in x . Explain why. Use this observation to write a faster version of bitcount .
```c
#include <stdio.h>

int bitcount(unsigned);

main()
{
	printf("%d\n", bitcount(255));
	printf("%d\n", bitcount(15));
	printf("%d\n", bitcount(1));
	printf("%d\n", bitcount(0));
	printf("%d\n", bitcount(~0U));
}

int bitcount(unsigned x)
{
	int b;
	for (b = 0; x != 0; x >>= 1)
		if (x & 01)
			b++;

	return b;
}
```

## Conditional Expressions

expr1 ? expr2 : expr3

```c
if (a > b)
    z = a;
else
    z = b;
is equivalent to 
z = (a > b) ? a : b; /* z = max(a, b)*/
```

**Exercise** 2-10. Rewrite the function lower , which converts upper case letters to lower case, with a conditional expression instead of if-else .
```c
#include <stdio.h>

int lower(int);

main()
{
	printf("%c\n", lower('S'));
	printf("%c\n", lower('A'));
	printf("%c\n", lower('Z'));
	printf("%c\n", lower('a'));
}

int lower(int c)
{
	return (c >= 'A' && c <= 'Z') ? (c + 'a' - 'A') : c;
}
```

# Chapter 3 - Control Flow

