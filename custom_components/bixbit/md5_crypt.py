"""Pure-Python implementation of the $1$ (md5-crypt) password hash.

This matches the glibc/passlib md5_crypt algorithm used by WhatsMiner
for its API token authentication. Avoids adding passlib as a dependency.
"""

from __future__ import annotations

import hashlib

_ITOA64 = b"./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_MAGIC = b"$1$"


def _to64(v: int, n: int) -> bytes:
    result = bytearray()
    for _ in range(n):
        result.append(_ITOA64[v & 0x3F])
        v >>= 6
    return bytes(result)


def md5_crypt(password: str, salt: str) -> str:
    """Compute a $1$ md5-crypt hash.

    Args:
        password: The plaintext password.
        salt: The salt string (without $1$ prefix, max 8 chars).

    Returns:
        The full hash string: $1$salt$hash
    """
    pwd = password.encode("utf-8") if isinstance(password, str) else password
    slt = salt.encode("utf-8") if isinstance(salt, str) else salt
    slt = slt[:8]

    # Digest A
    ctx = hashlib.md5(pwd + _MAGIC + slt)

    # Digest B
    ctx1 = hashlib.md5(pwd + slt + pwd)
    final = ctx1.digest()

    # Add B bytes based on password length
    plen = len(pwd)
    i = plen
    while i > 0:
        ctx.update(final[: min(i, 16)])
        i -= 16

    # Process password length bits
    i = plen
    while i:
        if i & 1:
            ctx.update(b"\x00")
        else:
            ctx.update(pwd[:1])
        i >>= 1

    final = ctx.digest()

    # 1000 rounds
    for i in range(1000):
        ctx1 = hashlib.md5()
        if i & 1:
            ctx1.update(pwd)
        else:
            ctx1.update(final)
        if i % 3:
            ctx1.update(slt)
        if i % 7:
            ctx1.update(pwd)
        if i & 1:
            ctx1.update(final)
        else:
            ctx1.update(pwd)
        final = ctx1.digest()

    # Encode
    rearranged = b""
    rearranged += _to64((final[0] << 16) | (final[6] << 8) | final[12], 4)
    rearranged += _to64((final[1] << 16) | (final[7] << 8) | final[13], 4)
    rearranged += _to64((final[2] << 16) | (final[8] << 8) | final[14], 4)
    rearranged += _to64((final[3] << 16) | (final[9] << 8) | final[15], 4)
    rearranged += _to64((final[4] << 16) | (final[10] << 8) | final[5], 4)
    rearranged += _to64(final[11], 2)

    return f"$1${slt.decode()}${rearranged.decode()}"
