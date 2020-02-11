#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @(#)microcode.py
# @author Karl Ljungkvist <k.ljungkvist@gmail.com>

import sys
import argparse

def assign(mem, addr, data):
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
#                              T0              T1         T2       T3       T4      T5  .  .
instructions['NOP']    = [PCO|MAI,    MDO|IRI|PCE,         0,       0,       0,      0, 0, 0]
instructions['HLT']    = [PCO|MAI,    MDO|IRI|PCE,       HLT,       0,       0,      0, 0, 0]
instructions['LDA(c)'] = [PCO|MAI,    MDO|IRI|PCE,   IMO|ARI,       0,       0,      0, 0, 0]
instructions['LDB(c)'] = [PCO|MAI,    MDO|IRI|PCE,   IMO|BRI,       0,       0,      0, 0, 0]
instructions['ADD']    = [PCO|MAI,    MDO|IRI|PCE,   ARI|ALU,       0,       0,      0, 0, 0]
instructions['OUT']    = [PCO|MAI,    MDO|IRI|PCE,   ARO|OUT,       0,       0,      0, 0, 0]
instructions['JMP(c)'] = [PCO|MAI,    MDO|IRI|PCE,   IMO|PCI,       0,       0,      0, 0, 0]


instruction_size = 8
eeprom_size = 2048
microcode = (eeprom_size//instruction_size)*instructions['NOP']

# opcodes 00, 08, 10, 18, 20, 28, ..., f0, f8
assign(microcode, 0x00, instructions['NOP'])
# LDA, LDB
assign(microcode, 0x08, instructions['LDA(c)'])
# assign(microcode, 0x08, instructions['LDA(i)'])
# assign(microcode, 0x08, instructions['LDA(a)'])
assign(microcode, 0x10, instructions['LDB(c)'])
# assign(microcode, 0x10, instructions['LDB(i)'])
# assign(microcode, 0x10, instructions['LDB(a)'])
assign(microcode, 0x40, instructions['ADD'])
# assign(microcode, 0x48, instructions['SUB'])
assign(microcode, 0x50, instructions['OUT'])
assign(microcode, 0x60, instructions['JMP(c)'])

assign(microcode, 0xf8, instructions['HLT'])

# microcode[0xf8:(0xf8+8)] = instructions['HLT']

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
            opcode = (row*8) & 0xf8
            flags  = ((row*8) & 0x700) >> 8
            print('  {:03b} {:02x}    {}'.format(flags, opcode,'\t'.join(format_code(c) for c in microcode[(row*8):(row*8+6)])))
    elif args.mode == 'low':
        microcode_low  = [c & 0xff for c in microcode]
        sys.stdout.buffer.write(bytes(microcode_low))
    else:
        microcode_high = [(c >> 8) for c in microcode]
        sys.stdout.buffer.write(bytes(microcode_high))
