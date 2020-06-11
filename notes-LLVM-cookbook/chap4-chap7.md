# Chapter 4: Preparing Optimizations

> After the source code is compiled to IR, it can be optimized into more effective code. A pass serves the purpose of optimizing LLVM IR. 
> A pass runs over the LLVM IR, processes the IR, analyzes it, identifies the optimization opportunities, and modifies the IR to produce optimized code.

`opt` <http://llvm.org/docs/CommandGuide/opt.html> is used to run optimization passes on LLVM IR.

Converts the C into LLVM IR first:

```shell
$ clang -S -O0 -emit-llvm example.c
```

Different opt levels:

```shell
$ opt -O0 -S example.ll // this is not provided in my version of llvm (4.0)
$ opt -O1 -S example.ll
$ opt -O2 -S example.ll
$ opt -O3 -S example.ll
```

## Writing your own LLVM pass

A pass is an instance of the Pass LLVM class.