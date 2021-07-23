# chap1

## 3 functions for OS:

- share a computer among multiple programs and provide services
  - services provided through an interface(shell is common)
    - shell read commands from user and excutes them
    - user program, not part of the kernel
  - when user program invokes a system call, hardware raises the privilege level and starts executing function in the kernel
- share hardware among multiple programs, make them run(or appear to run) at the same time
- controll ways for programs to interact

## xv6's services

### Processes and memory

- user-space memory(instructions, data, and stack)
- per-process state private to the kernel

*time-share* processes: transparently switches the available CPUs(idenfied with *pid*)

​		waiting: schedule

​		not executing: saves its CPU registers 

​		running: restoring registers when next runs

***fork***: process create a new process(child process, same memory contents). In the parent, *fork* returns the child's pid; in the child, it returns zero.

```c
int pid = fork();
if (pid > 0) {
  prinft("parent: child = %d\en", pid);
  pid = wait(0);		 
  printf("child %d is done\en", pid);
} else if (pid == 0) {
  printf (child: exiting\en");
          exit(0);			
} else {
  printf("fork error\en");
}
```

***exec***: replaces the calling process's memory with a new memory image loaded from a file stored in the file system.

***wait*** : returns the pid of an exited child of the current process and copies the exit status of the child to the address passed to wait.

***exit***: stops the calling process and release resources. takes an integer status argument. 0 to success, 1 to fail

###File description

file description is a small integer reprensenting a kernel-managed pbject that a process may read from or write to.                    Abstracts, streams of bytes

file description is an index into a per-process table

```
reads: descriptor 0
writes: descriptor 1
writes error: descriptor 2
```

read and write system calls read bytes from and write bytes to open files named by file descriptors.

***read(fd, buf, n)***: reads at most ***n*** bytes from the file descriptor ***fd***, copies into ***buf***, and returns the number of bytes read. Each file descriptor that refers to a file has an offset associated with it. returns 0 when it is the end of the file

***write(fd, buf, n)***: writes n bytes from buf to the file descriptor fd and returns the number of bytes written. each write picks up where the previus one left off.

See the simple implementation of ***cat***, copies data from its standard input to its standard output:

```c
char buf[512];
int n;

for(;;) {
  n = read(0, buf, sizeof buf);
  if (n == 0)
    break;
  if (n < 0) {
    fprintf(1, "read error\en");
    exit();
  }
  if (write(1, buf, n) != n) {
    fprintf(2, "write error\en");
    exit();
  }
}
```

***close***: release a file descriptor, making it free for reuse by a future ***open***, ***pipe***, or ***dup*** system call.

***I/O redirection***: ***Fork*** copies the parent's file descriptor table with its memory. ***Exec*** replaces the calling process's memory but preserves its file table, allowing the shell to implement I/O redirection by forking, reopening chosen file description, and then execing the new peogram.

See the implementation for the command ***cat < input.txt***:

```c
char *argv[2];

argv[0] = "cat";
argv[1] = 0;
if (fork() == 0) {
  close(0);
  open("input.txt", O_RDONLY);   //no file checking
  exec("cat", argv);
}
```



### Pipes

pipe is a small kernel buffer exposed to processes as a pair of file descriptors, one fore reading and one for writing.    processes communication







### file system



























