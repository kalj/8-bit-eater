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

class Microcode:
    def __init__(self, fetch_cycles):
        self.instructions = []
        self.fetch_cycles = fetch_cycles

    def push(self, opcode, mnemonic, micro_ops, **kwargs):
        matches = [i for i in self.instructions if mnemonic == i['mnemonic'] or opcode==i['opcode']]

        if len(matches) > 0:
            raise Exception("Cannot add instruction with mnemonic {}, and opcode {}. Conflicts with existing instruction(s): {}".format(mnemonic, opcode, matches))

        assert(len(micro_ops) > 0 and len(micro_ops) <= 4)

        instruction = {'mnemonic':mnemonic, 'opcode':opcode, 'micro_ops':micro_ops}

        if 'cf_ops' in kwargs:
            cf_ops = kwargs['cf_ops']
            assert(len(cf_ops) > 0 and len(cf_ops) <= 4)
            instruction['cf_micro_ops'] = cf_ops

        elif 'zf_ops' in kwargs:
            zf_ops = kwargs['zf_ops']
            assert(len(zf_ops) > 0 and len(zf_ops) <= 4)
            instruction['zf_micro_ops'] = zf_ops

        elif 'nf_ops' in kwargs:
            nf_ops = kwargs['nf_ops']
            assert(len(nf_ops) > 0 and len(nf_ops) <= 4)
            instruction['nf_micro_ops'] = nf_ops

        self.instructions.append(instruction)

    def _format_micro_ops(self,micro_ops, inc_fetcyc):
        if inc_fetcyc:
            micro_ops = self.fetch_cycles+micro_ops
        return '   '.join(format_code(c) for c in micro_ops)

    def print_uctable(self, include_fetch_cycles=True):
        code_width = len(format_code(0))
        mnem_width = max(len(i['mnemonic']) for i in self.instructions)
        cycles = range(2,6)
        if include_fetch_cycles:
            cycles = range(6)

        print(" op  {} f:xzc  {}".format(''.ljust(mnem_width),'   '.join(('T'+str(i)).ljust(code_width) for i in cycles)))

        for instr in sorted(self.instructions, key=lambda k:k['opcode']):
            opcode = instr['opcode']
            mnemonic = instr['mnemonic']
            micro_ops = instr['micro_ops']

            if 'cf_micro_ops' in instr:
                cf_ops = instr['cf_micro_ops']
                print(' {:02x}  {}   {}  {}'.format(opcode, mnemonic.ljust(mnem_width), '**0', self._format_micro_ops(micro_ops, include_fetch_cycles)))
                print('              {}  {}'.format('**1', self._format_micro_ops(cf_ops, include_fetch_cycles)))
            elif 'zf_micro_ops' in instr:
                zf_ops = instr['zf_micro_ops']
                print(' {:02x}  {}   {}  {}'.format(opcode, mnemonic.ljust(mnem_width), '*0*', self._format_micro_ops(micro_ops, include_fetch_cycles)))
                print('              {}  {}'.format('*1*', self._format_micro_ops(zf_ops, include_fetch_cycles)))
            elif 'nf_micro_ops' in instr:
                nf_ops = instr['nf_micro_ops']
                print(' {:02x}  {}   {}  {}'.format(opcode, mnemonic.ljust(mnem_width), '0**', self._format_micro_ops(micro_ops, include_fetch_cycles)))
                print('              {}  {}'.format('1**', self._format_micro_ops(nf_ops, include_fetch_cycles)))
            else:
                print(' {:02x}  {}   {}  {}'.format(opcode, mnemonic.ljust(mnem_width), '***', self._format_micro_ops(micro_ops, include_fetch_cycles)))

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
        for instr in self.instructions:
            for flags in range(8):
                addr = (instr['opcode'] << 3 ) | (flags << 8)
                micro_ops = instr['micro_ops']
                if flags & 1 and 'cf_micro_ops' in instr:
                    micro_ops = instr['cf_micro_ops']
                elif flags & 2 and 'zf_micro_ops' in instr:
                    micro_ops = instr['zf_micro_ops']
                elif flags & 4 and 'nf_micro_ops' in instr:
                    micro_ops = instr['nf_micro_ops']

                micro_ops = self.fetch_cycles+micro_ops
                blob[addr:(addr+len(micro_ops))] = micro_ops
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
    microcode.push(0x05, 'LDA(a)', [     PCO|MAI,   MDO|MAI|PCE,   MDO|ARI|PCE,    MIE])
    microcode.push(0x06, 'LDB(a)', [     PCO|MAI,   MDO|MAI|PCE,   MDO|BRI|PCE,    MIE])

    # STA                                     T2             T3             T4      T5
    microcode.push(0x07, 'STA(a)', [     PCO|MAI,   MDO|MAI|PCE,   MDI|ARO|PCE,    MIE])

    # ADD, SUB                                T2             T3             T4      T5
    microcode.push(0x08, 'ADD',    [     ARI|ALU,           MIE,             0,      0])
    microcode.push(0x09, 'SUB',    [ ARI|ALU|SUB,           MIE,             0,      0])

    # OUTPUT                                  T2             T3             T4      T5
    microcode.push(0x0a, 'OUT',    [     ARO|OUT,           MIE,             0,      0])

    # JUMP, BRANCH                            T2             T3             T4      T5
    microcode.push(0x0b, 'JMP(c)', [     IMO|PCI,           MIE,             0,      0]) #                   T2             T3             T4      T5
    microcode.push(0x0c, 'JMP(i)', [     PCO|MAI,       MDO|PCI,           MIE,      0]) #                   T2             T3             T4      T5
    microcode.push(0x0d, 'BRC(c)', [           0,           MIE,             0,      0], cf_ops = [     IMO|PCI,           MIE,             0,      0])
    microcode.push(0x0e, 'BRC(i)', [           0,           MIE,             0,      0], cf_ops = [     PCO|MAI,       MDO|PCI,           MIE,      0])
    microcode.push(0x0f, 'BRZ(c)', [           0,           MIE,             0,      0], zf_ops = [     IMO|PCI,           MIE,             0,      0])
    microcode.push(0x10, 'BRZ(i)', [           0,           MIE,             0,      0], zf_ops = [     PCO|MAI,       MDO|PCI,           MIE,      0])
    microcode.push(0x11, 'BRN(c)', [           0,           MIE,             0,      0], nf_ops = [     IMO|PCI,           MIE,             0,      0])
    microcode.push(0x12, 'BRN(i)', [           0,           MIE,             0,      0], nf_ops = [     PCO|MAI,       MDO|PCI,           MIE,      0])

    # HLT                                     T2             T3             T4      T5
    microcode.push(0x1f, 'HLT',    [         HLT,             0,             0,      0])


    parser = argparse.ArgumentParser(description='8-bit computer microcode generator')
    parser.add_argument('-m','--mode', help='Specify mode (table, or binary low or high byte of microcode)',choices=['isatable', 'uctable', 'low', 'high'], default='uctable')
    args = parser.parse_args()

    mc_blob = microcode.get_bytes()

    if args.mode == 'isatable':
        microcode.print_isatable()

    elif args.mode == 'uctable':
        microcode.print_uctable()

    elif args.mode == 'low':
        microcode_low  = [c & 0xff for c in mc_blob]
        sys.stdout.buffer.write(bytes(microcode_low))
    else:
        microcode_high = [(c >> 8) for c in mc_blob]
        sys.stdout.buffer.write(bytes(microcode_high))
