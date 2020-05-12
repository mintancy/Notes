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

In `switch` statement, the break statement causes an immediate eaxit from the `switch`. Because cases serve just as labels, after the code for one case is done, execution falls through to the next unless you take explicit action to escape.

`goto and labels`: break out of two or more loops at once. 

# Chapter 4 - Functions and Program Structure

If the return type is omitted, int is assumed.

The return statement is the mechanism for returning a value from the called function to its caler. Any expressions can follow return:

    return espression;

The expression wiil be converted to the return type of the function if necessary. Parentheses are often used around the expression, but they are optional.

If the return of the function is neither no value (void) nor an int, the function musr declare the type of value it returns. `double atof () {}`.

The function must be declared and defined consistently.

`double sum, atof()` the variable and function can be declared together if they have the same type.

The standard library includes a function `ungetch` that provides one character of pushback.

If an external variable is to be referred to before it is defined, or if it is defined in a different source file from the one where it is being used, then an extern declaration is mandatory.

> There must be only one definition of an external variable among all the files that make up the source program; other files may contain extern declarations to access it. (There may also be extern declarations in the file containing the definition.) Array sizes must be specified with the definition, but are optional with an extern declaration.

One header file that contains everthing that is to be shared between any two parts of the program.

`static` provides a way to hide names.

External `static`: often used for variables, but it can be applied to functions as well.

Internal `static`: local to a particular function just as automatic variables are, but unlike automatics, they remain in existence ranther than coming and going each time the function is activated.

A `register` declaration advises the compiler that the variable in quesiton will be heavily used (faster and smaller). But compiler are free to ignore the advice.
The `register` declaration can only be applied to automatic variables and to the formal parameters of a function.
```c
register int x;
f (register unsigned m, register long n) {
    register int i;
}
```

In the absence of explicit initialization, external and static variables are guaranted to be initialized to zero; automatic and register variables have undefined initial values.

For external and static variables, the initializer must be a constant expression; the initialization is done once, conceptionally before the program begins execution. For automatic and register variables, the initializer is not restricted to being a constant: it may be any expression involving previously defined values, even function calls.

```c
char pattern[] = "ould";
equals to 
char pattern[] = {'o', 'u', 'l', 'd', '\0'};
```

`The C Preprocessor`

C provides certain language facilities by means of a preprocessor, which is conceptionally a separate first step in compilation. The two most frequently used features are `#include` , to include the contents of a file during compilation, and `#define`, to replace a token by an arbitrary sequence of characters.

- File Inclusiong: 
    - `#include "filename" (<filename>)`
- Macro Substitution: 
    - `#define name replacement_text`

        ```c
        #define forever for(;;)
        #define max(A, B) ((A) > (B) ? (A) : (B))
        // Then 
        x = max (p + q, r + s); 
        // will be replaced by:
        x = ((p+q) > (r+s) ? (p+q) : (r+s));
        ```

    Names may be undefined with #undef
    Formal parameters are not replaced within quoted strings. If, however, a parameter name is preceded by a # in the replacement text, the combination will be expanded into a quated string with the parameter replaced by the actual argument.

        #define dprint(expr) printf(#expr " = %g\n", expr)
        // When this is invoked, as in
            dprintf(x/y);
        // the macro is expanded into 
            printf("x/y" " = &g\n", x/y);
        // equals to:
            printf("x/y = &g\n", x/y);

    The preprocessor operator `##` provides a way to concatenate actual arguments during macro expansion. If a parameter in the replacement text is adjacent to a `##`, the parameter is replaced by the actual argument, the `##` and surrounding white space are removed, and the result is rescanned. For example, the macro paste concatenates its two arguments:
    ```c
    #define paste(front, back) front ## back
    So paste(name, 1) creates the token name1
    ```
- Conditional Inclusion

    ```c
    #ifndef HDR
    #define EDR
    /* hdr.h 文件的内容放在这里 */
    #endif
    ```

