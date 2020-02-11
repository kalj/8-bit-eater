#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @(#)microcode.py
# @author Karl Ljungkvist <k.ljungkvist@gmail.com>

import sys
import argparse

def set_instruction(mem, opcode, data):
    addr = opcode << 3
    mem[addr:(addr+len(data))] = data

HLT = 1 << 0   # stop the clock
MAI = 1 << 1   # memory address in
MDI = 1 << 2   # memory data in
MDO = 1 << 3   # memory data out
IMO = 1 << 4   # instruction immediate out
IRI = 1 << 5   # instruction register in
ARI = 1 << 6   # A register in
ARO = 1 << 7   # A register out
ALU = 1 << 8   # perform ALU operation
SUB = 1 << 9   # enable subtraction in ALU
BRI = 1 << 10  # B register in
OUT = 1 << 11  # output register in
PCE = 1 << 12  # program counter enable
PCO = 1 << 13  # program counter out
PCI = 1 << 14  # program counter in
UKN = 1 << 15  # nothing

instructions = {}
#                              T0              T1            T2             T3             T4      T5  .  .
instructions['NOP']    = [PCO|MAI,    MDO|IRI|PCE,            0,             0,             0,      0, 0, 0]
instructions['HLT']    = [PCO|MAI,    MDO|IRI|PCE,          HLT,             0,             0,      0, 0, 0]
instructions['LDA(c)'] = [PCO|MAI,    MDO|IRI|PCE,      IMO|ARI,             0,             0,      0, 0, 0]
instructions['LDB(c)'] = [PCO|MAI,    MDO|IRI|PCE,      IMO|BRI,             0,             0,      0, 0, 0]
instructions['LDA(i)'] = [PCO|MAI,    MDO|IRI|PCE,      PCO|MAI,   MDO|ARI|PCE,             0,      0, 0, 0]
instructions['LDB(i)'] = [PCO|MAI,    MDO|IRI|PCE,      PCO|MAI,   MDO|BRI|PCE,             0,      0, 0, 0]
instructions['LDA(a)'] = [PCO|MAI,    MDO|IRI|PCE,      PCO|MAI,   MDO|MAI|PCE,   MDO|ARI|PCE,      0, 0, 0]
instructions['LDB(a)'] = [PCO|MAI,    MDO|IRI|PCE,      PCO|MAI,   MDO|MAI|PCE,   MDO|BRI|PCE,      0, 0, 0]
instructions['STA(a)'] = [PCO|MAI,    MDO|IRI|PCE,      PCO|MAI,   MDO|MAI|PCE,   MDI|ARO|PCE,      0, 0, 0]
instructions['ADD']    = [PCO|MAI,    MDO|IRI|PCE,      ARI|ALU,             0,             0,      0, 0, 0]
instructions['SUB']    = [PCO|MAI,    MDO|IRI|PCE,  ARI|ALU|SUB,             0,             0,      0, 0, 0]
instructions['OUT']    = [PCO|MAI,    MDO|IRI|PCE,      ARO|OUT,             0,             0,      0, 0, 0]
instructions['JMP(c)'] = [PCO|MAI,    MDO|IRI|PCE,      IMO|PCI,             0,             0,      0, 0, 0]
instructions['JMP(i)'] = [PCO|MAI,    MDO|IRI|PCE,      PCO|MAI,       MDO|PCI,             0,      0, 0, 0]


instruction_size = 8
eeprom_size = 2048
microcode = (eeprom_size//instruction_size)*instructions['NOP']

## Set the instructions
# opcodes 00, 01, 02, 03, ..., 0f, 10, 11, ..., 1e, 1f

# NOP
set_instruction(microcode, 0x00, instructions['NOP'])

# LDA, LDB
set_instruction(microcode, 0x01, instructions['LDA(c)'])
set_instruction(microcode, 0x02, instructions['LDB(c)'])
set_instruction(microcode, 0x03, instructions['LDA(i)'])
set_instruction(microcode, 0x04, instructions['LDB(i)'])
set_instruction(microcode, 0x05, instructions['LDA(a)'])
set_instruction(microcode, 0x06, instructions['LDB(a)'])

# STA
set_instruction(microcode, 0x07, instructions['STA(a)'])

# ADD, SUB
set_instruction(microcode, 0x08, instructions['ADD'])
set_instruction(microcode, 0x09, instructions['SUB'])

# OUTPUT
set_instruction(microcode, 0x0a, instructions['OUT'])

# JUMP, BRANCH
set_instruction(microcode, 0x0b, instructions['JMP(c)'])
set_instruction(microcode, 0x0c, instructions['JMP(i)'])

# HLT
set_instruction(microcode, 0x1f, instructions['HLT'])



def format_code(c):

    high = '{:08b}'.format(c >> 8)[::-1]
    low = '{:08b}'.format(c & 0xff)[::-1]
    return low+' '+high
    # return '{:04x}'.format(c)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='8-bit computer microcode generator')
    parser.add_argument('-m','--mode', help='Specify mode (table, or binary low or high byte of microcode)',choices=['table', 'low', 'high'], default='table')
    args = parser.parse_args()

    code_width = len(format_code(0))

    if args.mode == 'table':
        print("flags op    {}".format('\t'.join(('T'+str(i)).ljust(code_width) for i in range(6))))
        for row in range(len(microcode)//8):
            addr = row*8
            opcode = row & 0x1f
            flags  = ((addr) & 0x700) >> 8
            print('  {:03b} {:02x}    {}'.format(flags, opcode,'\t'.join(format_code(c) for c in microcode[addr:(addr+6)])))
    elif args.mode == 'low':
        microcode_low  = [c & 0xff for c in microcode]
        sys.stdout.buffer.write(bytes(microcode_low))
    else:
        microcode_high = [(c >> 8) for c in microcode]
        sys.stdout.buffer.write(bytes(microcode_high))
