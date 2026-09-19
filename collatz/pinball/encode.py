"""Integer encoders: turning a state into feature bits and a launch integer.

A state (bit tuple, text, or JSON-like dict) becomes a tuple of 0/1 feature
bits. A member of the model reads those bits in its own order and launches
the odd integer n = 1 + sum(bit_i * 2^(i+1)). Hashing uses zlib.crc32, so the
whole pipeline is deterministic integer arithmetic.
"""

import re
import zlib

_TOKEN = re.compile(r"[a-z0-9]+|[^\sa-z0-9]")


def launch_integer(bits) -> int:
    """Pack bits LSB-first above a forced low 1 bit (the ball always hits a bumper).

    Example: launch_integer((0, 1)) = 0b101 = 5
    """
    n = 1
    for i, b in enumerate(bits):
        if b:
            n |= 1 << (i + 1)
    return n


def integer_bits(n: int, width: int) -> tuple[int, ...]:
    """Bits 1..width of n, LSB-first (bit 0 is the forced odd bit).

    Example: integer_bits(5, 3) = (0, 1, 0);  launch_integer((0, 1, 0)) = 5
    """
    return tuple((n >> (i + 1)) & 1 for i in range(width))


def text_tokens(text: str) -> list[str]:
    """Lowercased word/punctuation tokens plus adjacent-word bigrams."""
    words = _TOKEN.findall(text.lower())
    return words + [a + " " + b for a, b in zip(words, words[1:])]


def hash_bits(tokens, width: int = 256) -> tuple[int, ...]:
    """Set bit crc32(token) mod width for every token (a Bloom-style signature).

    Example: sum(hash_bits(["free", "call"], 64)) = 2
    """
    bits = [0] * width
    for tok in tokens:
        bits[zlib.crc32(tok.encode("utf-8")) % width] = 1
    return tuple(bits)


def encode_state(state, width: int = 256) -> tuple[int, ...]:
    """Encode a str, a dict of fields, or a ready-made bit sequence.

    Dict fields are hashed as "key=value" tokens, with text values tokenized
    under their key so the same word in different fields stays distinct.
    """
    if isinstance(state, str):
        return hash_bits(text_tokens(state), width)
    if isinstance(state, dict):
        tokens = []
        for key in sorted(state):
            value = state[key]
            if isinstance(value, str):
                tokens += [f"{key}:{t}" for t in text_tokens(value)]
            else:
                tokens.append(f"{key}={value!r}")
        return hash_bits(tokens, width)
    return tuple(1 if b else 0 for b in state)
