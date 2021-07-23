# Chap7: Optimizing the Machine code

The machine code genreated is in the SSA form, but the target registers are limited in number.

Machine code optimizations are almost the same as in the LLVM IR.

One of the machine code optimization techniques implemented in the LLVM trunk code reposiroty--machine CSE. 

## Eliminating common subexpression from machine code

CSE algorithm: eliminate common subexpressions to make machine code compact and remove unnecessary, dublicate code. <lib/CodeGen/MachineCSE.cpp>

```c++
// MachineCSE inherites the MachineFucntionPass class
class MachineCSE : public MachineFunctionPass { 
  const TargetInstrInfo *TII; 		// it is used to get information about the target instruction (used in performing CSE)
  const TargetRegisterInfo *TRI; 	// used to get information about the target register
  AliasAnalysis *AA; 	
  MachineDominatorTree *DT;				// used to get information about the dominator tree for the machine block 
  MachineRegisterInfo *MRI;
  // the constructor fo this class (initialize the pass)
public:
  static char ID; // Pass identification 
  MachineCSE() : MachineFunctionPass(ID), LookAheadLimit(5), CurrVN(0) {
    initializeMachineCSEPass(*PassRegistry::getPassRegistry());
  }
  // determines which passes will run befroe this pass to get statistics that can be used in this pass
  void getAnalysisUsage(AnalysisUsage &AU) const override { 
    AU.setPreservesCFG(); 
    MachineFunctionPass::getAnalysisUsage(AU); 
    AU.addRequired<AliasAnalysis>();
    AU.addPreservedID(MachineLoopInfoID); 
    AU.addRequired<MachineDominatorTree>(); 
    AU.addPreserved<MachineDominatorTree>();
  }
  // Declare some helper functions in this pass to check for cimple copy progation and trivially dead definitions, check fot the liveness of physical registers and their definition used, and so on
private:
  ...
  bool PerformTrivialCopyPropagation(MachineInstr *MI, MachineBasicBlock *MBB);
  bool isPhysDefTriviallyDead(unsigned Reg,
                              MachineBasicBlock::const_iterator I,
                              MachineBasicBlock::const_iterator E) const;
  bool hasLivePhysRegDefUses(const MachineInstr *MI, 
                             const MachineBasicBlock *MBB, 
                             SmallSet<unsigned,8> &PhysRefs, 
                             SmallVectorImpl<unsigned> &PhysDefs, bool &PhysUseDef) const;
  bool PhysRegDefsReach(MachineInstr *CSMI, MachineInstr *MI, 
                        SmallSet<unsigned,8> &PhysRefs, 
                        SmallVectorImpl<unsigned> &PhysDefs, 
                        bool &NonLocal) const;
  // more helper functions help to determine the legality and profitability of the expression being a CSE candidate
  bool isCSECandidate(MachineInstr *MI); 
  bool isProfitableToCSE(unsigned CSReg, unsigned Reg, 
                         MachineInstr *CSMI, MachineInstr *MI);
  Actual CSE performing function bool PerformCSE(MachineDomTreeNode *Node);
```

The actual implementation of a CSE function

```c++
// called first as the pass runs
bool MachineCSE::runOnMachineFunction(MachineFunction &MF){ 
  if (skipOptnoneFunction(*MF.getFunction())) 
    return false;
  TII = MF.getSubtarget().getInstrInfo(); 
  TRI = MF.getSubtarget().getRegisterInfo(); 
  MRI = &MF.getRegInfo();
  AA = &getAnalysis<AliasAnalysis>();
  DT = &getAnalysis<MachineDominatorTree>();
  
  return PerformCSE(DT->getRootNode());
}

// called next. takes the root node of the DomTree, performs a DFS walk on the DomTree (starting from the root node), and populates a work list consisting of the nodes of the DomTree. After the DFS traverses through the DomTree, it processes the MachineBasicBlock class corresponding to each node in the work list:
bool MachineCSE::PerformCSE(MachineDomTreeNode *Node) { 
  SmallVector<MachineDomTreeNode*, 32> Scopes; 
  SmallVector<MachineDomTreeNode*, 8> WorkList; 
  DenseMap<MachineDomTreeNode*, unsigned> OpenChildren;

	CurrVN = 0; // DFS to populate worklist 
  WorkList.push_back(Node); 
  do { 
    Node = WorkList.pop_back_val(); 
    Scopes.push_back(Node); 
    const std::vector<MachineDomTreeNode*> &Children = Node->getChildren(); 
    unsigned NumChildren = Children.size(); 
    OpenChildren[Node] = NumChildren; 
    for (unsigned i = 0; i != NumChildren; ++i) { 
      MachineDomTreeNode *Child = Children[i]; 
      WorkList.push_back(Child); 
    } 
  } 
  while (!WorkList.empty());

	// perform CSE.

	bool Changed = false; 
  for (unsigned i = 0, e = Scopes.size(); i != e; ++i) { 
    MachineDomTreeNode *Node = Scopes[i];
    MachineBasicBlock *MBB = Node->getBlock(); 
    EnterScope(MBB); 
    Changed |= ProcessBlock(MBB); 
    ExitScopeIfDone(Node, OpenChildren);
}
	return Changed;
}

// acts on the machines basic block. The instructions in the MachineBasicBlock class are iterated and checked for legality and profitability if they can be a CSE candidate:
bool MachineCSE::ProcessBlock(MachineBasicBlock *MBB) { 
  bool Changed = false;
	SmallVector<std::pair<unsigned, unsigned>, 8> CSEPairs; 
  SmallVector<unsigned, 2> ImplicitDefsToUpdate;

	// Iterate over each Machine instructions in the MachineBasicBlock 
  for (MachineBasicBlock::iterator I = MBB->begin(), E = MBB->end(); I != E; ) { 
    MachineInstr *MI = &*I; ++I;

	// Check if this can be a CSE candidate.
	if (!isCSECandidate(MI)) continue;

	bool FoundCSE = VNT.count(MI); 
    if (!FoundCSE) { // Using trivial copy propagation to find more CSE opportunities.
      if (PerformTrivialCopyPropagation(MI, MBB)) { 
        Changed = true;
			// After coalescing MI itself may become a copy. 
        if (MI->isCopyLike()) 
          continue;
			// Try again to see if CSE is possible. 
        FoundCSE = VNT.count(MI);
      }
    }
    bool Commuted = false; 
    if (!FoundCSE && MI->isCommutable()) {
      MachineInstr *NewMI = TII->commuteInstruction(MI); 
      if (NewMI) { 
        Commuted = true; 
        FoundCSE = VNT.count(NewMI); 
        if (NewMI != MI) { // New instruction. It doesn't need to be kept. 
          NewMI->eraseFromParent(); 
          Changed = true; 
        } 
        else if (!FoundCSE) // MI was changed but it didn't help, commute it back!
          (void)TII->commuteInstruction(MI);
      }
    }

		// If the instruction defines physical registers and the values *may* be // used, then it's not safe to replace it with a common subexpression.
		// It's also not safe if the instruction uses physical registers.
    bool CrossMBBPhysDef = false; 
    SmallSet<unsigned, 8> PhysRefs; 
    SmallVector<unsigned, 2> PhysDefs; 
    bool PhysUseDef = false;

		// Check if this instruction has been marked for CSE. Check if it is using physical register, if yes then mark as nonCSE candidate 
    if (FoundCSE && hasLivePhysRegDefUses(MI, MBB, PhysRefs, PhysDefs, PhysUseDef)) {
      FoundCSE = false;
      ...
    }

		if (!FoundCSE) { 
      VNT.insert(MI, CurrVN++); 
      Exps.push_back(MI);
      continue; 
    }
    // Finished job of determining if there exists a common subexpression.
		// Found a common subexpression, eliminate it.

		unsigned CSVN = VNT.lookup(MI); 
    MachineInstr *CSMI = Exps[CSVN]; 
    DEBUG(dbgs() << "Examining: " << *MI); 
    DEBUG(dbgs() << "*** Found a common subexpression: " << *CSMI);

		// Check if it's profitable to perform this CSE.
		bool DoCSE = true; unsigned NumDefs = MI->getDesc().getNumDefs() + MI->getDesc().getNumImplicitDefs();

		for (unsigned i = 0, e = MI->getNumOperands(); NumDefs && i != e; ++i) { 
      MachineOperand &MO = MI->getOperand(i); 
      if (!MO.isReg() || !MO.isDef()) 
        continue; 
      unsigned OldReg = MO.getReg(); 
      unsigned NewReg = CSMI->getOperand(i).getReg();

			// Go through implicit defs of CSMI and MI, if a def is not dead at MI, // we should make sure it is not dead at CSMI.
      if (MO.isImplicit() && !MO.isDead() && CSMI->getOperand(i). isDead())
        ImplicitDefsToUpdate.push_back(i); 
      if (OldReg == NewReg) { 
        --NumDefs; 
        continue; 
      }
      assert(TargetRegisterInfo::isVirtualRegister(OldReg) && TargetRegisterInfo::isVirtualRegister(NewReg) && "Do not CSE physical register defs!");

			if (!isProfitableToCSE(NewReg, OldReg, CSMI, MI)) { 
        DEBUG(dbgs() << "*** Not profitable, avoid CSE!\n"); 
        DoCSE = false; 
        break;
      }

			// Don't perform CSE if the result of the old instruction cannot exist // within the register class of the new instruction.
			const TargetRegisterClass *OldRC = MRI->getRegClass(OldReg); 
      if (!MRI->constrainRegClass(NewReg, OldRC)) { 
        DEBUG(dbgs() << "*** Not the same register class, avoid CSE!\n"); 
        DoCSE = false; break; 
      }

			CSEPairs.push_back(std::make_pair(OldReg, NewReg)); 
      --NumDefs;
    }

		// Actually perform the elimination.
		if (DoCSE) { for (unsigned i = 0, e = CSEPairs.size(); i != e; ++i) { 
      MRI->replaceRegWith(CSEPairs[i].first, CSEPairs[i]. second); 
      MRI->clearKillFlags(CSEPairs[i].second); 
    }

		// Go through implicit defs of CSMI and MI, if a def is not dead at MI, 
    // we should make sure it is not dead at CSMI.
    for (unsigned i = 0, e = ImplicitDefsToUpdate.size(); i != e; ++i)
      CSMI->getOperand(ImplicitDefsToUpdate[i]). setIsDead(false);

		if (CrossMBBPhysDef) { // Add physical register defs now coming in from a predecessor to MBB // livein list.
      while (!PhysDefs.empty()) { 
        unsigned LiveIn = PhysDefs.pop_back_val(); 
        if (!MBB->isLiveIn(LiveIn)) 
          MBB->addLiveIn(LiveIn); 
      } 
      ++NumCrossBBCSEs;
			MI->eraseFromParent(); 
      ++NumCSEs; 
      if (!PhysRefs.empty()) 
        ++NumPhysCSEs; 
      if (Commuted) 
        ++NumCommutes; 
      Changed = true; 
    } 
    else { 
      VNT.insert(MI, CurrVN++); 
      Exps.push_back(MI); 
    } 
    CSEPairs.clear(); 
    ImplicitDefsToUpdate.clear();
   }
    return Changed;
  }
}
```

The legality and profitability functions to determine the CSE candidates

```c++
bool MachineCSE::isCSECandidate(MachineInstr *MI) { 
  // If Machine Instruction is PHI, or inline ASM or implicit defs, it is not a candidate for CSE.

	if (MI->isPosition() || MI->isPHI() || MI>isImplicitDef() || MI->isKill() || MI->isInlineAsm() || MI->isDebugValue()) 
    return false;

	// Ignore copies.
	if (MI->isCopyLike()) 
    return false;

	// Ignore instructions that we obviously can't move.
  if (MI->mayStore() || MI->isCall() || MI->isTerminator() || MI->hasUnmodeledSideEffects()) 
    return false;

	if (MI->mayLoad()) { 
    // Okay, this instruction does a load. As a refinement, we allow the target // to decide whether the loaded value is actually a constant. If so, we can // actually use it as a load.
    if (!MI->isInvariantLoad(AA)) 
      return false;
  } 
  return true;
}
```

The profitability function

```c++
bool MachineCSE::isProfitableToCSE(unsigned CSReg, unsigned Reg, MachineInstr *CSMI, MachineInstr *MI) {
  // If CSReg is used at all uses of Reg, CSE should not increase register // pressure of CSReg.
  bool MayIncreasePressure = true; 
  if (TargetRegisterInfo::isVirtualRegister(CSReg) && TargetRegisterInfo::isVirtualRegister(Reg)) { 
    MayIncreasePressure = false; 
    SmallPtrSet<MachineInstr*, 8> CSUses; 
    for (MachineInstr &MI : MRI->use_nodbg_instructions(CSReg)) { 
      CSUses.insert(&MI); 
    } 
    for (MachineInstr &MI : MRI>use_nodbg_instructions(Reg)) { 
      if (!CSUses.count(&MI)) { 
        MayIncreasePressure = true; 
        break; 
      } 
    }
  } 
  if (!MayIncreasePressure) 
    return true;

	// Heuristics #1: Don't CSE "cheap" computation if the def is not local or in // an immediate predecessor. We don't want to increase register pressure and // end up causing other computation to be spilled.
  if (TII->isAsCheapAsAMove(MI)) { 
    MachineBasicBlock *CSBB = CSMI->getParent(); 
    MachineBasicBlock *BB = MI->getParent(); 
    if (CSBB != BB && !CSBB->isSuccessor(BB)) 
      return false; 
  }
  // Heuristics #2: If the expression doesn't not use a vr and the only use // of the redundant computation are copies, do not cse. 
  bool HasVRegUse = false; 
  for (unsigned i = 0, e = MI->getNumOperands(); i != e; ++i) { 
    const MachineOperand &MO = MI->getOperand(i); 
    if (MO.isReg() && MO.isUse() && TargetRegisterInfo::isVirtualRegister(MO.getReg())) { 
      HasVRegUse = true; 
      break; 
    }
  } 
  if (!HasVRegUse) { 
    bool HasNonCopyUse = false; 
    for (MachineInstr &MI : MRI>use_nodbg_instructions(Reg)) { 
      // Ignore copies.
      if (!MI.isCopyLike()) { 
        HasNonCopyUse = true; 
        break; 
      } 
    } 
    if (!HasNonCopyUse) 
      return false;
  }

	// Heuristics #3: If the common subexpression is used by PHIs, do not reuse // it unless the defined value is already used in the BB of the new use.
  bool HasPHI = false; 
  SmallPtrSet<MachineBasicBlock*, 4> CSBBs; 
  for (MachineInstr &MI : MRI>use_nodbg_instructions(CSReg)) { 
    HasPHI |= MI.isPHI(); 
    CSBBs.insert(MI.getParent()); 
  }

	if (!HasPHI) 
    return true; 
  return CSBBs.count(MI->getParent());
}
```

> The MachineCSE pass runs on a machine function. It gets the DomTree information and then traverses the DomTree in the DFS way, creating a work list of nodes that are essentially MachineBasicBlocks. It then processes each block for CSE. In each block, it iterates through all the instructions and checks whether any instruction is a candidate for CSE. Then it checks whether it is profitable to eliminate the identified expression. Once it has found that the identified CSE is profitable to eliminate, it eliminates the MachineInstruction class from the MachineBasicBlock class. It also performs a simple copy propagation of the machine instruction. In some cases, the MachineInstruction may not be a candidate for CSE in its initial run, but may become one after copy propagation.

<lib/CodeGen/DeadMachineInstructionElim.cpp>

## Analyzing live intervals 

register allocation

- live intervals
  - The range in which a variable is live, that is, from the point where a variable is defined to its last use.

> Before register allocation, LLVM assumes that physical registers are live only within a single basic block. This enables it to perform a single, local analysis to resolve physical register lifetimes within each basic block. After performing the live variable analysis, we have the information required for performing live interval analysis and building live intervals. For this, we start numbering the basic block and machine instructions. After that live-in values, typically arguments in registers are handled.

1. Write a test code which will be used to perform live interval analysis.

- Write a test program with an if-else block then convert it into IR:

```shell
$ cat interval.c 
void donothing(int a) { 
	return; 
}

int func(int i) { 
	int a = 5; 
	donothing(a); 
	int m = a; 
	donothing(m);
	a = 9;
	if (i < 5) {
		int b = 3; 
		donothing(b); 
		int z = b; 
		donothing(z);
	} 
	else {
		int k = a;
		donothing(k); 
	}
	return m;
}

$ clang -cc1 -emit-llvm interval.c
```

2. To list the live intervals, we will need to modify the code of the LiveIntervalAnalysis.cpp fil by adding code to print the live intervals. We will add the following lines (marked with a+symbol before each added line):

```c++
void LiveIntervals::computeVirtRegInterval(LiveInterval &LI) {
	assert(LRCalc && "LRCalc not initialized.");
  assert(LI.empty() && "Should only compute empty intervals.");

	LRCalc->reset(MF, getSlotIndexes(), DomTree, &getVNInfoAllocator());
  LRCalc->calculate(LI, MRI->shouldTrackSubRegLiveness(LI.reg)); 
  computeDeadValues(LI, nullptr);

	/**** add the following code ****/ 
  + llvm::outs() << "********** INTERVALS **********\n";

	// Dump the regunits.
	+ for (unsigned i = 0, e = RegUnitRanges.size(); i != e; ++i) 
    + if (LiveRange *LR = RegUnitRanges[i]) 
      + llvm::outs() << PrintRegUnit(i, TRI) << ' ' << *LR << '\n';

	// Dump the virtregs.
	+ llvm::outs() << "virtregs:"; 
  + for (unsigned i = 0, e = MRI->getNumVirtRegs(); i != e; ++i) { 
    + unsigned Reg = TargetRegisterInfo::index2VirtReg(i); 
    + if (hasInterval(Reg)) 
      + llvm::outs() << getInterval(Reg) << '\n'; 
    + }
```

3. Build and install the LLVM after modifying the code.
4. Now combile the test code in the IR form using the llc command.

```shell
$ llc interval.ll 
********** INTERVALS ********** 
virtregs:%vreg0 [16r,32r:0) 0@16r 
********** INTERVALS ********** 
virtregs:%vreg0 [16r,32r:0) 0@16r 
********** INTERVALS ********** 
virtregs:%vreg0 [16r,32r:0) 0@16r 
%vreg1 [80r,96r:0) 0@80r 
********** INTERVALS ********** 
virtregs:%vreg0 [16r,32r:0) 0@16r 
%vreg1 [80r,96r:0) 0@80r 
%vreg2 [144r,192r:0) 0@144r 
********** INTERVALS ********** 
virtregs:%vreg0 [16r,32r:0) 0@16r 
%vreg1 [80r,96r:0) 0@80r
%vreg2 [144r,192r:0) 0@144r 
%vreg5 [544r,592r:0) 0@544r 
********** INTERVALS ********** 
virtregs:%vreg0 [16r,32r:0) 0@16r 
%vreg1 [80r,96r:0) 0@80r 
%vreg2 [144r,192r:0) 0@144r 
%vreg5 [544r,592r:0) 0@544r 
%vreg6 [352r,368r:0) 0@352r 
********** INTERVALS ********** 
virtregs:%vreg0 [16r,32r:0) 0@16r 
%vreg1 [80r,96r:0) 0@80r 
%vreg2 [144r,192r:0) 0@144r 
%vreg5 [544r,592r:0) 0@544r 
%vreg6 [352r,368r:0) 0@352r 
%vreg7 [416r,464r:0) 0@416r 
********** INTERVALS ********** 
virtregs:%vreg0 [16r,32r:0) 0@16r 
%vreg1 [80r,96r:0) 0@80r 
%vreg2 [144r,192r:0) 0@144r 
%vreg5 [544r,592r:0) 0@544r 
%vreg6 [352r,368r:0) 0@352r 
%vreg7 [416r,464r:0) 0@416r 
%vreg8 [656r,672r:0) 0@656r
```

>The process of generating these live intervals starts from the `LiveVariables::runOnMachineFunction(MachineFunction &mf)` function in the `lib/CodeGen/LiveVariables.cpp` file, where it assigns the definition and usage of the registers using the `HandleVirtRegUse` and `HandleVirtRegDef` functions. It gets the `VarInfo` object for the given virtual register using the `getVarInfo` function.
>
>The `LiveInterval` and `LiveRange` classes are defined in `LiveInterval.cpp`. The functions in this file takes the information on the liveliness of each variable and then checks whether they overlap or not.
>
>In the `LiveIntervalAnalysis.cp`p file, we have the implementation of the live interval analysis pass, which scans the basic blocks (ordered in a linear fashion) in depth-first order, and creates a live interval for each virtual and physical register. 
>
>Use the –debugonly=regalloc command-line option with the llc tool when compiling the test case to see how the virtual registers for different basic blocks get generated, and see the lifetime of these virtual registers.
>
>To get more detail on live intervals, go through these code files:
>
>- Lib/CodeGen/ LiveInterval.cpp 
>- Lib/CodeGen/ LiveIntervalAnalysis.cpp 
>- Lib/CodeGen/ LiveVariables.cpp

## Allocatin registers

Register allocation is the task of assigning physical registers to virtual registers.

1. To see how registers are represented in LLVM, open the build-folder/lib/ Target/X86/X86GenRegisterInfo.inc file and check out the first few lines, which show that registers are represented as integers:

```c++
namespace X86 { 
  enum { 
    NoRegister,
		AH = 1,
    AL = 2,
    AX = 3,
    BH = 4,
    BL = 5,
    BP = 6,
    BPL = 7,
    BX = 8,
    CH = 9,
    ...
```

2. Check alias information. For example: lib/Target/X86/X86RegisterInfo.td file

```c++
def AL : X86Reg<"al", 0>;
def DL : X86Reg<"dl", 2>;
def CL : X86Reg<"cl", 1>;
def BL : X86Reg<"bl", 3>;
def AH : X86Reg<"ah", 4>;
def DH : X86Reg<"dh", 6>;
def CH : X86Reg<"ch", 5>;
def BH : X86Reg<"bh", 7>;
def AX : X86Reg<"ax", 0, [AL,AH]>;
def DX : X86Reg<"dx", 2, [DL,DH]>;
def CX : X86Reg<"cx", 1, [CL,CH]>;
def BX : X86Reg<"bx", 3, [BL,BH]>;

// 32-bit registers 
let SubRegIndices = [sub_16bit] in {
	def EAX : X86Reg<"eax", 0, [AX]>, DwarfRegNum<[-2, 0, 0]>;
	def EDX : X86Reg<"edx", 2, [DX]>, DwarfRegNum<[-2, 2, 2]>;
	def ECX : X86Reg<"ecx", 1, [CX]>, DwarfRegNum<[-2, 1, 1]>;
	def EBX : X86Reg<"ebx", 3, [BX]>, DwarfRegNum<[-2, 3, 3]>;
	def ESI : X86Reg<"esi", 6, [SI]>, DwarfRegNum<[-2, 6, 6]>;
	def EDI : X86Reg<"edi", 7, [DI]>, DwarfRegNum<[-2, 7, 7]>;
	def EBP : X86Reg<"ebp", 5, [BP]>, DwarfRegNum<[-2, 4, 5]>;
	def ESP : X86Reg<"esp", 4, [SP]>, DwarfRegNum<[-2, 5, 4]>;
	def EIP : X86Reg<"eip", 0, [IP]>, DwarfRegNum<[-2, 8, 8]>;
  ...
```

3. Comment out some registers. Open the `X86RegisterInfo.cpp` file and remove the registers `AH`, `CH`, and `DH`:

```c++
def GR8 : RegisterClass<"X86", [i8], 8, 
		(add AL, CL, DL, AH, CH, DH, BL, BH, SIL, DIL, BPL, SPL, R8B, R9B, R10B, R11B, R14B, R15B, R12B, R13B)> {
```

4. When you build LLVM, the .inc file in the first step will have been changed and will not contain the AH, CH, and DH registers.
5. Use the test case from the previous sectin

```shell
$ llc –regalloc=basic interval.ll –o intervalregbasic.s
```

Next, create the `intervalregbasic.s` file, and run the command to compare the two files:

```shell
$ llc –regalloc=pbqp interval.ll –o intervalregpbqp.s
```

Create the intervalregbqp.s file, then use a diff tool and compare the two assemblies side by side.

> - Direct Mapping: By making use of the TargetRegisterInfo and MachineOperand classes. This depends on the developer, who needs to provide the location where load and store instructions should be inserted in order to get and store values in the memory.
>
> - Indirect Mapping: This depends on the VirtRegMap class to insert loads and stores, and to get and set values from the memory. Use the VirtRegMap::assignVirt2Phys(vreg, preg) function to map a virtual register on a physical one.
>
> To learn more about the algorithms used in LLVM, look through the source codes located at
>
> - lib/CodeGen/:
>
> - lib/CodeGen/RegAllocBasic.cpp 
> - lib/CodeGen/ RegAllocFast.cpp 
> - lib/CodeGen/ RegAllocGreedy.cpp 
> - lib/CodeGen/ RegAllocPBQP.cpp

## Inserting the prologue-epilogue code

Involves stack unwinding, finalizing the function layout, saving callee-saved registers and emitting the prologue and epilogue code. It also replaces abstract frame indexes with appriopriate refernces. This pass runs after the register application phase.

It runs on a machine function, hence it inherits the MachineFunctionPass class.

## Code emission

The code emission phase lowers the code from code genrator abstractions (such as `MachineFunction` class, `MachineInstr` class, and so on) to machine code layer abstractions (`MCInst` class, `MCStreamer` class, and soco). The important classes in this phase are the target-independent `AsmPrinter `class, target-specific subclasses of `AsmPrinter`, and the `TargetLoweringObjectFile` class.

- Define a subclass of the AsmPrinter class for the target
- Implement an instruction printer for the target.
- Implement code that lowers a MachineInstr class to an MCInst class, usually implemented in \<target\> MCInstLower.cpp.
- Implement a subclass of MCCodeEmitter that lowers MCInsts to machine code bytes and relocations

`AsmPrinter` base class: <lib/CodeGen/AsmPrinter/AsmPrinter.cpp>

- EmitLinkage(): This emits the linkage of the given variables or functions:

```c++
void AsmPrinter::EmitLinkage(const GlobalValue *GV, MCSymbol *GVSym) const ;
```

- EmitGlobalVariable(): This emits the specified global variable to the .s file:

```c++
void AsmPrinter::EmitGlobalVariable(const GlobalVariable *GV);
```

- EmitFunctionHeader(): This emits the header of the current function:

```c++
void AsmPrinter::EmitFunctionHeader();
```

- EmitFunctionBody(): This method emits the body and trailer of a function:

```c++
void AsmPrinter::EmitFunctionBody();
```

- EmitJumpTableInfo(): This prints assembly representations of the jump tables used by the current function to the current output stream:

```c++
void AsmPrinter::EmitJumpTableInfo();
```

- EmitJumpTableEntry(): This emits a jump table entry for the specified MachineBasicBlock class to the current stream:

```c++
void AsmPrinter::EmitJumpTableEntry(const MachineJumpTableInfo *MJTI, const MachineBasicBlock *MBB, unsigned UID) const;
```

- Emit integer types of 8, 16, or 32 bit size:

```c++
void AsmPrinter::EmitInt8(int Value) const { 
  OutStreamer.EmitIntValue(Value, 1); 
} 

void AsmPrinter::EmitInt16(int Value) const {
  OutStreamer.EmitIntValue(Value, 2); 
} 

void AsmPrinter::EmitInt32(int Value) const { 
  OutStreamer.EmitIntValue(Value, 4); 
}
```

## Tail call optimization

Tail call optimization is a technique where the callee reuses the stack of the caller instead of adding a new stack frame to the call stack, hence saving stack space and the number of returns when dealing with mutually recursive functions.

```shell
llc -tailcallopt tailcall.ll
```

> The tail call optimization is a compiler optimization technique, which a compiler can use to make a call to a function and take up no additional stack space; we don't need to create a new stack frame for this function call. This happens if the last instruction executed in a function is a call to another function. A point to note is that the caller function now does not need the stack space; it simply calls a function (another function or itself) and returns whatever value the called function would have returned. This optimization can make recursive calls take up constant and limited space. In this optimization, the code might not always be in the form for which a tail call is possible. It tries and modifies the source to see whether a tail call is possible or not.

## Sibling call optimisation

Sibling call optimization can be lookked at as an optimized tail call, the only constraint being that the functions should share a similar function signature, that is, matching return types and matching function arguments.

Write a case: the caller and the callee have the same `calling conventions`

```shell
$ cat sibcall.ll 
declare i32 @bar(i32, i32)

define i32 @foo(i32 %a, i32 %b, i32 %c) {
  entry:
  	%0 = tail call i32 @bar(i32 %a, i32 %b) 
  ret i32 %0
}
$ llc sibcall.ll
$ cat sibcall.s
		.text 
  	.file "sibcall.ll" 
  	.globl foo 
  	.align 16, 0x90 
  	.type foo,@function 
  foo:									# @foo
		.cfi_startproc 
 	# %bb.0:							# %entry
		jmp bar 						# TAILCALL					
  .Lfunc_end0:
		.size foo, .Lfunc_end0-foo 
    .cfi_endproc
												# -- End function
		.section		".note.GNU-stack","",@progbits
```

> Sibling call optimization works in a similar way to tail call optimization, except that the sibling calls are automatically detected and do not need any ABI changes. The similarity needed in the function signatures is because when the caller function (which calls a tail recursive function) tries to clean up the callee's argument, after the callee has done its work, this may lead to memory leak if the callee exceeds the argument space to perform a sibling call to a function requiring more stack space for arguments.

# Chap8: Writing an LLVM Backend

To generate the tartget code or assembly code which can be converted into object code and executed on the actual hardware, the compiler needs to know the various aspects of the architecture of the target machine - the registers, instruction set, calling convention, pupeline, and so on.

Define the target machine: using`tablegen` to specify the target registers, instructinos, calling conventions, and so on.

Pipeline structure for the backend: from the LLVM IR to SelectionDAG, then to MachineDAG, then to MachineInstr, and finally to MCInst.

​	LLVM IR --> SelectionDAG --> MachineDAG

CPUs execute a linear sequence of instructions. The goal of the scheduling step is to linearize the DAG by assigning an order to its operations.

The sample backend: a simple RISC-type architecture, with a few registers (r0 - r3), a stack pointer (sp), and a link register (lr), for storing the return address.

- Arguments passed to the function will be stored in register sets r0-r1, and the return value will be stored in r0.

## Defining registers and registers sets

Define registers and register sets in `.td` files. The `tablegen` function will convert this `.td` file into `.inc` file, which will be the #include declarative in our `.cpp` files and refer to registers.

1. Create a new folder in `lib/Target` named `TOY`:

```shell
$ mkdir llvm_root_directory/lib/Target/TOY
```

2. Create a new `TOYRegisterInfo.td` file in the new `TOY` folder:

```shell
$ cd llvm_root_directory/lib/Target/TOY 
$ vi TOYRegisterInfo.td

class TOYReg<bits<16> Enc, string n> : Register<n> { 
	let HWEncoding = Enc; 
	let Namespace = "TOY"; 
}

foreach i = 0-3 in {
	def R#i : R<i, "r"#i >;
}

def SP : TOYReg<13, "sp">;

def LR : TOYReg<14, "lr">;

def GRRegs : RegisterClass<"TOY", [i32], 32, (add R0, R1, R2, R3, SP)>;
```

`tablegen` function processes this `.td` file to generate the `.inc` file, which generally has enums generated for these registers. These enums can be used in the `.cpp` files, in which the registers can be referenced as `TOY::R0`. These .inc files will be generated when we build the LLVM project.

<lib/Target/ARM/ARMRegisterInfo.td>

## Defing the calling convention

The calling convention specifies how values are passed to and from a function call.

For our case, two arguments are passed in two registers, r0 and r1, while the remaing ones are passed to the stack. `ISelLoweing`

Define the calling convention in the `TOYCalingConv.td` file

	- Define the return value convention: how the return values will reside and in which registers
	- define the argument passing convention: specify how the arguments passes will reside and in which registers

