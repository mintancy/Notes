LLVM Cook Book: <chrome-extension://cdonnmffkdaoajfknoeeecmchibpmkmg/assets/pdf/web/viewer.html?file=https%3A%2F%2Forg.computer%2Fdist%2Fpdf%2Fllvm-cookbook.pdf>

Sample code: <https://github.com/elongbug/llvm-cookbook>

# Chapter 1

## Modular design

`opt`

Optimize the statement in functions, combining the instructions:

```shell
$ opt –S –instcombine testfile.ll –o output1.ll
```

Dead argument elimination optimization:

```shell
$ opt –S –deadargelim testfile.ll –o output2.ll
```

## Converting c source code to LLVM assembly

`clang`

Generate LLVM IR from C code:

```shell
$ clang -emit-llvm -S multiply.c -o multiply.ll
```

Use `ccl` for generating IR
```shell
$ clang -ccl -emit-llvm testfile.c -o testfile.ll
```

## Converting IR to LLVM bitcode

`llvm-as` is the LLVM assembler. It converts the LLVM assembly file from IR to bitcode.

```shell
$ llvm-as test.ll -o test.bc
$ hexdump -C test.bc
```

## Converting LLVM bitcode to target machine assembly

`llc`

```shell
$ llc test.bc -o test.s
```
`test.s` is the assembly code.

Or use Clang front end to generate the assembly code:
```shell
$ clang -S test.bc -o test.s –fomit-frame-pointer
```
We use the additional option fomit-frame-pointer , as Clang by default does not eliminate the frame pointer whereas llc eliminates it by default

### Setting Arch and CPU

```shell
-march=architecture flag
-mcpu=cpu flag
-regalloc=basic/greedy/fast/pbqp
```

## Converting LLVM bitcode back to LLVM assembly

`llvm-dis`

```shell
$ llvm-dis test.bc -o test.ll
```

## Transforming LLVM IR

```shell
$ opt -passname input.ll -o output.ll
For example:
$ opt -mem2reg -S multiply.ll -o multiply1.ll
```

When the `–analyze` option is passed to `opt`, it performs various analyses of the input source
and prints results usually on the standard output or standard error. Also, the output can be
redirected to a file when it is meant to be fed to another program.
When the `–analyze` option is not passed to opt, it runs the transformation passes meant to
optimize the input file.

Important transformations:

- adce : Aggressive Dead Code Elimination
- bb-vectorize : Basic-Block Vectorization
- constprop : Simple constant propagation
- dce : Dead Code Elimination
- deadargelim : Dead Argument Elimination
- globaldce : Dead Global Elimination
- globalopt : Global Variable Optimizer
- gvn : Global Value Numbering
- inline : Function Integration/Inlining
- instcombine : Combine redundant instructions
- licm : Loop Invariant Code Motion
- loop : unswitch: Unswitch loops
- loweratomic : Lower atomic intrinsics to non-atomic form
- lowerinvoke : Lower invokes to calls, for unwindless code generators
- lowerswitch : Lower SwitchInsts to branches
- mem2reg : Promote Memory to Register
- memcpyopt : MemCpy Optimization
- simplifycfg : Simplify the CFG
- sink : Code sinking
- tailcallelim : Tail Call Elimination

## Linking LLVM bitcode

`llvm-link`

```shell
$ clang -emit-llvm -S test1.c -o test1.ll
$ clang -emit-llvm -S test2.c -o test2.ll
$ llvm-as test1.ll -o test1.bc
$ llvm-as test2.ll -o test2.bc
```

`llvm-link` only links bitcode files.

## Executing LLVM bitcode

`lli`

```shell
$ lli output.bc
```

`lli` command executes the program present in LLVM bitcode format by using a jsut-in-time compiler, if there is one available for the architecture, or an interpreter.

## Using the C frontend Clang

`Clang` tool

```shell
$ clang test.c
```

`Clang` can be used in preprocessor only mode by providing the `-E` flag. If we use 
```c
#define MAX 100

int a[MAX]
```
After compiling,
```shell
$ clang test.c -E
```
It turns out:
```c
int a[100]
```
### Print the AST

`clang` can also be used to print the AST (`-ccl` option ensures that only the compiler front-end should be run, not the driver, and it prints the AST corresponding to the test.c file code):
```shell
clang -ccl test.c -ast-dump
```

### Generate LLVM assembly
Or using `clang` to generate the LLVM assembly (`-S` and `-emit-llvm` flag ensure the LLVM assembly is generated for the test.c code):
```shell
$ clang test.c -S -emit-llvm -o -
```

### Generate Machine Code

It generates the output on standard output because of the option `-o -`:
```shell
$ clang -S test.c -o -
```

When the `-S` flag is used alone, machine code is generated by the code generation process of the compiler.

## Using the GO frontend, DragonEgg...

...

# Chapter 2: Steps in Writing a Frontend

Before implementing a lexer and parser, the ayntax and grammer of the language need to be determined first. A TOY langugage is used to demonstrate how a lexer and a parser can be implemented.

### Lexer

Lexer <http://clang.llvm.org/doxygen/Lexer_8cpp_source.html> tokenizes a stream of input in a program. A token is a string of one or more characters that are significant as a group.

Defining the types of tokens of input strings:

```c++
enum Token_Type { 
  EOF_TOKEN = 0, 	//It states the end of file
  DEF_TOKEN, 			// The current token is of numeric type
  IDENTIFIER_TOKEN,	// The current token is identifier 
  PARAN_TOKEN,		// The current token is parenthesis 
  DEF_TOKEN			// the current token def states the whatever follows is a function definition 
};

static in Numeric_Val;	// Holds numeric values

static std::string Identifier_string;	// Holds the Identifier string name

static int get_token() {...}
```

### Parsing simple expressions

A simple expression may consist of numeric values, identifiers, function calls, a dfunction declaration, and function definitions. Individual parser logic needs to be defined for each type of expression.

Now invoking the AST constructors for every type of expression.

```c++
// the parser function for numeric expression
static BaseAST *numeric_parser() {	
  BaseAST *Result = new NumericAST(Numeric_Val); 
  next_token(); 
  return Result; 
}
// The parser function for an idenfitier expression. An identifier can be a variable reference or a function call. They are distinguished by checking if the next token is (.
static BaseAST* identifier_parser() {
  std::string IdName = Identifier_string;
  next_token();
  if(Current_token != '(') 
    return new VariableAST(IdName);
  next_token();
  std::vector<BaseAST*> Args; 
  if(Current_token != ')') {
    while(1) { BaseAST* Arg = expression_parser(); 
              if(!Arg) return 0;
              Args.push_back(Arg);
              if(Current_token == ')') break;
              if(Current_token != ',') return 0; 
              next_token();
             }
  } 
  next_token();
  return new FunctionCallAST(IdName, Args);
}
// The parser function for the function declaration
static FunctionDeclAST *func_decl_parser() {
  if(Current_token != IDENTIFIER_TOKEN) 
    return 0;
  std::string FnName = Identifier_string;
  next_token();
  if(Current_token != '(') return 0;
  std::vector<std::string> Function_Argument_Names;
  while(next_token() == IDENTIFIER_TOKEN)
    Function_Argument_Names.push_back(Identifier_string); 
  if(Current_token != ')') return 0;
  next_token();
  return new FunctionDeclAST(FnName, Function_Argument_Names);
}
// The parser function for the function definition.
static FunctionDefnAST *func_defn_parser() {
  next_token(); 
  FunctionDeclAST *Decl = func_decl_parser(); 
  if(Decl == 0) return 0;
  if(BaseAST* Body = expression_parser()) 
    return new FunctionDefnAST(Decl, Body); 
  return 0;
}
// The parser function for the expression parses
static BaseAST *expression_parser() { 
  BaseAST *LHS = Base_Parser(); 
  if(!LHS) return 0; 
  return binary_op_parser(0, LHS); 
}
```

### Parsing binary expressions

<http://clang.llvm.org/doxygen/classclang_1_1Parser.html.>

The binary expression parser requires precedence of binary operators for determining LHS and RHS in order. An STL map can be used to define precedence of binary operators.

```c++
// Declare a map for operator precedence to store the precedence at global scope. 4 operators: -<+</<*
static std::map<char, int> Operator_precedence;
// Precedence initilization
static void init_precedence() {
  Operator_Precedence['-'] = 1;
  Operator_Precedence['+'] = 2;
  Operator_Precedence['/'] = 3;
  Operator_Precedence['*'] = 4;
}
// A helper function to return precedence of binary operator
static int getBinOpPrecedence() { 
  if(!isascii(Current_token)) return -1;
  int TokPrec = Operator_Precedence[Current_token]; 
  if(TokPrec <= 0) return -1; 
  return TokPrec;
}
// The parser function for binary operator. The binary operator is recusively called since the RHS can be an expression and not just a single identifier.
static BaseAST* binary_op_parser(int Old_Prec, BaseAST *LHS) { 
  while(1) { 
    int Operator_Prec = getBinOpPrecedence();
    if(Operator_Prec < Old_Prec) return LHS;
    int BinOp = Current_token; next_token();
    BaseAST* RHS = Base_Parser(); 
    if(!RHS) return 0;
    int Next_Prec = getBinOpPrecedence(); 
    if(Operator_Prec < Next_Prec) {
      RHS = binary_op_parser(Operator_Prec+1, RHS);
      if(RHS == 0) return 0;
    }
    LHS = new BinaryAST(std::to_string(BinOp), LHS, RHS);
  }
}
// Parser for parenthesis
static BaseAST* paran_parser() {
  next_token(); 
  BaseAST* V = expression_parser(); 
  if (!V) return 0;
  if(Current_token != ')') return 0; 
  return V;
}
// Some top-level functions acting as wrapper around these parser functions
static void HandleDefn() {
  if (FunctionDefnAST *F = func_defn_parser()) { 
    if(Function* LF = F->Codegen()) { } 
  } else {
    next_token();
  }
}
static void HandleTopExpression() {
  if(FunctionDefnAST *F = top_level_parser()) { 
    if(Function *LF = F->Codegen()) { } 
  } else {
    next_token(); 
  }
}
```

### Invoking a driver for parsing

<http://llvm.org/viewvc/llvm-project/cfe/trunk/tools/driver/cc1_main.cpp>

Call the parser function from the main function.

```c++
// A Driver function called from the main function
static void Driver() {
  while(1) { 
    switch(Current_token) { 
      case EOF_TOKEN : return; 
      case ';' : next_token(); break; 
      case DEF_TOKEN : HandleDefn(); break; 
      default : HandleTopExpression(); break; 
    } 
  }
}
// Main function
int main(int argc, char* argv[]) {
  LLVMContext &Context = getGlobalContext(); 
  init_precedence();
  file = fopen(argv[1], "r");
  if(file == 0) { 
    printf("Could not open file\n"); 
  } 
  next_token(); 
  Module_Ob = new Module("my compiler", Context); 
  Driver(); 
  Module_Ob->dump();
  return 0;
}
```

### Running lexer and parser

<http://llvm.org/docs/tutorial/LangImpl2.html#parser-basics.>

```c++
// compile the program into an executable
$ clang++ toy.cpp -O3 -o toy
// Now using this frontend to parse a file
$ cat example
  def foo(x, y)
  x + y * 16
$ ./toy example
```

### Defining IR code generation methods for each AST class

In order to generate LLVM IR, a virtual CodeGen function is defined in each AST class

```c++
// virtual Codegen() function is included in every AST class. It returns an LLVM Value object, which represents Static Single Assignment calue in LLVM.
class BaseAST {
  ...
    virtual Value* Codegen() = 0;
}
class NumericAST : public BaseAST { 
  ...
    virtual Value* Codegen(); 
}; 
class VariableAST : public BaseAST { 
  ...
    virtual Value* Codegen(); 
};
// Declare the following static variables in global scope
static Module *Module_Ob; 	// Module_Ob module contains all the functions and variables in the code
static IRBuilder<> Builder(getGlobalContext()); 	// Builder object helps to generate LLVM IR and keeps track of the current point in the program to insert LLVM instructions. Builder object has functions to create new instructions
static std::map<std::string, Value*>Named_Values;		// Named_Value map keeps track of all values defined in the current scope like a symbol table. 
```

### Gnerating IR code for expressions

```c++
// Gnerates code for numeric values. Integer constants are represented by the ConstantInt class whose numeric value is held by APInt class.
Value *NumericAST::Codegen() { 
  return ConstantInt::get(Type::getInt32Ty(getGlobalContext()), numeric_val); 
}
// Generates code for variabl expressions
Value *VariableAST::Codegen() { 
  Value *V = Named_Values[Var_Name]; 
  return V ? V : 0; 
}
// The Codegen() function for binary expression. If the code emits multiple addtmp variables, LLVM will automatically provide each one with an increasing, unique numeric suffix.
Value *BinaryAST::Codegen() {
  Value *L = LHS->Codegen(); 
  Value *R = RHS->Codegen(); 
  if(L == 0 || R == 0) return 0;
  switch(atoi(Bin_Operator.c_str())) { 
    case '+' : return Builder.CreateAdd(L, R, "addtmp"); 
    case '-' : return Builder.CreateSub(L, R, "subtmp"); 
    case '*' : return Builder.CreateMul(L, R, "multmp"); 
    case '/' : return Builder.CreateUDiv(L, R, "divtmp"); 
    default : return 0; 
  }
}
```

### Gnerating IR code for functions

```c++
// The Codegen() function for the function call. We recursively call the Codegen() function for each argument taht is to be passed in and create an LLVM call instruction.
Value *FunctionCallAST::Codegen() {
  Function *CalleeF = Module_Ob->getFunction(Function_Callee); 
  std::vector<Value*>ArgsV; 
  for(unsigned i = 0, e = Function_Arguments.size(); i != e; ++i) {
    ArgsV.push_back(Function_Arguments[i]->Codegen()); 
    if(ArgsV.back() == 0) return 0;
  } return Builder.CreateCall(CalleeF, ArgsV, "calltmp");
}
// The Codegen() function for declaration and function definitions.
Function *FunctionDeclAST::Codegen() {...}
Function *FunctionDefnAST::Codegen() {...}
// The Codegen() functions can be called in the wrappers written to parse top-level expressions. After parsing successfully, the respective Codegen() functions are called to generate the LLVM IR. The dump() function is called to print the generated IR.
static void HandleDefn() {
  if (FunctionDefnAST *F = func_defn_parser()) { 
    if(Function* LF = F->Codegen()) { } 
  	} else {next_token();
  }
} 
static void HandleTopExpression() {
  if(FunctionDefnAST *F = top_level_parser()) { 
    if(Function *LF = F->Codegen()) { } 
  	} else {
    next_token(); 
  	}
	}
}
```

The Codegen() fcuntions use LLVM inbuilt function calls to generate IR. So we need to include header files:

```c++
llvm/IR/Verifier.h, llvm/IR/DerivedTypes.h, llvm/ IR/IRBuilder.h, and llvm/IR/LLVMContext.h, llvm/IR/Module.h.
```

While compiling, this program needs to be linked with LLVM libraries.

```shell
$ clang++ -O3 toy.cpp `llvm-config --cxxflags --ldflags -system-libs --libs core` -o toy
```

After compiling, run on example code.

```shell
$ ./toy example

define i32 @foo (i32 %x, i32 %y) { 
	entry:%multmp = muli32 %y, 16 
	%addtmp = add i32 %x, %multmp 
	reti32 %addtmp 
}
```

Codegen() function: <http://llvm.org/viewvc/llvm-project/cfe/trunk/lib/CodeGen/>

### Adding IR optimization support

```c++
// To start with the addition of IR optimization support, first of all a static variable for function manager has to be defined
static FunctionPassManager *Global_FP;
// A function pass manager needs to be defined for the Module object used previous. This can be done in the main() function
FunctionPassManager My_FP(TheModule);
// A pipeline of various optimizer passes can be added in the main() function
My_FP.add(createBasicAliasAnalysisPass()); 
My_FP.add(createInstructionCombiningPass()); 
My_FP.add(createReassociatePass()); 
My_FP.add(createGVNPass()); 
My_FP.doInitialization();
// The static global function Pass Manager is assigned to this pipeline. 
Global_FP = &My_FP;
Driver();
// This PassManager has a run method, which we can run on the function IR generated before returing from Codegen() of the fucntion definition.
Function* FunctionDefnAST::Codegen() { 
  Named_Values.clear(); 
  Function *TheFunction = Func_Decl->Codegen(); 
  if (!TheFunction) return 0; 
  BasicBlock *BB = BasicBlock::Create(getGlobalContext(), "entry", TheFunction);
  Builder.SetInsertPoint(BB); 
  if (Value* Return_Value = Body->Codegen()) { 
    Builder.CreateRet(Return_Value); 
    verifyFunction(*TheFunction); 
    Global_FP->run(*TheFunction); 
    returnTheFunction; 
  } 
  TheFunction->eraseFromParent(); 
  return 0;
}

```

# Chapter 3: Extending the Frontend and Adding JIT Support
This chapter deals with enhancements of a programming language that make it more meaningfule and powerful to use. 

### Handling decision making paradigms - if/then/else constructs

So we add the condition related functions.

```c++
// For TOY language, if/then.else can be defined as:
if x<2 then
  x+y
else
  x-y 
// For checking a condition, a comparison operator is required. 
static void init_precedence() {
  Operator_Precedence['<'] = 0;
  ...
}
// And the codegen() function for binary expression needs to be included for <
Value* BinaryAST::Codegen() {
  ...
    case '<': 
  			L = Builder.CreateICmpULT(L, R, "cmptmp"); 
  			return Builder.CreateZExt(L, Type::getInt32Ty(getGlobalContext()), "booltmp");
 	...
}
```

For the toy.cpp file, additional tokens need to be include.

```c++
enum Token_Type{..., IF_TOKEN, THEN_TOKEN, ELSE_TOKEN }
// Append the entries for these tokens in the get_token() function
static int get_token() { 
  ...
  if (Identifier_string == "def") return DEF_TOKEN; 
  if(Identifier_string == "if") return IF_TOKEN; 
  if(Identifier_string == "then") return THEN_TOKEN; 
  if(Identifier_string == "else") return ELSE_TOKEN;
  ...
}
// Then define an AST node
class ExprIfAST : public BaseAST { 
  BaseAST *Cond, *Then, *Else;
public:
  ExprIfAST(BaseAST *cond, BaseAST *then, BaseAST * else_st) : Cond(cond), Then(then), Else(else_st) {} 
  Value *Codegen() override; 
};
// Define the parsing logic for the if/then/else constructs. The if token is searched for and the expression following it is parsed for the condition. After that, the then token is identified and the tru condition expression is parsed. Then the else token is searched for and the false condition expression is parsed.
static BaseAST *If_parser() {
  next_token();
  BaseAST *Cond = expression_parser(); 
  if (!Cond)return 0;
  if (Current_token != THEN_TOKEN) return 0; 
  next_token();
  BaseAST *Then = expression_parser(); 
  if (Then == 0) return 0;
  if (Current_token != ELSE_TOKEN) return 0;
  next_token();
  BaseAST *Else = expression_parser(); 
  if (!Else) return 0;
  return new ExprIfAST(Cond, Then, Else);
}
// Hook up the previously defined function with Base_parser()
static BaseAST* Base_Parser() { switch(Current_token) { 
  ...
	case IF_TOKEN : return If_parser(); 
  ...
}
// Generate the LLVM IR for the condition paradigm
Value *ExprIfAST::Codegen() {...}                               
```

![image-20200610173326575](/Users/tancy/Library/Application Support/typora-user-images/image-20200610173326575.png)

Details about how an if else statement is handled in C++ by Clang: <http://clang.llvm.org/doxygen/classclang_1_1IfStmt.html.>

### Gernerating code for loops

The loop in TOY language can be defined as:

```c++
for i = 1, i < n, 1 in
  x + y;
```

The same as if/then/else, loops are also handled by including states in lexer.

```c++
enum Token_Type { ..., FOR_TOKEN, IN_TOKEN, ...};
// Inluding the logic in the lexer
static int get_token() { 
  ...
  if (Identifier_string == "else") return ELSE_TOKEN; 
  if (Identifier_string == "for") return FOR_TOKEN; 
  if (Identifier_string == "in") return IN_TOKEN; 
  ...
}
// Define the AST
class ExprForAST : public BaseAST {
  std::string Var_Name; BaseAST *Start, *End, *Step, *Body;
public:
  ExprForAST (const std::string &varname, BaseAST *start, BaseAST *end, BaseAST *step, BaseAST *body): Var_Name(varname), Start(start), End(end), Step(step), Body(body) {}
  Value *Codegen() override; 
};
// Define the parser
static BaseAST *For_parser() {...}
// Define the Codegen() function to generate the LLVM IR
Value *ExprForAST::Codegen() {...}
```

Run the example to see the output:

```shell
$ g++ -g toy.cpp `llvm-config --cxxflags --ldflags --systemlibs --libs core ` -O3 -o toy
$ vi example
def printstar(n x)
	for i = 1, i < n, 1.0 in
		x + 1
$ ./toy example
; ModuleID = 'my compiler' 
target datalayout = "e-m:e-p:32:32-f64:32:64-f80:32-n8:16:32-S128"

define i32 @printstar(i32 %n, i32 %x) { 
	entry:
		br label %loop
	loop: 																								; preds = %loop,
		%entry
			%i = phi i32 [ 1, %entry ], [ %nextvar, %loop ]
			%nextvar = add i32 %i, 1 
			%cmptmp = icmp ult i32 %i, %n 
			br i1 %cmptmp, label %loop, label %afterloop
	afterloop:																						; preds = %loop
		ret i32 0 
	}
```

> A phi instruction gets two values for the variable i from two basic blocks: %entry and %loop. In the preceding case, the %entry block represents the value assigned to the induction variable at the start of the loop (this is 1). The next updated value of i comes from the %loop block, which completes one iteration of the loop.

Details of how loops are handled for C++ in Clang: 

http://llvm.org/viewvc/llvm-project/cfe/trunk/lib/Parse/ParseExprCXX.cpp>

### Handling user-defined operators - binary operators

Set | operator as an example:

```c++
// As seen in the preceding code, if any of the values of the LHS or RHS are not equal to 0, then we return 1. If both the LHS and RHS are null, then we return 0.
def binary | (LHS RHS) if LHS then 1 else if RHS then 1 else 0;
```

Modify the toy.cpp to handle user-defined operators.

```c++
// Append the enum states and get_token() function
enum Token_Type { ..., BINARY_TOKEN } 
static int get_token() { 
  ...
  if (Identifier_string == "in") return IN_TOKEN; 
  if (Identifier_string == "binary") return BINARY_TOKEN; 
  ...
}
// Modify the function declaration AST
class FunctionDeclAST { 
  std::string Func_Name; std::vector<std::string> Arguments; 
  bool isOperator; 
  unsigned Precedence; public:
  
  FunctionDeclAST(const std::string &name, const std::vector<std::string> &args, 
                  bool isoperator = false, unsigned prec = 0)
    : Func_Name(name), Arguments(args), isOperator(isoperator), 
  Precedence(prec) {}
  bool isUnaryOp() const { return isOperator && Arguments.size() == 1; }
  bool isBinaryOp() const { return isOperator && Arguments.size() == 2; }
  
  char getOperatorName() const { 
    assert(isUnaryOp() || isBinaryOp()); 
    return Func_Name[Func_Name.size() - 1]; 
  }
  unsigned getBinaryPrecedence() const { 
    return Precedence;
  }

	Function *Codegen(); 
};
// Modify the parser
static FunctionDeclAST *func_decl_parser() {...}
// Modify the Codegen()
...
// Modify the function definition
Function* FunctionDefnAST::Codegen() { 
  Named_Values.clear(); Function *TheFunction = Func_Decl->Codegen(); 
  if (!TheFunction) return 0; 
  if (Func_Decl->isBinaryOp())
    Operator_Precedence [Func_Decl->getOperatorName()] = Func_ Decl->getBinaryPrecedence();
  BasicBlock *BB = BasicBlock::Create(getGlobalContext(), "entry", TheFunction);
  Builder.SetInsertPoint(BB); if (Value* Return_Value = Body->Codegen()) {
    Builder.CreateRet(Return_Value); 
  ...
```

Compile and run it.

```shell
$ g++ -g toy.cpp `llvm-config --cxxflags --ldflags --systemlibs --libs core ` -O3 -o toy
$ vi example
def binary| 5 (LHS RHS)
	if LHS then 
		1 
	else if RHS then
		1 
	else
		0;
$ ./toy example

output :

; ModuleID = 'my compiler' 
target datalayout = "e-m:e-p:32:32-f64:32:64-f80:32-n8:16:32-S128"
define i32 @"binary|"(i32 %LHS, i32 %RHS) { 
entry:
	%ifcond = icmp eq i32 %LHS, 0 
	%ifcond1 = icmp eq i32 %RHS, 0 
	%. = select i1 %ifcond1, i32 0, i32 1 
	%iftmp5 = select i1 %ifcond, i32 %., i32 1 
	ret i32 %iftmp5
}
```

### Handling user-defined operators - unary operators

```c++
// If the value v is equal to 1, then 0 is returned. If the value is 0, 1 is returned as the output.
def unary!(v) if v then 0 else 1;
```

...

### Adding JIT support

JIT support can be added. It immediately evaluates the top-level expression typed in. For example, input 1+2, output 3.

```c++
// Define a static global variable for the execution engine in the same toy.cpp file
static ExecutionEngine *TheExecutionEngine;
// Write the code for JIT in the main() function
int main() { 
  ...
  init_precedence(); 
  TheExecutionEngine = EngineBuilder(TheModule).create();
  ...
}
// Modify the top-level expression parser in the toy.cpp file
static void HandleTopExpression() {
  if (FunctionDefAST *F = expression_parser()) 
    if (Function *LF = F->Codegen()) { 
      LF -> dump(); 
      void *FPtr = TheExecutionEngine>getPointerToFunction(LF); 
      int (*Int)() = (int (*)())(intptr_t)FPtr;
      
      printf("Evaluated to %d\n", Int());
    }
  else next_token(); 
}
```

Compile and run:

```shell
$ g++ -g toy.cpp `llvm-config --cxxflags --ldflags --systemlibs --libs core mcjit native` -O3 -o toy
$ vi example
...
	4+5;
$ ./toy example 
# The output will be 
define i32 @0() { 
	entry:
	ret i32 9 
}
```

