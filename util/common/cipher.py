# coding=utf-8

# @Time    : 1/12/17 15:16
# @Author  :
# @File    : cipher.py
# @DES     : referer: http://kvz.io/blog/2009/06/10/create-short-ids-with-php-like-youtube-or-tinyurl/

# Copyright 2016 MoSeeker

import math
import hashlib

# A random created SECREAT ALPHABET sequence
ALPHABET = "xef3mghi68RpOPrsyQSFXNTqz0tuHIaVW5DMUEw2bcdYZ4v7JKLB1AjknCGl9"


def __alphaMeow(idnum, to_num=False, pad_up=False, passkey=None):
    index = ALPHABET
    if passkey:
        i = list(index)
        passhash = hashlib.sha256(passkey).hexdigest()
        passhash = hashlib.sha512(passkey).hexdigest() if len(passhash) < len(
            index) else passhash
        p = list(passhash)[0:len(index)]
        index = ''.join(zip(*sorted(zip(p, i)))[1])

    base = len(index)

    if to_num:
        idnum = idnum[::-1]
        out = 0
        length = len(idnum) - 1
        t = 0
        while True:
            bcpow = int(pow(base, length - t))
            out = out + index.index(idnum[t:t + 1]) * bcpow
            t += 1
            if t > length: break

        if pad_up:
            pad_up -= 1
            if pad_up > 0:
                out -= int(pow(base, pad_up))
    else:
        if pad_up:
            pad_up -= 1
            if pad_up > 0:
                idnum += int(pow(base, pad_up))

        out = []
        t = int(math.log(idnum, base))
        while True:
            bcp = int(pow(base, t))
            a = int(idnum / bcp) % base
            out.append(index[a:a + 1])
            idnum = idnum - (a * bcp)
            t -= 1
            if t < 0:
                break

        out = ''.join(out[::-1])

    return out

def encode_id(inputi, length=10):
    return __alphaMeow(inputi, pad_up=length)

def decode_id(inputs, length=10):
    if len(inputs) == 10:
        return __alphaMeow(inputs, to_num=True, pad_up=length)
    else:
        return inputs

if __name__ == '__main__':

    print (encode_id(13232))
    print (decode_id("0t3xx2xxxe"))
    print (decode_id("0t3xx2exxe5"))
