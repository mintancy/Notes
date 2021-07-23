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

Example: pass function block counter. This pass will simply display the name of the function and count the basic blocks in that function when run.

1. A Makefile needs to be written for the pass.

   - Open and modify a Makefile in the llvm lib/Tranform folder:

     ```c++
     // Specify the path to the LLVM root folder and the library name, and make this pass a loadable module by specifying it in Makefile. All the .cpp files in the current directory are to be compiled and libked in a shared object.
     LEVEL = ../../..
     LIBRARYNAME = FuncBlockCount 
     LOADABLE_MODULE = 1 
     include $(LEVEL)/Makefile.common
     ```

2. Create the new .cpp file called FuncBlockCount.cpp. This is the pass.

   ```c++
   // Include the header files
   #include "llvm/Pass.h" 
   #include "llvm/IR/Function.h" 
   #include "llvm/Support/raw_ostream.h"
   // Include the llvm namespace to enable access to LLVM functions
   using namespace llvm;
   // Then start with an anonymous namespace
   namespace {
     // declare the pass
     struct FuncBlockCount : public FunctionPass {
       // declare the pass identifier, which will be used by LLVM to identify the pass
       static char ID;
       FuncBlockCount () : FunctionPass(ID) {
         // Most importantly: writing a run function. FuncBlockCount pass inherits FunctionPass and runs on a function, a runOnFunction is defined to be run on a function
         bool runOnFunction(Function &F) override {
           errs() << "Function " << F.getName() << '\n';	// Prints the name of the function that is being processed
           return false;
         }
       };
     }
     // Initialize the pass ID
     char FuncBlockCount::ID = 0;
     // Register the pass with a coomand-line argument and a name
     static RegisterPass<FuncBlockCount> X("funcblockcount", "Function Block Count", false, false);
   }
   ```

3. Compile the pass with a simple gmake command, then a new file FuncBlockCount.so is generated at the LLVM root directory. This shared object file can be dynamically loaded to the opt tool to run it on a piece of LLVM IR code. <http://llvm.org/docs/WritingAnLLVMPass.html>

## Running your own pass with the opt tool

Now the FuncBlockCount pass is ready to be run on the LLVM IR.

1. Write the C test code: sample.c

   ```c++
   int foo(int n, int m) {
     int sum = 0; int c0; for (c0 = n; c0 > 0; c0--) {
       int c1 = m;
       for (; c1 > 0; c1--) {
         sum += c0 > c1 ? 1 : 0;
       } 
     } 
     return sum;
   }
   ```

2. Convert the C code into LLVM IR (.ll)

   ```shell
   $ clang –O0 –S –emit-llvm sample.c –o sample.ll
   ```

3. Run the new pass with the opt tool

   ```shell
   $ opt -load (path_to_.so_file)/FuncBlockCount.so -funcblockcount sample.ll
   ```

   The output should look like:

   ```shell
   Function foo
   ```

   ??? <http://llvm.org/docs/WritingAnLLVMPass.html#pass-classes-and-requirements>

## Using another pass in a new pass

Counts the number of basic blocks in the IR. 

```c++
...
// Go over the loop to count the basic blocks inside it. It counts only the basic blocks in the outermost loop. To get information on the innermost loop, recursive calling of the getSubLoops function will help. 
void countBlocksInLoop(Loop *L, unsigned nest) {
  // Call the LoopInfo pass to get information on the loop.
  unsigned num_Blocks = 0; 
  Loop::block_iterator bb; 
  for(bb = L->block_begin(); bb != L->block_end();++bb) 
    num_Blocks++; errs() << "Loop level " << nest << " has " << num_Blocks << " blocks\n";  
  std::vector<Loop*> subLoops = L->getSubLoops(); 
  Loop::iterator j, f; 
  for (j = subLoops.begin(), f = subLoops.end(); j != f; ++j) 
    countBlocksInLoop(*j, nest + 1); 
}

virtual bool runOnFunction(Function &F) { 
  // The getAnalysis function is used to specify which other pass will be used: 
  LoopInfo *LI = &getAnalysis<LoopInfoWrapperPass>(). getLoopInfo(); // newly added
  errs() << "Function " << F.getName() + "\n"; 
  for (Loop *L : *LI) countBlocksInLoop(L, 0); 
  return false; 
}
```

## Registering a pass with pass manager

The pass we create previous was a dynamic object that was run indelendently. The opt tool consists of a pipeline of such passes that are registered with the pass manager, and a part of LLVM.

> The Passmanager class takes a list of passes, ensures that theire prerequisites are set up correctly, and then schedules the passes to run efficiently.
>
> - Shares the analysis results to avoid recomputing analysis results as much as possible
> - Pipelines the execution of passes to the program to get better cache and memory usage behavior out of a series of passes by pipelining the passes together

1. Modify the **FunBlockCount.cpp** file:

```c++
// Define a DEBUG_TYPE macro, specifying the debugging name in the FuncBlockCount.cpp file
#define DEBUG_TYPE "func-block-count"
// Specify the getAnalysisUsage syntax in the FuncBlockCount struct
void getAnalysisUsage(AnalysisUsage &AU) const override {
  AU.addRequired<LoopInfoWrapperPass>(); 
}
// Initialize the macros for initialization of the new pass
INITIALIZE_PASS_BEGIN(FuncBlockCount, " funcblockcount ", "Function Block Count", false, false) INITIALIZE_PASS_DEPENDENCY(LoopInfoWrapperPass)
INITIALIZE_PASS_END(FuncBlockCount, "funcblockcount", "Function Block Count", false, false)

Pass *llvm::createFuncBlockCountPass() { return new FuncBlockCount(); }
```

2. Add the createFuncBlockCount pass function in the **LinkAllPasses.h** file:

```c++
(void) llvm:: createFuncBlockCountPass ();
```

3. Add declaration to the **Scalar.h** file (include/llvm/Transforms):

```c++
Pass * createFuncBlockCountPass ();
```

4. Modify the constructor of the pass:

```c++
FuncBlockCount() : FunctionPass(ID) {initializeFuncBlockCount Pass (*PassRegistry::getPassRegistry());}
```

5. Add initialization pass entry in the **Scalar.cpp** file (lib/Transforms/Scalar):

```c++
initializeFuncBlockCountPass (Registry);
```

6. Add the initialization declaration to the InitializaePasses.h file (include/llvm):

```c++
void initializeFuncBlockCountPass (Registry);
```

7. Add the FuncBlockCount.cpp filename to the CMakeLists.txt file (lib/Transfoms/Scalar):

```c++
FuncBlockCount.cpp
```

Compile the LLVM with cmake command as specified in Chapter 1. Then this pass can be run in isolation from the command line:

```shell
$ opt –funcblockcount sample.ll
```

Pass Manager: <http://llvm.org/viewvc/llvm-project/llvm/trunk/lib/Transforms/Scalar/LoopInstSimplify.cpp>

## Writing an analysis pass

The results after the analysis pass provides can be used by another analysis pass to compute its result. This section will write an analysis paaes that counts and outputs the number of opcodes used in a function.

1. The example C code should be transformed into a .bc file, which will be used as the input to the analysis pass:

```shell
$ clang -c -emit-llvm testcode.c -o testcode.bc
```

2. Create a new folder to store the source code of our new analysis passes and make the necessary Makefile changes so that this pass can be compiled.

```c++
llvm_root_dir/lib/Transforms/opcodeCounter
```

3. Now starts writing the source code:

```c++
// Include the necessary header files and use the llvm namespace
#define DEBUG_TYPE "opcodeCounter" 
#include "llvm/Pass.h" 
#include "llvm/IR/Function.h" 
#include "llvm/Support/raw_ostream.h" 
#include <map> 
using namespace llvm;
// Create the structure defining the pass
namespace {
  struct CountOpcode: public FunctionPass {
    // Create the necessary data structures to count the number of opcodes and to denote the pass ID of the pass:
    std::map< std::string, int> opcodeCounter; // The opcodeCounter funtion keeps a count of every opcode that has been used in the function
    static char ID; 
    CountOpcode () : FunctionPass(ID) {}
    // Code for the actual implementation of the pass, overloading the runOnFunction function
    
    virtual bool runOnFunction (Function &F) { 
      llvm::outs() << "Function " << F.getName () << '\n';
      // The following loops collect the opcodes from all the functions.
      // The first loop iterates over all basic blocks present int the function. It collects the opcodes and their numbers
      for ( Function::iterator bb = F.begin(), e = F.end(); bb != e; ++bb) { 
        // The second loop iterates over all the instructions present in the basic block. It is meant for printing the results.
        for ( BasicBlock::iterator i = bb->begin(), e = bb->end(); i!= e; ++i) {
          if(opcodeCounter.find(i->getOpcodeName()) == opcodeCounter.end()) {
            opcodeCounter[i->getOpcodeName()] = 1; 
          } else { 
            opcodeCounter[i->getOpcodeName()] += 1; 
          } 
        } 
      }
      std::map< std::string, int>::iterator i = opcodeCounter.begin(); 
      std::map< std::string, int>::iterator e = opcodeCounter.end(); 
      // It iterates the over the map to print the pair of the opcode name and its number in the function.
      while (i != e) {
        llvm::outs() << i->first << ": " << i->second << "\n";
        i++; 
      } 
      llvm::outs() << "\n"; 
      opcodeCounter.clear(); 
      return false; // False means we are not modifying anything in the test code.
    } 
  }; 
}
// Register the pass
char CountOpcode::ID = 0;
static RegisterPass<CountOpcode> X("opcodeCounter", "Count number of opcode in a functions");
```

4. Compile the pass using the make or cmake command.

5. Run the pass on the test code using the opt tool to get the information on the number of opcodes present in the function:

```shell
$ opt -load path-to-build-folder/lib/LLVMCountopcodes.so -opcodeCounter -disable-output testcode.bc 
```

> This analysis pass works on a function level, funning once for each function in the program. Hence, we have inherited the FunctionPass function when declaring the **CountOpCodes : public FunctionPass** struct.

## Writing an alias analysis pass

Two passes point to the same location, or further optimizations, such as common subexpression elimination. Use the same testcode.c file as the example.

> Make the necessary Makefile changes, make changes to register the pass by adding entries for the pass in ***llvm/lib/Analysis/Analysis.cpp***, ***llvm/include/llvm/ InitializePasses.h***, ***llvm/include/llvm/LinkAllPasses.h***, ***llvm/include/ llvm/Analysis/Passes.h*** and create a file in ***llvm_source_dir/lib/Analysis/named EverythingMustAlias.cpp*** that will contain the source code for our pass.

Now writing alias pass.

```c++
// Header files
#include "llvm/Pass.h" 
#include "llvm/Analysis/AliasAnalysis.h" 
#include "llvm/IR/DataLayout.h" 
#include "llvm/IR/LLVMContext.h" 
#include "llvm/IR/Module.h" 
using namespace llvm;
// Create a structure for our pass by inheriting the ImmutablePass and AliasAnalysis classes
namespace { 
  // AliasAnalysis class gives the interface that the various alias analysis implementations should support. It exports the AliasResult and ModRefResult enums, representing the results of the alias and modref query respectively.
  // The getModRefInfo method returns the information on whether the execution of an instruction can read or modify a memory location. The pass in the preceding example works by returning the value MustAlias for every set of two pointers, as we have implemented it that way. Here, we have inherited the ImmutablePasses class, which suits our pass, as it is a very basic pass. We have inherited the AliasAnalysis pass, which provides the interface for our implementation.
  struct EverythingMustAlias : public ImmutablePass, public AliasAnalysis {
    // Declare the data structures and constructor:
    static char ID; 
    EverythingMustAlias() : ImmutablePass(ID) {
      initializeEverythingMustAliasPass(*PassRegistry::getPassRegist ry());
    }
    // Implement the getAdjustedAnalysisPointer function:
    // The getAdjustedAnalysisPointer function is used when a pass implements an analysis interface through multiple inheritance. If needed, it should override this to adjust the pointer as required for the specified pass information.
    void *getAdjustedAnalysisPointer(const void *ID) override {
      if (ID == &AliasAnalysis::ID)
        return (AliasAnalysis*)this; 
      return this;
    }
    // Implement the initializePass function to initialize the pass:
    // The initializePass function is used to initialize the pass that contains the InitializeAliasAnalysis method, which should contain the actual implementation of the alias analysis.
    bool doInitialization(Module &M) override {
      DL = &M.getDataLayout();
      return true;
    }
    // Implement the alias function:
    // The getAnalysisUsage method is used to declare any dependency on other passes by explicitly calling the AliasAnalysis::getAnalysisUsage method.
    void *getAdjustedAnalysisPointer(const void *ID) override {
      if (ID == &AliasAnalysis::ID)
        return (AliasAnalysis*)this; 
      return this;
    }
  }; 
}
// Register the pass
char EverythingMustAlias::ID = 0; 
INITIALIZE_AG_PASS(EverythingMustAlias, AliasAnalysis, "must-aa", "Everything Alias (always returns 'must' alias)", true, true, true)

ImmutablePass *llvm::createEverythingMustAliasPass() { return new EverythingMustAlias(); }
```

Compile the pass using the cmake or make command

Execute the test code using the .so file that is formed after acompiling the pass:

```shell
$ opt -must-aa -aa-eval -disable-output testcode.bc
===== Alias Analysis Evaluator Report ===== 
	10 Total Alias Queries Performed 
	0 no alias responses (0.0%) 
	0 may alias responses (0.0%) 
	0 partial alias responses (0.0%) 
	10 must alias responses (100.0%) 
	Alias Analysis Evaluator Pointer Alias Summary: 0%/0%/0%/100% 
	Alias Analysis Mod/Ref Evaluator Summary: no mod/ref!
```

> The alias method is used to check whether two memory objects are pointing to the same location or not. It takes two memory objects as the input and returns MustAlias, PartialAlias, MayAlias, or NoAlias as appropriate. <http://llvm.org/docs/AliasAnalysis.html.>

## Using other analysis passes

We will look into passes that have already been implemented in LLVM, and how we can use them for our purpose.

1. Create the test code.

```shell
$ cat testcode1.c
void func() { 
	int i; 
	char C[2]; 
	char A[10];
	for(i = 0; i != 10; ++i) {
		((short*)C)[0] = A[i];
		C[1] = A[9-i];
	} 
}
$ clang -c -emit-llvm testcode1.c -o testcode1.bc
```

2. Use the alias analysis evaluator pass by passing –aa-eval as a command-line option to the opt tool:

>  It iterates through all pairs of pointers in the function and queries whether the two are aliases of each other ot not.

```shell
$ opt -aa-eval -disable-output testcode1.bc
```

![image-20200611181817908](/Users/tancy/Library/Application Support/typora-user-images/image-20200611181817908.png)

3. Print the dominator tree information using the –print-dom-info command-line option along with opt

>  The pass for printing the dominator tree is run, through which information about the dominator tree can be obtained.

```shell
$ opt -print-dom-info -disable-output testcode1.bc
```

![image-20200611181931388](/Users/tancy/Library/Application Support/typora-user-images/image-20200611181931388.png)

4. Count the number of queries made by one pass to another using the –count-aa command-line option along with opt

> The count-aa command option counts the number of queries made by the licm pass to the basicaa pass. This information is obtained by the count alias analysis pass using the opt tool.

```shell
$ opt -count-aa -basicaa -licm -disable-output testcode1.bc
```

llvm4.0 does not have -count-aa

5. Print the alias sets in a program using the -print-alias-sets command-line option with opt:

> It prints the alias sets obtained after analyzing with the basicaa pass.

```shell
$ opt -basicaa -print-alias-sets -disable-output testcode1.bc
```

![image-20200611182355300](/Users/tancy/Library/Application Support/typora-user-images/image-20200611182355300.png)

<http://llvm.org/docs/Passes.html#analysis-passes>

# Chap5: Implementing Optimizations

The passes we create in Chapter4 just read the source code and gave us information about it. This chapter will go futher and write transformation passes that will actually change the source code, trying to optimize it for the faster execution of code.

## Writing a dead code elimination pass

Dead code elimination means removing the code that has no effect whatsoever on the results that the source program outputs on executing.

Aggressive dead code elimination: assumes every piece of code to be dead until proven otherwise. The source code still stores in the lib/Transform/Scalar folder.

1. Create the test code:

In this code, strlen function is called but the return value is not used.

```shell
$ cat testcode.ll 
declare i32 @strlen(i8*) readonly nounwind 
define void @test() {
	call i32 @strlen( i8* null )
	ret void 
}
```

2. Preparation for the pass

- Modify the InitializaPasses.h file (/llvm/)

```c++
namespace llvm {
  ...
  void initializeMYADCEPass(PassRegistry&);	// Add this line
```

- Modify the scalar.h file located at include/llvm-c/scalar.h/Transform/

```c++
// add the entry for the pass
void LLVMAddMYAggressiveDCEPass(LLVMPassManagerRef PM);
```

- Modify the scalar.h file located at include/llvm/Transform/

```c++
// Add the entry for the pass in the llvm namespace
FunctionPass *createMYAggressiveDCEPass();
```

- In the lib/Transforms/Scalar/scalar.cpp file, add the entry for the pass in two places. In the void ***llvm::initializeScalarOpts(PassRegistry &Registry)*** function, add the following code:

```c++
initializeMergedLoadStoreMotionPass(Registry); // already present in the file
initializeMYADCEPass(Registry); // add this line 
initializeNaryReassociatePass(Registry); // already present in the file
...
void LLVMAddMemCpyOptPass(LLVMPassManagerRef PM) { 
  unwrap(PM)->add(createMemCpyOptPass()); 
}

// add the following three lines 
void LLVMAddMYAggressiveDCEPass(LLVMPassManagerRef PM) { 
  unwrap(PM)->add(createMYAggressiveDCEPass()); 
}

void LLVMAddPartiallyInlineLibCallsPass(LLVMPassManagerRef PM) { 
  unwrap(PM)->add(createPartiallyInlineLibCallsPass()); 
} 
...
```

3. Write the pass.  

```c++
// header files
#include "llvm/Transforms/Scalar.h" 
#include "llvm/ADT/DepthFirstIterator.h" 
#include "llvm/ADT/SmallPtrSet.h" 
#include "llvm/ADT/SmallVector.h" 
#include "llvm/ADT/Statistic.h" 
#include "llvm/IR/BasicBlock.h" 
#include "llvm/IR/CFG.h" 
#include "llvm/IR/InstIterator.h" 
#include "llvm/IR/Instructions.h" 
#include "llvm/IR/IntrinsicInst.h" 
#include "llvm/Pass.h" 
using namespace llvm;
// Declare the structure of the pass
namespace { 
  struct MYADCE : public FunctionPass { 
    static char ID; // Pass identification, replacement for typeid 
    MYADCE() : FunctionPass(ID) { 
      initializeMYADCEPass(*PassRegistry::getPassRegistry()); 
    }
    bool runOnFunction(Function& F) override;
    void getAnalysisUsage(AnalysisUsage& AU) const override { 
      AU.setPreservesCFG(); 
    } 
  };
}
// Initialize the pass and its ID
char MYADCE::ID = 0; 
INITIALIZE_PASS(MYADCE, "myadce", "My Aggressive Dead Code Elimination", false, false)
// Implement the actual pass in the runOnFunction
// First collecting a list of all the root instructions that are live in the first for loop of the runOnFunction function.
bool MYADCE::runOnFunction(Function& F) { 
  if (skipOptnoneFunction(F)) 
    return false;
  SmallPtrSet<Instruction*, 128> Alive; 
  SmallVector<Instruction*, 128> Worklist;
  
  // Collect the set of "root" instructions that are known live.
  for (Instruction &I : inst_range(F)) { 
    if (isa<TerminatorInst>(I) || isa<DbgInfoIntrinsic>(I) || isa<LandingPadInst>(I) || I.mayHaveSideEffects()) { 
      Alive.insert(&I); 
      Worklist.push_back(&I); 
    } 
  }
  // Propagate liveness backwards to operands. 
  while (!Worklist.empty()) {
    Instruction *Curr = Worklist.pop_back_val(); 
    for (Use &OI : Curr->operands()) {
      if (Instruction *Inst = dyn_cast<Instruction>(OI)) 
        if (Alive.insert(Inst).second) 
          Worklist.push_back(Inst);
    }
  }
  // the instructions which are not in live set are considered dead in this pass. The instructions which do not effect the control flow, return value and do not have any side effects are hence deleted.
  for (Instruction &I : inst_range(F)) { 
    if (!Alive.count(&I)) { 
      Worklist.push_back(&I); 
      I.dropAllReferences(); 
    } 
  }
  for (Instruction *&I : Worklist) { 
    I->eraseFromParent(); 
  }
  return !Worklist.empty();
} 

FunctionPass *llvm::createMYAggressiveDCEPass() { return new MYADCE(); }
```

4. Run the preceding pass after compiling the testcode.ll file

```shell
$ opt -myadce -S testcode.ll

; ModuleID = 'testcode.ll'
; Function Attrs: nounwind readonly 
declare i32 @strlen(i8*) #0

define void @test() { 
	ret void 
}
```

>  More dead code elimination method, check the llvm/lib/Transfroms/Scalar folder, where the code for other kinds of DCEs is present.

## Writing an inlining transformation pass

> The compiler takes the decision whether to inline a function or not. In this recipe, you will learn to how to write a simple function-inlining pass that makes use of the implementation in LLVM for inlining. We will write a pass that will handle the functions marked with the **alwaysinline** attribute.

1. Get ready: Make the necessary changes in the ***lib/Transforms/IPO/IPO.cpp*** and ***include/llvm/InitializePasses.h*** files, the ***include/llvm/Transforms/IPO.h*** file, and the ***/include/llvm-c/Transforms/IPO.h*** file to include the following pass. Also make the necessary makefile changes to include this pass.

   ```shell
   $ cat testcode.c 
   # the alwaysinline attribute declares that the pass will always inline such functions
   define i32 @inner1() alwaysinline { 
   	ret i32 1 
   }
   
   define i32 @outer1() { 
   	%r = call i32 @inner1() 
   	ret i32 %r 
   }
   ```

2. Write the pass

```c++
// Header files
#include "llvm/Transforms/IPO.h" 
#include "llvm/ADT/SmallPtrSet.h" 
#include "llvm/Analysis/AliasAnalysis.h" 
#include "llvm/Analysis/AssumptionCache.h" 
#include "llvm/Analysis/CallGraph.h" 
#include "llvm/Analysis/InlineCost.h" 
#include "llvm/IR/CallSite.h" 
#include "llvm/IR/CallingConv.h" 
#include "llvm/IR/DataLayout.h" 
#include "llvm/IR/Instructions.h" 
#include "llvm/IR/IntrinsicInst.h" 
#include "llvm/IR/Module.h" 
#include "llvm/IR/Type.h" 
#include "llvm/Transforms/IPO/InlinerPass.h"

using namespace llvm;
// Describe the class
namespace {
  class MyInliner : public Inliner { 
    InlineCostAnalysis *ICA;
    public:
    MyInliner() : Inliner(ID, -2000000000, /*InsertLifetime*/ true), ICA(nullptr) {
      initializeMyInlinerPass(*PassRegistry::getPassRegistry());
    }
    MyInliner(bool InsertLifetime) : Inliner(ID, -2000000000, InsertLifetime), ICA(nullptr) { 
      initializeMyInlinerPass(*PassRegistry::getPassRegistry());
    }
    static char ID;
    // Main function at work here. 
    InlineCost getInlineCost(CallSite CS) override;
    void getAnalysisUsage(AnalysisUsage &AU) const override; bool runOnSCC(CallGraphSCC &SCC) override;
    using llvm::Pass::doFinalization; bool doFinalization(CallGraph &CG) override { 
      return removeDeadFunctions(CG, /*AlwaysInlineOnly=*/ true); 
    } 
  };
}
// Initialize the pass and add the dependencies
char MyInliner::ID = 0; 
INITIALIZE_PASS_BEGIN(MyInliner, "my-inline", "Inliner for always_inline functions", false, false) 
INITIALIZE_AG_DEPENDENCY(AliasAnalysis) INITIALIZE_PASS_DEPENDENCY(AssumptionTracker) INITIALIZE_PASS_DEPENDENCY(CallGraphWrapperPass) INITIALIZE_PASS_DEPENDENCY(InlineCostAnalysis) INITIALIZE_PASS_END(MyInliner, "my-inline", "Inliner for always_inline functions", false, false)

Pass *llvm::createMyInlinerPass() { return new MyInliner(); }
Pass *llvm::createMynlinerPass(bool InsertLifetime) { return new MyInliner(InsertLifetime); }
// Implement the function to get the inlining cost, getInliineCost function was overrided.
InlineCost MyInliner::getInlineCost(CallSite CS) { 
  Function *Callee = CS.getCalledFunction(); 
  if (Callee && !Callee->isDeclaration() && CS.hasFnAttr(Attribute::AlwaysInline) && ICA->isInlineViable(*Callee)) 
    return InlineCost::getAlways();	// If the functions maeked with the alwaysline attribute
  
  return InlineCost::getNever();	// others
}
// Write the other helper methods
bool MyInliner::runOnSCC(CallGraphSCC &SCC) { 
  ICA = &getAnalysis<InlineCostAnalysis>(); 
  return Inliner::runOnSCC(SCC); 
}

void MyInliner::getAnalysisUsage(AnalysisUsage &AU) const {
  AU.addRequired<InlineCostAnalysis>(); 
  Inliner::getAnalysisUsage(AU); 
}
```

3. Compile the pass. After compiling, run it on the preceding test case

```shell
$ opt -inline-threshold=0 -always-inline -S test.ll

; ModuleID = 'test.ll'

; Function Attrs: alwaysinline 
define i32 @inner1() #0 {
	ret i32 1 
} 
define i32 @outer1() {
	ret i32 1 
}
```

The call of inner1 function is replaced by its actual function body.

## Pass for memory optimization

A transformation pass that deals with memory optimization. **memcpyopt**

```shell
$ opt -memcpyopt -S memcopytest.ll
```

![image-20200611191351759](/Users/tancy/Library/Application Support/typora-user-images/image-20200611191351759.png)

The Memcpyopt pass deals with eliminating the memcpy calls wherever possible, or transforms them into other calls.

```c++
call void @llvm.memcpy.p0i8.p0i8.i64(i8* %arr_i8, i8* bitcast ([3 x i32]* @cst to i8*), i64 12, i32 4, i1 false)
// the pass converts the memcpy into a memset call
call void @llvm.memset.p0i8.i64(i8* %arr_i8, i8 -1, i64 12, i32 4, i1 false)
```

llvm/lib/Transforms/Scalar/MemCpyOptimizer.cpp: tryMergingIntoMemset function

> The tryMergingIntoMemset function looks for some other pattern to fold away when scanning forward over instructions. It looks for stores in the neighboring memory and, on seeing consecutive ones, it attempts to merge them together into memset.
>
> The processMemSet function looks out for any other neighboring memset to this memset, which helps us widen out the memset call to create a single larger store.

More memory optimization passes: <http://llvm.org/docs/Passes.html#memcpyopt-memcpy-optimization>

## Combining LLVM IR

Instruction combining in LLVM. The pass will handle transformations involving the AND, OR, and XOR operators.

1. Test code

```c++
define i32 @test19(i32 %x, i32 %y, i32 %z) { 
  %xor1 = xor i32 %y, %z
  %or = or i32 %x, %xor1 
  %xor2 = xor i32 %x, %z 
  %xor3 = xor i32 %xor2, %y 
  %res = xor i32 %or, %xor3 
  ret i32 %res 
}
```

2. Modify lib/Transforms/InstCombine/InstCombineAndOrXor.cpp

```c++
// In the InstCombiner::visitXor(BinaryOperator &I) function, go to the if condition—if (Op0I && Op1I)—and add this:
if (match(Op0I, m_Or(m_Xor(m_Value(B), m_Value(C)), m_Value(A))) && match(Op1I, m_Xor( m_Xor(m_Specific(A), m_Specific(C)), m_Specific(B)))) {
  // If matches the pattern, return the reduced values after building a new instruction
  return BinaryOperator::CreateAnd(A, Builder>CreateXor(B,C)); 
}
```

3. Build the LLVM again, then run this pass

```shell
$ opt –instcombine –S testcode.ll 
define i32 @test19(i32 %x, i32 %y, i32 %z) { 
	%1 = xor i32 %y, %z
	%res = and i32 %1, %x
	ret i32 %res 
}
```

More in lib/Transforms/InstCombine

## Transforming and optimizing loops

Loop-Invariant Code Motion (LICM) optimization

Loop deletion: eliminate loops with non-infinite, computable trip counts that have no side effects on a function's return value.

```c
$ cat testlicm.ll 
define void @testfunc(i32 %i) {  							; <label>:0 
	br label %Loop 
	Loop: 																			; preds = %Loop, %0
	
	%j = phi i32 [ 0, %0 ], [ %Next, %Loop ]		; <i32>
	[#uses=1] 
	%i2 = mul i32 %i, 17 												; <i32> [#uses=1]
	%Next = add i32 %j, %i2 										; <i32> [#uses=2]
	%cond = icmp eq i32 %Next, 0 								; <i1> [#uses=1]
	br i1 %cond, label %Out, label %Loop 
	Out: 																				; preds = %Loop 
	ret void 
}

$ opt licmtest.ll -licm -S
; ModuleID = 'licmtest.ll'

define void @testfunc(i32 %i) { 
  %i2 = mul i32 %i, 17 
  br label %Loop

Loop: 																				; preds = %Loop, %0
	%j = phi i32 [ 0, %0 ], [ %Next, %Loop ]
  %Next = add i32 %j, %i2 
  %cond = icmp eq i32 %Next, 0 
  br i1 %cond, label %Out, label %Loop

Out:																					; preds = %Loop
	ret void 
}

$ cat deletetest.ll
define void @foo(i64 %n, i64 %m) nounwind { 
entry:
  br label %bb

bb:
  %x.0 = phi i64 [ 0, %entry ], [ %t0, %bb2 ]
	%t0 = add i64 %x.0, 1 
  %t1 = icmp slt i64 %x.0, %n 
  br i1 %t1, label %bb2, label %return 
bb2:
	%t2 = icmp slt i64 %x.0, %m 
  br i1 %t1, label %bb, label %return

return:
  ret void 
}

$ opt deletetest.ll -loop-deletion -S
; ModuleID = "deletetest.ll'

; Function Attrs: nounwind 
define void @foo(i64 %n, i64 %m) #0 { 
entry:
	br label %return

return: 
  %entry ret void 
}

attributes #0 = { nounwind }
```



> The LICM pass performs loop-invariant code motion; it tries to move the code that is not modified in the loop out of the loop. It can go either above the loop in the pre-header block, or after the loop exits from the exit block.

## Reassociating expressions

> In the preceding example, we used the inverse property to eliminate patterns such as "X + ~X" -> "-1" using reassociation.

![image-20200611193802263](/Users/tancy/Library/Application Support/typora-user-images/image-20200611193802263.png)

lib/Transforms/Scalar/Reassociate.cpp

## Vectorizing IR

Vectorize code to excute an instruction on multiple datasets in one go.

>  Two types of vectorization in LLVM - Superword-Level Parallelism (SLP) and loop vectorization. Loop vectorization deals with vectorization opportunities in a loop, while SLP vectorization deals with vectorizing straight-line code in a basic block. In this recipe, we will see how straight-line code is vectorized.

## Other optimization passes

strip-debug-symbols pass: strips off the debug symbols from the test code.

prune-eh pass: remove unused exception information

```shell
$ opt -strip-debug teststripdebug.ll -S
$ opt -prune-eh -S simpletest.ll
```

Other transformation passes: <http://llvm.org/docs/Passes.html#transform-passes>

# Chapter 6: Target-independent Code Genrator

>  After optimizing the LLVM IR, it needs to be converted into machine instructions for excution. The machine-independent code generator interface gives an abstract layer that helps convert IR into machine instructions. In this phase, the IR is converted into SelectionDAG (DAG stands for Directed Acyclic Graph).

## The life of an LLVM IR instruction

> LLVM  uses the SelectionDAG approach to convert the IR into machine instructions. The Linear IR is converted into SelectionDAG, a DAG that represents instructions as nodes.
>
> - The SelectionDAG is created out of LLVM IR
> - Legalizing SDAG nodes
> - DAG combine optimization
> - Instruction selection from the target instruction
> - Scheduling and emitting a machine instruction
> - Register allocation—SSA destruction, register assignment, and register spilling
> - Emitting code

1. Convert the front end language example to LLVM IR.

```c++
int test (int a, int b, int c) {
  return c/(a+b);
}
```

```c++
// LLVM IR code
define i32 @test(i32 %a, i32 %b, i32 %c) { 
  %add = add nsw i32 %a, %b 
  %div = sdiv i32 %add, %c 
  return i32 %div 
}
```

2. IR optimization

> The IR, in the transformation phase, goes through the InstCombiner::visitSDiv() function in the InstCombine pass. In that function, it also goes through the SimplifySDivInst() function and tries to check whether an opportunity exists to further simplify the instruction.

3. LLVM IR to SelectionDAG

> After the IR transformations and optimizations are over, the LLVM IR instruction passes through a Selection DAG node incarnation. Selection DAG nodes are created by the SelectionDAGBuilder class. The SelectionDAGBuilder::visit() function call from the SelectionDAGISel class visits each IR instruction for creating an SDAGNode node.
>
> The method that handles an SDiv instruction is SelectionDAGBuilder::visitSDiv. It requests a new SDNode node from the DAG with theISD::SDIV opcode, which then becomes a node in the DAG.

4. SelectionDAG legalization

The SelectionDAG node created may not be supported by the target architecture (called illegal if the nodes are unsupported). 

> The legalization of SDNode involves type and operation legalization. The target-specific information is conveyed to the target-independent algorithms via an interface called TargetLowering. This interface is implemented by the target and, describes how LLVM IR instructions should be lowered to legal SelectionDAG operations.

5. Conversion from tartget-independent DAG to machine DAG (SDNode --> MachineSDNode)

.td -> .inc

6. Scheduling instructions

Convert a DAG into a linear set of instructions.

> Since each target has its own set of registers and customized pipelining of the instructions, each target has its own hook for scheduling and calculating heuristics to produce optimized, faster code. After calculating the best possible way to arrange instructions, the scheduler emits the machine instructions in the machine basic block, and finally destroys the DAG.

7. Register allocation

There are unlimited virtual registers in LLVM IR, but the number of registers in machine is infinite.

Register allocation algorithms: liveness of variables and live interval analysis is importatnt.

An interference graph is created by analyzing liveness, and a graph coloring algorithm can be used to allocate the registers.

LLVM employs a greedy approach for register allocation, where variables that have large live ranges are allocated registers first.

8. Code emission

LLVM emit the code in two ways; the first is JIT, which directly emits the code to the memory. The second way is by using the MC framework to emit assembly and object files for all backend targets.

> The LLVMTargetMachine::addPassesToEmitFile function is responsible for defining the sequence of actions required to emit an object file. The actual MI-to-MCInst translation is done in the EmitInstruction function of the AsmPrinter interface. The static compiler tool, llc, generates assembly instructions for a target. Object file (or assembly code) emission is done by implementing the MCStreamer interface.

## Visualizing LLVM IR CFG using GraphViz

Visualizing the LLVM IR control flow graph.

Install the graphviz

```shell
$ sudo apt-add-repository ppa:dperry/ppa-graphviz-test
$ sudo apt-get update
$ sudo apt-get install graphviz
```

If you get the graphviz : Depends: libgraphviz4 (>= 2.18) but it is not going to be installed error, run the following commands:

```shell
$ sudo apt-get remove libcdt4 
$ sudo apt-get remove libpathplan4
$ sudo apt-get install graphviz
```

Create example code to draw the graph

```c++
// test.ll
define i32 @test(i32 %a, i32 %b, i32 %c) {
	%add = add nsw i32 %a, %b
	%div = sdiv i32 %add, %c
	ret i32 %div 
}
```

Display DAG after it is built, before optimization:

```shell
$ llc -view-dag-combine1-dags test.ll
Writing 'tmp/dag._xxx.dot'... done
Trying 'xdg-open' program... Remember to erase graph file: /tmp/dag._xxx.dot

$ dot -Tpng /tmp/dag._xxx.dat > test.png
```

Display the DAG defore legalization:

```shell
$ llc -view-legalize-dags test.ll
```

Display the DAG before the second optimization pass

```shell
$ llc -view-dag-combine2-dags test.ll
```

Display the DAG beform the selection phase:

```shell
$ llc -view-isel-dags test.ll
```

Display the DAG before scheduling:

```shell
$ llc -view-sched-dags test.ll
```

Display the scheduler's dependency graph:

```shell
$ llc -view-sunit-dags test.ll
```

view graphs in debug mode: <http://llvm.org/docs/ProgrammersManual.html#viewing-graphs-while-debugging-code>

## Describing targets using TableGen

> TableGen is a tool for backend developers that describes their target machine with a declarative language-*.td. The *.td files will be converted to enums, DAG-pattern matching functions, instruction encoding/decoding functions, and so on, which can then be used in other C++ files for coding.
>
> To define registers and the register set in the target description's .td files, tablegen will convert the intended .td file into .inc files, which will be #include syntax in our .cpp files referring to the registers.



> Assuming the sample target machine has four registers, r0-r3; a stack register, sp; and a link register, lr. These can be specified in the SAMPLERegisterInfo.td file. TableGen provides the Register class, which can be extended to specify registers.

```shell
# create a new folder in lib/Target named SAMPLE
$ mkdir llvm_root_directory/lib/Target/SAMPLE
# Create a new file called SAMPLERegisterInfo.td in the new SAMPLE folder:
$ cd llvm_root_directory/lib/Target/SAMPLE 
$ vi SAMPLERegisterInfo.td
```

Define the hardware encoding , namespace, registers, and register class:

```xml
class SAMPLEReg<bits<16> Enc, string n> : Register<n> { 
  let HWEncoding = Enc; 
  let Namespace = "SAMPLE"; 
}
foreach i = 0-3 in {
	def R#i : R<i, "r"#i >;
}
def SP : SAMPLEReg<13, "sp">;
def LR : SAMPLEReg<14, "lr">;
def GRRegs : RegisterClass<"SAMPLE", [i32], 32, (add R0, R1, R2, R3, SP)>;
```

TableGen processes this .td file to generate the .inc files, which habe registers represented in the form of enums that can be used in the .cpp files. These .inc files will be generated when we build the LLVM project.

<X86RegisterInfo.td file located at llvm_source_ code/lib/Target/X86/>

## Defining an instruction set

How instruction sets are defined for the target architecture: operands, an assembly string, and an instruction pattern. 

```shell
# create a new file called SAMPLEInstrInfo.td in the lib/Target/SAMPLE folder
$ vi SAMPLEInstrInfo.td

def ADDrr : InstSAMPLE<(outs GRRegs:$dst), 
						(ins GRRegs:$src1, GRRegs:$src2), 
						"add $dst, $src1, $src2", 
						[(set i32:$dst, (add i32:$src1, i32:$src2))]>;
```

> The add register instruction specifies \$dst as the resultant operand, which belongs to the general register type class; the \$src1 and ​\$src2 inputs as two input operands, which also belong to the general register class; and the instruction assembly string as add ​\$dst, ​\$src1, ​\$src2, which is of the 32-bit integer type.

add r0, r0, r1

For more detailed information on various types of instruction sets for advanced architecture, such as the x86, refer to the X86InstrInfo.td file located at lib/Target/X86/

## Adding a machine code descriptor

Convert LLVM IR abstract blocks into machin-specific blocks. MachinFunction, MachinBasicBlock, and MachineInstr.

> Machine instructions are instances of the MachineInstr class. This class is an extremely abstract way of representing machine instructions. In particular, it only keeps track of an opcode number and a set of operands. The opcode number is a simple unsigned integer that has a meaning only for a specific backend.

MachinInstr.cpp

```c++
// MachinInstr constructor creates an object of MachineInstr class and adds the implicit operands. It reserves space for the number of operands specified by the MCInstrDesc class
MachineInstr::MachineInstr(MachineFunction &MF, const MCInstrDesc &tid, const DebugLoc dl, bool NoImp)
  : MCID(&tid), Parent(nullptr), Operands(nullptr), NumOperands(0), 
		Flags(0), AsmPrinterFlags(0), NumMemRefs(0), MemRefs(nullptr), debugLoc(dl) { 
      // Reserve space for the expected number of operands. 
    if (unsigned NumOps = MCID->getNumOperands() + MCID->getNumImplicitDefs() + MCID->getNumImplicitUses()) {
      CapOperands = OperandCapacity::get(NumOps);
      Operands = MF.allocateOperandArray(CapOperands); 
    }
    if (!NoImp) 
      addImplicitDefUseOperands(MF);
}

// addOperand function adds the specified operand to the instruction. If it is an implicit operand, it is added at the end of the operand list. If it is an explicit operand, it is added at the end of the explicit operand list.
void MachineInstr::addOperand(MachineFunction &MF, const MachineOperand &Op) { 
  assert(MCID && "Cannot add operands before providing an instr descriptor"); 
  if (&Op >= Operands && &Op < Operands + NumOperands) { 
    MachineOperand CopyOp(Op); 
    return addOperand(MF, CopyOp); 
  } 
  unsigned OpNo = getNumOperands(); 
  bool isImpReg = Op.isReg() && Op.isImplicit(); 
  if (!isImpReg && !isInlineAsm()) { 
    while (OpNo && Operands[OpNo-1].isReg() && Operands[OpNo1].isImplicit()) { 
      --OpNo; 
      assert(!Operands[OpNo].isTied() && "Cannot move tied operands"); 
    } 
  }
  #ifndef NDEBUG 
  bool isMetaDataOp = Op.getType() == MachineOperand::MO_Metadata; 
  assert((isImpReg || Op.isRegMask() || MCID->isVariadic() || OpNo < MCID->getNumOperands() || isMetaDataOp) && "Trying to add an operand to a machine instr that is already done!"); 		#endif
    
    MachineRegisterInfo *MRI = getRegInfo(); 
  OperandCapacity OldCap = CapOperands; 
  MachineOperand *OldOperands = Operands; 
  if (!OldOperands || OldCap.getSize() == getNumOperands()) { 
    CapOperands = OldOperands ? OldCap.getNext() : OldCap.get(1); 
    Operands = MF.allocateOperandArray(CapOperands); 
    if (OpNo) 
      moveOperands(Operands, OldOperands, OpNo, MRI); 
  } 
  if (OpNo != NumOperands) 
    moveOperands(Operands + OpNo + 1, OldOperands + OpNo, NumOperands - OpNo, MRI);
  ++NumOperands; 
  if (OldOperands != Operands && OldOperands) 
    MF.deallocateOperandArray(OldCap, OldOperands); 
  MachineOperand *NewMO = new (Operands + OpNo) MachineOperand(Op); 
  NewMO->ParentMI = this; 
  if (NewMO->isReg()) { 
    NewMO->Contents.Reg.Prev = nullptr; 
    NewMO->TiedTo = 0; 
    if (MRI) MRI->addRegOperandToUseList(NewMO); 
    if (!isImpReg) { 
      if (NewMO->isUse()) { 
        int DefIdx = MCID->getOperandConstraint(OpNo, MCOI::TIED_TO); 
        if (DefIdx != -1) 
          tieOperands(DefIdx, OpNo); 
      } 
      if (MCID->getOperandConstraint(OpNo, MCOI::EARLY_CLOBBER) != -1) 
        NewMO->setIsEarlyClobber(true); 
    } 
  } 
}

// addMemoperands function is defined to add the memory operands.
void MachineInstr::addMemOperand(MachineFunction &MF, MachineMemOperand *MO) { 
  mmo_iterator OldMemRefs = MemRefs; 
  unsigned OldNumMemRefs = NumMemRefs; 
  unsigned NewNum = NumMemRefs + 1; 
  mmo_iterator NewMemRefs = MF.allocateMemRefsArray(NewNum); 
  std::copy(OldMemRefs, OldMemRefs + OldNumMemRefs, NewMemRefs); 
  NewMemRefs[NewNum - 1] = MO; 
  setMemRefs(NewMemRefs, NewMemRefs + NewNum);		//setMemRefs function is the primary method for setting up a MachineInstr MemRefs list
}
```

Although the MachineIntr class provides machine-instruction-creating methods, a dedicated function called BuildMI(), based on the MachinInstrBuilder class, is more convenient.

## Implementing the MachineInstrBuilder class

BuildMI() is used to build machine instructions. <include/llvm/CodeGen/MachinInstrBuilder.h>

We can use BuildMI in code snippets for the  following purposes:

1. To create a DestReg = mov 42 (rendered in the x86 assembly as mov DestReg, 42) instruction:

   ```assembly
   MachineInstr *MI = BuildMI(X86::MOV32ri, 1, DestReg).addImm(42);
   ```

2. To create the same instruction, but insert it at the end of a basic block:

   ```assembly
   MachineBasicBlock &MBB = BuildMI(MBB, X86,::MOV32ri, 1, DestReg).addImm(42);
   ```

3. To create the same instruction, but insert it before a pecified iterator point:

   ```assembly
   MachineBasicBlock::iterator MBBI = BuildMI(MBB, MBBI, X86::MOV32ri, 1, DestReg).addImm(42)
   ```

4. To create a self-looping branch instruction:

   ```assembly
   BuildMI(MBB, X86::JNE, 1).addMBB(&MBB);
   ```

## Implementing the MachineBasicBlock class

> A MachineFunction class contain a series of MachineBasiBlocks classes. These MachineFunction classes map to LLVM IR functions that are given as input to the instruction selector. In addtition to a list of basic blocks, the MachineFucntion class contains the MachineConstantPool, MachineFrameInfro, MahcineFunctionInfo, and MachineRegisterInfo class.

- `RegInfo` keeps information about each register that is in use in the function: `MachineRegisterInfo *RegInfo;`

- `MachineFrameInfo` keeps track of objects allocated on the stack: `MachineFrameInfo *FrameInfo;`

- `ConstantPool` keeps track of constants that have been spilled to the memory: `MachineConstantPool *ConstantPool;`
- `JumpTableInfo` keeps track of jump tables for switch instructions: `MachineJumpTableInfo *JumpTableInfo;`

- The list of machine basic blocks in the function:

  `typedef ilist<MachineBasicBlock> BasicBlockListType; `

  `BasicBlockListType BasicBlocks;`

- The getFunction function returns the LLVM function that the current machine code represents: `const Function *getFunction() const { return Fn; }`

- CreateMachineInstr allocates a new MachineInstr class: `MachineInstr *CreateMachineInstr(const MCInstrDesc &MCID, DebugLoc DL, bool NoImp = false);`

>  The MachineFunction class primarily contains a list of MachineBasicBlock objects (typedef ilist<MachineBasicBlock> BasicBlockListType; BasicBlockListType BasicBlocks;), and defines various methods for retrieving information about the machine function and manipulating the objects in the basic blocks member.

<A detailed implementation of the MachineFunction class can be found in the MachineFunction.cpp file located at lib/Codegen/>

## Writing an instruction selector

> LLVM uses the SelectionDAG representation to represent the LLVM IR in a low-level data-dependence DAG for instruction selection. Various simplifications and target-specific optimizations can be applied to the SelectionDAG representation. This representation is target-independent. It is a significant, simple, and powerful representation used to implement IR lowering to target instructions.

The SelectionDAG class provides lots of target-independent methods to create SDNode of various kinds, and retrieves/computes useful information from the nodes in the SelectionDAG graph.



## Legalizing SelectionDAG

>  A selectionDAG representation is a target-independent representation of instructions and operands. However, a target may not always support the instruction or data type represented by SelectionDAG. In that sense, the initial SelectionDAG graph constructed can be called illegal. The DAG legalize phase converts the illegal DAG into a legal DAG supported by the target architecture.

Two ways to convert unsupported data types into supported data types: by promoting smaller data types to larger data types, or by truncating larger data types into smaller ones. i8, i15 to i32. i64 to two i32.

The SelectionDAGLegalize class consists of various data members, tracking data structures to keep a track of legalized nodes, and various methods that are used to operate on nodes to legalize them.

Type legalization and instruction legalization.

Type legalization:

```shell
$ cat test.ll 
define i64 @test(i64 %a, i64 %b, i64 %c) {
	%add = add nsw i64 %a, %b
	%div = sdiv i64 %add, %c
	ret i64 %div 
}
```

To view the DAG before type legalization,

```shell
$ llc -view-dag-combine1-dags test.ll
```

After type legalization:

```shell
$ llc -view-dag-combine2-dags test.ll
```

Instruction legalization:

```shell
$ cat test.ll 
define i32 @test(i32 %a, i32 %b, i32 %c) {
	%add = add nsw i32 %a, %b
	%div = sdiv i32 %add, %c
	ret i32 %div 
}
```

View the DAG before legalization:

```shell
$ llc –view-dag-combine1-dags test.ll
```

After legalization:

```shell
$ llc -view-dag-combine2-dags test.ll
```

## Optimizing SelectionDAG

A SelectionDAG representation shows data and instructions in the form of nodes. minimized SelectionDAG

DAGCombiner: some DAGCombine passes search for a pattern and then fold the patterns into a single DAG. This basically reduces the number of DAGs, while loweing DAGs. 

<For a more detailed implementation of the optimized SelectionDAG class, see the DAGCombiner.cpp file located at lib/CodeGen/SelectionDAG/>

## Selection instruction from the DAG

After legalization and DAG combination, the SelectionDAG representation is in the optimized phase. 

Input: target-independent DAG nodes, patterns (from the /td file)

Output: DAG nodes (target-specific)

`SelectionDAGISel` is the common base class used for pattern-matching instruction selectors that are based on SelectionDAG. It inherits the MachineFunctionPass class. It has various functions used to determine the legality and profitability of operations such as folding.

```c++
class SelectionDAGISel : public MachineFunctionPass {...}
```

The `TablGen` class helps select target-specific instructions.

The `CodeGenAndEmitDAG` function calls the `DoInstructionSelection` function, which visites each DAG node and calls the `Select` function for each node.

```c++
SDNode *ResNode = Select(Node);
```

The `Select` function is an abstract method implemented by the targets. The X86 target implements it in the `X86DAGToDAGISel::Select` function. The `X86DAGToDAGISel::Select()` function intercepts some nodes for manual matching, but delegates the bulk of the work to the `X86DAGToDAGISel::SelectCode()` function.

The `X86DAGToDAGISel::SelectCode` function is autogenerated by TableGen. It contains the matcher table, followed by a call to the generic `SelectionDAGISel::SelectCodeCommon()` function, passing it the table.

```shell
$ cat test.ll 
define i32 @test(i32 %a, i32 %b, i32 %c) {
	%add = add nsw i32 %a, %b
	%div = sdiv i32 %add, %c
	ret i32 %div 
}
```

<To see the detailed implementation of the instruction selection, take a look at the SelectionDAGISel.cpp file located at lib/CodeGen/SelectionDAG/>



## Scheduling instructions in SelectionDAG

SelectionDAG nodes consisting of target-supported instructions and operands. However, the code is still in DAG representation. The next step is to schedule the SelectionDAG nodes.

> A scheduler assigns the order of execution of instructions from the DAG. In this process, it takes into account various heuristics, such as register pressure, to optimize the execution order of instructions and to minimize latencies in instruction execution. After assigning the order of execution to the DAG nodes, the nodes are converted into a list of MachineInstrs and the SelectionDAG nodes are destroyed.

The ScheduleDAG class is a base class for other schedulers to inherit, and it provides only graph-related manipulation operations such as an iterator, DFS, topological sorting, functions for moving nodes around, and so on.

```c++
class ScheduleDAG { 
public:
	const TargetMachine &TM; 									// Target processor
  const TargetInstrInfo *TII; 							// Target instruction
  const TargetRegisterInfo *TRI; 						// Target processor register info 
  MachineFunction &MF; 											// Machine function	
  MachineRegisterInfo &MRI; 								// Virtual/real
  register map std::vector<SUnit> SUnits; 	// The scheduling
  units.SUnit EntrySU; 											// Special node for the region entry
	SUnit ExitSU; 														// Special node for the region exit

	explicit ScheduleDAG(MachineFunction &mf);

	virtual ~ScheduleDAG();
  ..
}
```

The SelectionDAG class takes into account various heuristics, such as register pressure, spilling cost, live interval analysis, and so on to determine the best possible scheduling of instructions.

<For a detailed implementation of scheduling instructions, see the ScheduleDAGSDNodes.cpp, ScheduleDAGSDNodes.h, ScheduleDAGRRList. cpp, ScheduleDAGFast.cpp, and ScheduleDAGVLIW.cpp files located in the lib/CodeGen/SelectionDAG folder>



