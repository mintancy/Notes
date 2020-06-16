

## Preparations

REQUIREMENT (I used the virtualbox with ubuntu16.04-desktop):

- Memory: at least 12GB (or 10GB memory + 8GB swap memory)
- Disk: at least 100GB
- Time costs: at least 10 hours, depends on the performance of your system.

Before installing the llvm, make sure the system provides at least 12GB memory. If not, 10GB memory with 8GB swap will also work. But the make thread should be set lower than 8 and need two more steps:

1. Change the link tool to gold:

```shell
$ sudo rm ld
$ sudo cp -d gold ld
```

2. Add swap memory: <https://www.digitalocean.com/community/tutorials/how-to-add-swap-on-ubuntu-14-04>

Then prepare the environment for the llvm

```shell
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install build-essential subversion cmake python3-dev libncurses5-dev libxml2-dev libedit-dev swig doxygen graphviz xz-utils
```

Remember change the svn timeout setting: 

```c++
// open ~/.subverion/servers
// change 
# http-timeout = 60
// to
http-timeout = 6000
```

If you don't modify this line, when you try to download the source code with svn, it will genreate timeout errors because the size of LLVM is not small.

## Download the LLVM

Reference: <https://solarianprogrammer.com/2013/01/17/building-clang-libcpp-ubuntu-linux/>

Download the latest stable LLVM:

```shell
$ cd ~
$ mkdir llvm_all && cd llvm_all
$ svn co http://llvm.org/svn/llvm-project/llvm/tags/RELEASE_900/final llvm
 
$ cd llvm/tools
$ svn co http://llvm.org/svn/llvm-project/cfe/tags/RELEASE_900/final clang

$ cd ../..
$ cd llvm/projects
$ svn co http://llvm.org/svn/llvm-project/compiler-rt/tags/RELEASE_900/final compiler-rt
$ svn co http://llvm.org/svn/llvm-project/libcxx/tags/RELEASE_900/final libcxx
$ svn co http://llvm.org/svn/llvm-project/libcxxabi/tags/RELEASE_900/final libcxxabi
$ svn co http://llvm.org/svn/llvm-project/polly/tags/RELEASE_900/final polly
$ svn co http://llvm.org/svn/llvm-project/lld/tags/RELEASE_900/final lld
$ svn co http://llvm.org/svn/llvm-project/openmp/tags/RELEASE_900/final openmp
$ svn co http://llvm.org/svn/llvm-project/libunwind/tags/RELEASE_900/final libunwind
```

## Build and install the LLVM

- I want to use the llc to generate the dag figures, so I set the `DCMAKE_BUILD_TYPE=Debug`. If you set `DCMAKE_BUILD_TYPE=Relaese`, it will need smaller memory than debug type.
- I want to use X86 and ARM platform, so I set `-DLLVM_TARGETS_TO_BUILD="X86;ARM"` . If you don't set this option, llvm will be built for all targets.
- I don't want the tests ot examples, so I off all those options.
- I opened shared libraries and the benchmark.
- ATTENTION: If you stll got memory errors after setting link tool and swap memory when use `make -j 8`, reduce the 8 to 4 or 2 will help.

```shell
$ cd ~/llvm_all
$ mkdir build && cd build
$ cmake -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Debug -DLLVM_ENABLE_ASSERTION=ON -DLLVM_TARGETS_TO_BUILD="X86;ARM" -DLLVM_BUILD_TESTS=OFF -DLLVM_BUILD_EXAMPLES=OFF -DLLVM_INCLUDE_TESTS=OFF -DLLVM_INCLUDE_EXAMPLES=OFF -DLLVM_SHARED_LIBS=ON -DLLVM_BUILD_BENCHMARKS=ON -DLLVM_BUILD_DOCS=OFF -DCMAKE_INSTALL_PREFIX=/usr/local/clang_9.0.0 ../llvm
 
$ make -j 8 
$ sudo make install/strip
```

## Add clang to the system path

```shell
$ cd ~
$ echo 'export PATH=/usr/local/clang_9.0.0/bin:$PATH' >> ~/.bashrc
$ echo 'export LD_LIBRARY_PATH=/usr/local/clang_9.0.0/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
$ source ~/.bashrc
```

If you use oh-my-zsh, change the ~/.bashrc file to ~/.zshrc file.

## Download and build lldb

I still set the build type to `debug`.

```shell
$ cd ~/llvm_all
$ svn co http://llvm.org/svn/llvm-project/lldb/tags/RELEASE_900/final lldb
$ mkdir build2 && cd build2
$ cmake -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=/usr/local/clang_9.0.0 ../lldb
$ make -j 8
$ sudo make install/strip
```

If you meet error when you run cmake, such as 

```
Found imcompatible python interpreter and python libraries.
```

That is because the version of the python interpreter and python libraries should be the same. (The minimal version is 3.5).

Add options when cmake (https://runsisi.com/2019-08-28/cmake-choose-python):

```shell
$ cmake -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Debug -DPythonInterp_FIND_VERSION=3.5 -DPythonInterp_FIND_VERSION_MAJOR=3 -DCMAKE_INSTALL_PREFIX=/usr/local/clang_9.0.0 ../lldb
```

## LLVM with graphviz

LLVM can create the dag figure and open with graphviz, but the LLVM and lldb must set the `CMAKE_BUILD_TYPE` to `Debug`.  If llc with view option can not generate the .dot file, add `-fast-isel=false` option.

```shell
$ llc --help-hidden | grep dag
$ clang -ccl -emit-llvm test.cpp -o test.ll
$ llc -fast-isel=false --view-dag-combin1-dags test.ll
Writing 'tmp/dag._xxx.dot'... done
Trying 'xdg-open' program... Remember to erase graph file: /tmp/dag._xxx.dot
```

But I got an error when try to open this dot file

```
gvfs-open: /tmp/dag._xxx.dot: error opening location: No application is registered as bandling this file.
```

We can open this dot file manuly:

```shell
$ dot -Tpng /tmp/dag._xxx.dat > test.png
```

Then open the test.png file. But this is not so convenient. We still want to use llc command and call graphviz to open the dot file automatically. Let us find out other solutions.

