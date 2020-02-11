#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @(#)7-segment-hex-decode.py
# @author Karl Ljungkvist <k.ljungkvist@gmail.com>


# Segments to pins
#
#       (7)
#      -----  (6)
#     |     | /
#   / | (10)|
# (9)  -----  (4)
#     |     | /
#   / |     |
# (1)  -----  .--(5)
#       (2)
#
# Segments to bits
#
#       (5)
#      -----  (4)
#     |     | /
#   / | (7) |
# (6)  -----  (2)
#     |     | /
#   / |     |
# (0)  -----  .--(3)
#       (1)


# int to hexadecimal 7-segment

hexsegm_off = (0 << 0) | (0 << 1) | (0 << 2) | (0 << 3) | (0 << 4) | (0 << 5) | (0 << 6) | (0 << 7)

hexsegm = [(1 << 0) | (1 << 1) | (1 << 2) | (0 << 3) | (1 << 4) | (1 << 5) | (1 << 6) | (0 << 7), # 0
           (0 << 0) | (0 << 1) | (1 << 2) | (0 << 3) | (1 << 4) | (0 << 5) | (0 << 6) | (0 << 7), # 1
           (1 << 0) | (1 << 1) | (0 << 2) | (0 << 3) | (1 << 4) | (1 << 5) | (0 << 6) | (1 << 7), # 2
           (0 << 0) | (1 << 1) | (1 << 2) | (0 << 3) | (1 << 4) | (1 << 5) | (0 << 6) | (1 << 7), # 3
           (0 << 0) | (0 << 1) | (1 << 2) | (0 << 3) | (1 << 4) | (0 << 5) | (1 << 6) | (1 << 7), # 4
           (0 << 0) | (1 << 1) | (1 << 2) | (0 << 3) | (0 << 4) | (1 << 5) | (1 << 6) | (1 << 7), # 5
           (1 << 0) | (1 << 1) | (1 << 2) | (0 << 3) | (0 << 4) | (1 << 5) | (1 << 6) | (1 << 7), # 6
           (0 << 0) | (0 << 1) | (1 << 2) | (0 << 3) | (1 << 4) | (1 << 5) | (0 << 6) | (0 << 7), # 7
           (1 << 0) | (1 << 1) | (1 << 2) | (0 << 3) | (1 << 4) | (1 << 5) | (1 << 6) | (1 << 7), # 8
           (0 << 0) | (1 << 1) | (1 << 2) | (0 << 3) | (1 << 4) | (1 << 5) | (1 << 6) | (1 << 7), # 9
           (1 << 0) | (0 << 1) | (1 << 2) | (0 << 3) | (1 << 4) | (1 << 5) | (1 << 6) | (1 << 7), # A
           (1 << 0) | (1 << 1) | (1 << 2) | (0 << 3) | (0 << 4) | (0 << 5) | (1 << 6) | (1 << 7), # b
           (1 << 0) | (1 << 1) | (0 << 2) | (0 << 3) | (0 << 4) | (1 << 5) | (1 << 6) | (0 << 7), # C
           (1 << 0) | (1 << 1) | (1 << 2) | (0 << 3) | (1 << 4) | (0 << 5) | (0 << 6) | (1 << 7), # d
           (1 << 0) | (1 << 1) | (0 << 2) | (0 << 3) | (0 << 4) | (1 << 5) | (1 << 6) | (1 << 7), # E
           (1 << 0) | (0 << 1) | (0 << 2) | (0 << 3) | (0 << 4) | (1 << 5) | (1 << 6) | (1 << 7)  # F
           ]


import sys

data = [None]*2048

for i in range(256):
    data[i] = hexsegm[i%16]
    data[256+i] = hexsegm[(i//16)%16]
    data[512+i] = hexsegm_off
    data[768+i] = hexsegm_off

    data[1024+i] = hexsegm[i%10]
    data[1280+i] = hexsegm[(i//10)%10] if (i>9) else hexsegm_off
    data[1536+i] = hexsegm[(i//100)%10] if (i>99) else hexsegm_off
    data[1792+i] = hexsegm_off

def lines_from_7segm_digit(d0):
    lines = [ " "+ ("_____" if ((d0>>5) & 1) else "     "),
              ("|" if ((d0>>6)&1) else " ")+"     "+("|" if ((d0>>4)&1) else " "),
              ("|" if ((d0>>6)&1) else " ")+("_____" if ((d0>>7) & 1) else "     ")+("|" if ((d0>>4)&1) else " "),
              ("|" if ((d0>>0)&1) else " ")+"     "+("|" if ((d0>>2)&1) else " "),
              ("|" if ((d0>>0)&1) else " ")+("_____" if ((d0>>1) & 1) else "     ")+("|" if ((d0>>2)&1) else " ")+"  "+("." if ((d0>>3)&1) else " "),
    ]
    maxlen = max([len(l) for l in lines])
    lines = [l.ljust(maxlen) for l in lines]
    return lines

def print_7segm_number(d0,d1,d2):
    d0_lines = lines_from_7segm_digit(d0)
    d1_lines = lines_from_7segm_digit(d1)
    d2_lines = lines_from_7segm_digit(d2)

    lines = list(map(lambda l0,l1,l2: " ".join([l2,l1,l0]),d0_lines,d1_lines,d2_lines))

    for l in lines:
        print(l)


# decimal = True
# for i in range(256):

#     offset = 1024 if decimal else 0
#     print_7segm_number(data[offset+i],data[offset+256+i],data[offset+512+i])


sys.stdout.buffer.write(bytes(data))
