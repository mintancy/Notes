# 06/01/2020

- brk(): you know the address
- sbrk(): you don't know the address
- sbrk(NULL): get the address of the stack

All thumb2 instructions the last bit is 1.

# 05/15/2020
SP 20 notes
---
Session #1

NetCAT: attack

SPECCFI: a low overhead protection for spectre
- change call to call label (LLVM instruction instrumentation)
- check CFI
- convert indirect call/jmp to {load, tfence, call/jmp}
- convert ret to {pop, tfence, jmp}

symbolic execution

---

Session #2

1. Detection for sensor system. turn on and off the sensor

2. Isolation secure? against with side-channel: light on, light off
   - screen attack. PIN theft, :CS Response for PIN. key word, cursor, app type, pixel re-construction

3. SoK: A minimalist approach to Formalizing Analog snesor security

---

Session #4

cycles

check anything like pointer in the stack, BSS, Data, and Registers