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

minus_segm = (0 << 0) | (0 << 1) | (0 << 2) | (0 << 3) | (0 << 4) | (0 << 5) | (0 << 6) | (1 << 7) # -



import sys

data = [None]*2048

for i in range(256):
    # hexadecimal
    hexa = [hexsegm[i%16],
            hexsegm[(i//16)%16],
            hexsegm_off,
            hexsegm_off]

    # signed decimal
    if i > 127:
        add_minus_sign = True
        signed_abs = abs(i-256)
    else:
        add_minus_sign = False
        signed_abs = i

    signed_dec = [hexsegm[signed_abs%10],
                  hexsegm_off,
                  hexsegm_off,
                  hexsegm_off]

    if signed_abs>9:
        signed_dec[1] = hexsegm[(signed_abs//10)%10]
    elif add_minus_sign:
        signed_dec[1] = minus_segm
        add_minus_sign = False

    if signed_abs>99:
        signed_dec[2] = hexsegm[(signed_abs//100)%10]
    elif add_minus_sign:
        signed_dec[2] = minus_segm
        add_minus_sign = False

    if add_minus_sign:
        signed_dec[3] = minus_segm
        add_minus_sign = False

    # unsigned decimal
    unsigned_dec = [hexsegm[i%10],
                    hexsegm_off,
                    hexsegm_off,
                    hexsegm_off]
    if i>9:
        unsigned_dec[1] = hexsegm[(i//10)%10]
    if (i>99):
        unsigned_dec[2] = hexsegm[(i//100)%10]


    # write stuff

    # data[i]     = hexa[0]
    # data[256+i] = hexa[1]
    # data[512+i] = hexa[2]
    # data[768+i] = hexa[3]

    data[i]     = signed_dec[0]
    data[256+i] = signed_dec[1]
    data[512+i] = signed_dec[2]
    data[768+i] = signed_dec[3]

    data[1024+i] = unsigned_dec[0]
    data[1280+i] = unsigned_dec[1]
    data[1536+i] = unsigned_dec[2]
    data[1792+i] = unsigned_dec[3]


sys.stdout.buffer.write(bytes(data))

# Stuff for debug printing as ascii art

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
