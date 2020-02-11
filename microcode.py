#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @(#)microcode.py
# @author Karl Ljungkvist <k.ljungkvist@gmail.com>

import sys
import argparse

HLT = 1 << 0
MAI = 1 << 1
MDI = 1 << 2
MDO = 1 << 3
IMO = 1 << 4
IRI = 1 << 5
ARI = 1 << 6
ARO = 1 << 7
ALU = 1 << 8
SUB = 1 << 9
BRI = 1 << 10
OUT = 1 << 11
CTE = 1 << 12
CTO = 1 << 13
JMP = 1 << 14
UKN = 1 << 15

instructions = {}
#                              T0              T1      T2       T3       T4      T5  .  .
instructions['NOP']    = [CTO|MAI,    MDO|IRI|CTE,      0,       0,       0,      0, 0, 0]
instructions['HLT']    = [CTO|MAI,    MDO|IRI|CTE,    HLT,       0,       0,      0, 0, 0]
# instructions['LDA(i)'] = [CTO|MAI,    MDO|IRI|CTE,    HLT,       0,       0,      0, 0, 0]
# instructions['LDA(a)'] = [CTO|MAI,    MDO|IRI|CTE,    HLT,       0,       0,      0, 0, 0]
# instructions['LDB(i)'] = [CTO|MAI,    MDO|IRI|CTE,    HLT,       0,       0,      0, 0, 0]
# instructions['LDB(a)'] = [CTO|MAI,    MDO|IRI|CTE,    HLT,       0,       0,      0, 0, 0]
# instructions['ADD']    = [CTO|MAI,    MDO|IRI|CTE,    HLT,       0,       0,      0, 0, 0]
# instructions['OUT']    = [CTO|MAI,    MDO|IRI|CTE,    HLT,       0,       0,      0, 0, 0]


instruction_size = 8
eeprom_size = 2048
microcode = (eeprom_size//instruction_size)*instructions['NOP']

# opcodes 00, 08, 10, 18, 20, 28, ..., f0, f8
microcode[0xf8:(0xf8+8)] = instructions['HLT']

def format_code(c):

    high = '{:08b}'.format(c >> 8)[::-1]
    low = '{:08b}'.format(c & 0xff)[::-1]
    return low+' '+high
    # return '{:04x}'.format(c)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='8-bit computer microcode generator')
    parser.add_argument('-m','--mode', help='Specify mode (table, or binary low or high byte of microcode.',choices=['table', 'low', 'high'], default='table')
    args = parser.parse_args()

    code_width = len(format_code(0))

    if args.mode == 'table':
        print("opcode\t{}".format('\t'.join(('T'+str(i)).ljust(code_width) for i in range(6))))
        for opcode in range(0,len(microcode),8):
            print('    {:02x}\t{}'.format(opcode,'\t'.join(format_code(c) for c in microcode[opcode:(opcode+6)])))
    elif args.mode == 'low':
        microcode_low  = [c & 0xff for c in microcode]
        sys.stdout.buffer.write(bytes(microcode_low))
    else:
        microcode_high = [(c >> 8) for c in microcode]
        sys.stdout.buffer.write(bytes(microcode_high))
