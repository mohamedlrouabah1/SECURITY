import hashlib
import operator
import itertools

def generate_hmac(key, message, hash_algorithm='sha256'):
    block_size = 64  # Block size for SHA-1 and SHA-256

    # If the hash algorithm is SHA-512, adjust the block size
    if hash_algorithm == 'sha512':
        block_size = 128

    # If the key is longer than the block size, hash it
    if len(key) > block_size:
        key = hashlib.new(hash_algorithm, key).digest()

    # If the key is shorter than the block size, pad with zeros
    if len(key) < block_size:
        key += b'\x00' * (block_size - len(key))

    # XOR the key with the outer and inner pads
    o_key_pad = bytes(map(operator.xor, itertools.cycle(b'\x5c'), key))
    i_key_pad = bytes(map(operator.xor, itertools.cycle(b'\x36'), key))

    # Calculate the inner hash
    inner_hash = hashlib.new(hash_algorithm, i_key_pad + message).digest()

    # Calculate the outer hash
    outer_hash = hashlib.new(hash_algorithm, o_key_pad + inner_hash).digest()

    return outer_hash


def truncate_hmac_for_totp(hmac_value, code_length=6):
    """
    Truncate the HMAC value for TOTP protocol.

    Parameters:
    - hmac_value (bytes): The HMAC value to truncate.
    - code_length (int): The length of the TOTP code (default is 6).

    Returns:
    - int: The truncated TOTP code.
    """
    # Extract the last byte and the 4 least significant bits
    offset = hmac_value[-1] & 0x0F

    # Extract a portion of 4 bytes from the HMAC value based on the offset
    truncated_bytes = hmac_value[offset:offset + 4]

    # Apply a mask to get an unsigned big-endian int of 31 bits
    masked_value = int.from_bytes(truncated_bytes, byteorder='big') & 0x7FFFFFFF

    # Calculate the TOTP code using modulo 10^n
    totp_code = masked_value % (10 ** code_length)

    return totp_code
