# MIT License
#
# Copyright (c) 2019 Michał Leszczyński
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import binascii
import io

from pycryptodome.Cipher import AES
from Crypto.Hash import CMAC


def calculate_sdmmac(sdm_file_read_key: bytes,
                     picc_data: bytes) -> bytes:
    """
    Calculate SDMMAC for NTAG 424 DNA
    :param sdm_file_read_key: MAC calculation key (K_SDMFileReadKey)
    :param picc_data: [ UID ][ SDMReadCtr ]
    :return: calculated SDMMAC (8 bytes)
    """
    sv2stream = io.BytesIO()
    sv2stream.write(b"\x3C\xC3\x00\x01\x00\x80")
    sv2stream.write(picc_data)

    while sv2stream.getbuffer().nbytes % AES.block_size != 0:
        # zero padding till the end of the block
        sv2stream.write(b"\x00")

    c2 = CMAC.new(sdm_file_read_key, ciphermod=AES)
    c2.update(sv2stream.getvalue())
    sdmmac = CMAC.new(c2.digest(), ciphermod=AES)

    return bytes(bytearray([sdmmac.digest()[i] for i in range(16) if i % 2 == 1]))


def validate_uid(uid):
    # Removing 0x if present
    uid = uid[2:] if uid[0:2] == "0x" else uid
    # Checking if length is 14
    if len(uid) != 14:
        raise InvalidUID("UID must be hexadecimal number of length 14")
    # Turning hexadecimal number to binary
    try:
        unhexed_uid = binascii.unhexlify(uid)
    except binascii.Error:
        raise InvalidUID("UID must be an hexadecimal number of length 14")

    return unhexed_uid


def validate_app_key(app_key):
    # Removing 0x if present
    app_key = app_key[2:] if app_key[0:2] == "0x" else app_key
    # Checking if length is 32
    if len(app_key) != 32:
        raise InvalidUID("UID must be hexadecimal number of length 32")
    # Turning hexadecimal number to binary
    try:
        unhexed_app_key = binascii.unhexlify(app_key)
    except binascii.Error:
        raise InvalidAppKey("UID must be an hexadecimal number of length 32")

    return unhexed_app_key


def validate_counter(counter):
    # Removing 0x if present
    counter = counter[2:] if counter[0:2] == "0x" else counter
    # Checking if length is 6
    if len(counter) != 6:
        raise InvalidUID("Counter must be an hexadecimal number of length 6")
    # Turning hexadecimal number to binary
    try:
        unhexed_counter = binascii.unhexlify(counter)
    except binascii.Error:
        raise InvalidCounter("Counter must be an hexadecimal number of length 6")

    return unhexed_counter


def calculate_cmac(uid, app_key, counter):
    unhexed_uid = validate_uid(uid)
    unhexed_app_key = validate_app_key(app_key)
    unhexed_ctr = validate_counter(counter)

    unhexed_ctr_ba = bytearray(unhexed_ctr)
    unhexed_ctr_ba.reverse()

    datastream = io.BytesIO()
    datastream.write(unhexed_uid)
    datastream.write(unhexed_ctr_ba)

    valid_cmac = calculate_sdmmac(unhexed_app_key, datastream.getvalue())

    return valid_cmac


def validate_cmac(uid, app_key, counter, cmac):
    try:
        unhexed_cmac = binascii.unhexlify(cmac)
    except binascii.Error:
        raise InvalidCMAC("CMAC must be an hexadecimal number.")

    valid_cmac = calculate_cmac(uid, app_key, counter)

    if unhexed_cmac != valid_cmac:
        raise MessageAuthenticationFailed("CMAC sent does not match Server-side CMAC calculation.")

    return valid_cmac


class InvalidUID(Exception):
    pass


class InvalidCounter(Exception):
    pass


class InvalidAppKey(Exception):
    pass


class InvalidCMAC(Exception):
    pass


class MessageAuthenticationFailed(Exception):
    pass
