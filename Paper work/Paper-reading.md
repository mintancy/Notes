## S & P 2020

------------

### OAT: Attesting Operation Integrity of Embedded Devices

> Zhichuang Sun, Bo Feng, Long Lu (Northeastern University), Somesh Jha (University of Wisconsin)
>

**Concepts**

OEI: Operation Execution Integrity, including control-flow integrity and critical data integrity

OAT: remote OEI attestation

CPS: Cyber-Physical System



**Target**: IoT/CPS systems, embedded devices (IoT frontends).

**Senario**: The communication between IoT frontends and backends (controllers or servers).

**Problems**: IoT backends (controllers or servers) can not sure about the integrity of the communication.

**Main idea**: Remote contro-flow verification through abstract execution, which is fast and deterministic. Focusing on the execution of individual operations (hence the name)

**Purpose:** Enable IoT backends to reliably verify if an operation performed by a device has suffered from control or data attacks.

**Two challenges:**

- Incomplete verification of control-flow integrity
  - conventional hash-based attestation: small subset
  - *combines hashes and compact execution traces
- Heavy data integrity checking
  - address-based checking 
    - instrument every memory write instruction and some memory-read instructions
    - too heavy for embedded devices
  - *value-based define-use check
    - only covers critical variables which will affect the outcome of an operation
      - auto detecting ot annotated by developers
        - arm attribute

**Four components**: 

  - customized compiler
      - identifies the critical variables and instrument the code
  - trampoline library linked to attestation-enabled programs
  - runtime measurement engine
    		- processes the instrumented control-flow and data events and produces a proof or measurement (meets tOEI)
    		- ARM TrustZone: provides the TEE
  - remote/offline verification engine
    		- checks and determines if the operation execution meets the OEI

**Implementation:**

- Operation level

- HiKey board (**ARM CortexA53**)



---

### KARONTE: Detecting Insecure Multi-binary Interactions in Embedded Firmware

> Nilo Redini ∗ , Aravind Machiry ∗ , Ruoyu Wang † , Chad Spensky ∗ , Andrea Continella ∗ , Yan Shoshitaishvili † , Christopher Kruegel ∗ , and Giovanni Vigna ∗
>
> UC Santa Barbara † Arizona State University

**Concepts:**

IPC: Inter-process Communication (IPC) paradigms

binwalk: unpack the firmware image

Sinks: memcpy-like functions and attacker-controlled loops



**Target**: multi-binary embedded devices

**Problems:** unable to identify and adequately model the communication between the various executables. Previous work is to automatically identify vulnerabilities in firmware distributions, generally by unpacking them into analyzable components (analyzed in isolation). insufficient, and vulnerabilities persist.

- embedded devices are made up pf interconnected components. They are different binary excutables, or different modules of a large embedded OS, which interact to accomplish various tasks.

**Main idea:** Performs inter-binary data flow tracking to automatically detect insecure interactions among binaries of a firmware sample, ultimately discovering security vulnerabilities.

- Focuses on memory-corruption and DoS vunerabilities.
- Lies in the creation of its Binary Dependency Graph and its ability to accurately propagate taint information across binay boundries
- Focuses on inter-binary software bugs.
- Detects data-flows across binaries of a firmware sample

**Work flow:**

- Firmware Pre-processing: unpack the firmware sample (binwalk)
- Border Binaries Discovery: analyzes the unpacked firmware sample, and automaticallt retrives the set of binaries that exported the device functionality to the outside world.
  - identifies the set of binaries that export network services in a firmware sample from a network socket
  - three features to identify functions that implement parsers and other two additional features
    - the number of basic blocks
    - the number of branches
    - the number of conditional statements
    - network mark
    - connection mark
  - output: 
    - unpacked firmware sample
    - the set of identified network-facing binaries
    - the program locations containing memory comparisons against network-encoding keywords.
- Binary Dependency Graph Recovery: builds a directed graph that models communications among those binaries processing attacker-controlled data. (Communication Paradigm Finder, CPF)
  - inter-process interactions
    - CPF provides the necassary logic to detect and describe instances of a communication paradigm
      - Data key recovery
      - flow direction determination
      - binary set magnification
- Multi-binary Data-flow Analysis: leverages **static taint engine** to track how the data is propagated through the binary and collect the constaints that are applied to such data.
  - static taint engine
    - based on BootStomp
    - sumbolic execution
- Insecure Interactions Detection: identifies security issues cause by insecure attacker-controlled data flows.
  - Leverages the BFG to find dangerous data flows and detect subsets of two classes of vulnerabilities: memory-corruption bugs, and DoS
    - first find memcpy-like functions within a binary
    - then, if attacker-controlled data unsafety reaches a memcpy-like function, raise an alert
    - retrieve the conditions that control the iterations of a loop
    - check whether their truthfulness completely depends on attacker-controlled data, raise an alert
    - consider every disconnected node in the BFG, and perform a single-binary static analysis



---

### TrustZone Explained: Architectural Features and Use Cases

> Bernard Ngabonziza, Daniel Martin, Anna Bailey, Haehyun Cho and Sarah Martin
>
> Arizona State University

**Purpose:** overview the TrustZone technology on different ARM architectures and discuss the trend of using TrustZone.

ARMv7-A: VMSA (MMU)

ARMv7-R: PMSA (MPU)

ARMv7-M: PMSA (MPU)

Features:

- it has a large uniform register ﬁle; 
- data-processing operations only operate on registers, not directly on memory; 
- simple addressing modes; 
- instructions that combine a shift with an arithmetic and logical operation.

**TrustZone V.S. Secure Elemetn/TPM**

​	integrated

**Intel TX and SGX**

​	different hardware support

**TI M-Shield and AMD**

​	Another implementation of TZ: AMD uses TrustZone in its 64-bit Advanced Processing Units(APU’s). TI integrated TrustZone into its M-Shield Security framework used in the OMAP2 and OMAP3 processors

**Virtualization**

​	Both Hypervisor and TrustZone can be used for out of VM kernel monitoring.