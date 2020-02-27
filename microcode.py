#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @(#)microcode.py
# @author Karl Ljungkvist <k.ljungkvist@gmail.com>

import sys
import argparse

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
MIE = 1 << 15  # micro instruction end

def format_code(c):
    high = '{:08b}'.format(c >> 8)[::-1]
    low = '{:08b}'.format(c & 0xff)[::-1]
    return low+' '+high
    # return '{:04x}'.format(c)

def add_conditional_uops(instruction, kwargs):
    if 'cf_uops' in kwargs:
        cf_uops = kwargs['cf_uops']
        assert(len(cf_uops) > 0 and len(cf_uops) <= 4)
        instruction['cf_uops'] = cf_uops

    elif 'zf_uops' in kwargs:
        zf_uops = kwargs['zf_uops']
        assert(len(zf_uops) > 0 and len(zf_uops) <= 4)
        instruction['zf_uops'] = zf_uops

    elif 'nf_uops' in kwargs:
        nf_uops = kwargs['nf_uops']
        assert(len(nf_uops) > 0 and len(nf_uops) <= 4)
        instruction['nf_uops'] = nf_uops

class Microcode:
    def __init__(self, fetch_cycles):
        self.instructions = []
        self.fetch_cycles = fetch_cycles
        self.default_instruction = None

    def set_default(self, mnemonic, uops, **kwargs):
        self.default_instruction = {'mnemonic':mnemonic, 'uops':uops}
        add_conditional_uops(self.default_instruction, kwargs)

    def push(self, opcode, mnemonic, uops, **kwargs):
        matches = [i for i in self.instructions if mnemonic == i['mnemonic'] or opcode==i['opcode']]

        if len(matches) > 0:
            raise Exception("Cannot add instruction with mnemonic {}, and opcode {}. Conflicts with existing instruction(s): {}".format(mnemonic, opcode, matches))

        assert(len(uops) > 0 and len(uops) <= 4)

        instruction = {'mnemonic':mnemonic, 'opcode':opcode, 'uops':uops}

        add_conditional_uops(instruction,kwargs)

        self.instructions.append(instruction)

    def _format_uops(self,uops, inc_fetcyc):
        if inc_fetcyc:
            uops = self.fetch_cycles+uops
        return '   '.join(format_code(c) for c in uops)

    def print_uctable(self, print_default=False, include_fetch_cycles=True):
        code_width = len(format_code(0))
        mnem_width = max(len(i['mnemonic']) for i in self.instructions)
        cycles = range(2,6)
        if include_fetch_cycles:
            cycles = range(6)

        print(" op  {} f:xzc  {}".format(''.ljust(mnem_width),'   '.join(('T'+str(i)).ljust(code_width) for i in cycles)))

        for opcode in range(1<<5):
            matches = [i for i in self.instructions if i['opcode']==opcode]
            if len(matches) > 0:
                instr = matches[0]
            elif print_default and self.default_instruction:
                instr = self.default_instruction
            else:
                instr = None

            if instr:
                mnemonic = instr['mnemonic']
                uops = instr['uops']

                if 'cf_uops' in instr:
                    cf_uops = instr['cf_uops']
                    print(' {:02x}  {}   {}  {}'.format(opcode, mnemonic.ljust(mnem_width), '**0', self._format_uops(uops, include_fetch_cycles)))
                    print('              {}  {}'.format('**1', self._format_uops(cf_uops, include_fetch_cycles)))
                elif 'zf_uops' in instr:
                    zf_uops = instr['zf_uops']
                    print(' {:02x}  {}   {}  {}'.format(opcode, mnemonic.ljust(mnem_width), '*0*', self._format_uops(uops, include_fetch_cycles)))
                    print('              {}  {}'.format('*1*', self._format_uops(zf_uops, include_fetch_cycles)))
                elif 'nf_uops' in instr:
                    nf_uops = instr['nf_uops']
                    print(' {:02x}  {}   {}  {}'.format(opcode, mnemonic.ljust(mnem_width), '0**', self._format_uops(uops, include_fetch_cycles)))
                    print('              {}  {}'.format('1**', self._format_uops(nf_uops, include_fetch_cycles)))
                else:
                    print(' {:02x}  {}   {}  {}'.format(opcode, mnemonic.ljust(mnem_width), '***', self._format_uops(uops, include_fetch_cycles)))

    def print_isatable(self):
        code_width = len(format_code(0))
        mnem_width = max(len(i['mnemonic']) for i in self.instructions)

        for instr in sorted(self.instructions, key=lambda k:k['opcode']):
            opcode = instr['opcode']
            mnemonic = instr['mnemonic']
            prototype = "{:05b}:".format(opcode)
            if mnemonic[-3:] == '(c)':
                prototype+= "iii"
            else:
                prototype+= "***"
                if mnemonic[-3:] == '(i)':
                    prototype+= " iiiiiiii"
                elif mnemonic[-3:] == '(a)':
                    prototype+= " aaaaaaaa"

            print('{:6s} {:02x}    {}'.format(mnemonic, opcode, prototype))

    def get_bytes(self):
        eeprom_size = 2048
        blob = eeprom_size*[0]

        if self.default_instruction:
            instr = self.default_instruction
            for opcode in range(1 << 5):
                for flags in range(8):
                    addr = (opcode << 3 ) | (flags << 8)
                    uops = instr['uops']
                    if flags & 1 and 'cf_uops' in instr:
                        uops = instr['cf_uops']
                    elif flags & 2 and 'zf_uops' in instr:
                        uops = instr['zf_uops']
                    elif flags & 4 and 'nf_uops' in instr:
                        uops = instr['nf_uops']

                    uops = self.fetch_cycles+uops
                    blob[addr:(addr+len(uops))] = uops

        for instr in self.instructions:
            for flags in range(8):
                addr = (instr['opcode'] << 3 ) | (flags << 8)
                uops = instr['uops']
                if flags & 1 and 'cf_uops' in instr:
                    uops = instr['cf_uops']
                elif flags & 2 and 'zf_uops' in instr:
                    uops = instr['zf_uops']
                elif flags & 4 and 'nf_uops' in instr:
                    uops = instr['nf_uops']

                uops = self.fetch_cycles+uops
                blob[addr:(addr+len(uops))] = uops
        return blob


if __name__ == '__main__':


    fetch_cycles = [PCO|MAI,    MDO|IRI|PCE]
    microcode = Microcode(fetch_cycles)

    ## Set the instructions
    # opcodes 00, 01, 02, 03, ..., 0f, 10, 11, ..., 1e, 1f

    # NOP                                     T2             T3             T4      T5
    microcode.push(0x00, 'NOP',    [           0,           MIE,             0,      0])

    # LDA, LDB                                T2             T3             T4      T5
    microcode.push(0x01, 'LDA(c)', [     IMO|ARI,           MIE,             0,      0])
    microcode.push(0x02, 'LDB(c)', [     IMO|BRI,           MIE,             0,      0])
    microcode.push(0x03, 'LDA(i)', [     PCO|MAI,   MDO|ARI|PCE,           MIE,      0])
    microcode.push(0x04, 'LDB(i)', [     PCO|MAI,   MDO|BRI|PCE,           MIE,      0])
    microcode.push(0x05, 'LDA(a)', [     PCO|MAI,   MDO|MAI|PCE,       MDO|ARI,    MIE])
    microcode.push(0x06, 'LDB(a)', [     PCO|MAI,   MDO|MAI|PCE,       MDO|BRI,    MIE])

    # STA                                     T2             T3             T4      T5
    microcode.push(0x07, 'STA(c)', [     IMO|MAI,       MDI|ARO,           MIE,      0])
    microcode.push(0x08, 'STA(i)', [     PCO|MAI,   MDO|MAI|PCE,       MDI|ARO,    MIE])

    # ADD, SUB                                T2             T3             T4      T5
    microcode.push(0x09, 'ADD',    [     ARI|ALU,           MIE,             0,      0])
    microcode.push(0x0a, 'SUB',    [ ARI|ALU|SUB,           MIE,             0,      0])

    # OUTPUT                                  T2             T3             T4      T5
    microcode.push(0x0b, 'OUT',    [     ARO|OUT,           MIE,             0,      0])

    # JUMP, BRANCH                            T2             T3             T4      T5
    microcode.push(0x0c, 'JMP(c)', [     IMO|PCI,           MIE,             0,      0]) #                   T2             T3             T4      T5
    microcode.push(0x0d, 'JMP(i)', [     PCO|MAI,       MDO|PCI,           MIE,      0]) #                   T2             T3             T4      T5
    microcode.push(0x0e, 'BRC(c)', [           0,           MIE,             0,      0], cf_uops = [    IMO|PCI,           MIE,             0,      0])
    microcode.push(0x0f, 'BRC(i)', [           0,           MIE,             0,      0], cf_uops = [    PCO|MAI,       MDO|PCI,           MIE,      0])
    microcode.push(0x10, 'BRZ(c)', [           0,           MIE,             0,      0], zf_uops = [    IMO|PCI,           MIE,             0,      0])
    microcode.push(0x11, 'BRZ(i)', [           0,           MIE,             0,      0], zf_uops = [    PCO|MAI,       MDO|PCI,           MIE,      0])
    microcode.push(0x12, 'BRN(c)', [           0,           MIE,             0,      0], nf_uops = [    IMO|PCI,           MIE,             0,      0])
    microcode.push(0x13, 'BRN(i)', [           0,           MIE,             0,      0], nf_uops = [    PCO|MAI,       MDO|PCI,           MIE,      0])

    # HLT                                     T2             T3             T4      T5
    microcode.push(0x1f, 'HLT',    [         HLT,             0,             0,      0])
    microcode.set_default('HLT',   [         HLT,             0,             0,      0])


    parser = argparse.ArgumentParser(description='8-bit computer microcode generator')
    parser.add_argument('-m','--mode', help='Specify mode (table, or binary low or high byte of microcode)',choices=['isatable', 'uctable', 'low', 'high'], default='uctable')
    args = parser.parse_args()

    mc_blob = microcode.get_bytes()

    if args.mode == 'isatable':
        microcode.print_isatable()

    elif args.mode == 'uctable':
        microcode.print_uctable(print_default=True)

    elif args.mode == 'low':
        microcode_low  = [c & 0xff for c in mc_blob]
        sys.stdout.buffer.write(bytes(microcode_low))
    else:
        microcode_high = [(c >> 8) for c in mc_blob]
        sys.stdout.buffer.write(bytes(microcode_high))
