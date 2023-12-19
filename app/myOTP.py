import base64
import hashlib
import operator
import itertools
import time
from datetime import datetime, timedelta

from config_otp import user_secrets

def get_rounded_time_to_nearest_half_minute():
    """
    Return the time rounded to the nearest 30 seconds.
    """
    current_time = datetime.now()
    half_minute = timedelta(seconds=30)
    return int(int(time.time()) // 30)


def generate_personnal_totp(user, key:str, code_length:int=6, hash_algorithm:str='sha256') -> int:
    """
    Generate an OTP code for the given key and counter.

    Parameters:
    - key str : A str of a base32 encoded key. (générated with pyotp.random_base32())
    - counter (int): The counter to use for OTP.
    - code_length (int): The length of the OTP code (default is 6).
    - hash_algorithm (str): The hash algorithm to use (default is SHA-1).

    Returns:
    - int: The OTP code.
    """
    current_time = get_rounded_time_to_nearest_half_minute()
    key = base64.b32decode(user_secrets[user]['TOTP'])
    message = current_time.to_bytes(8, byteorder='big')
    totp = generate_hmac(key, message)
    totp = truncate_hmac_for_totp(totp)

    return totp


def generate_personnal_hotp(user, key:str, counter:int, code_length:int=6, hash_algorithm:str='sha1') -> int:
    """
    Generate an OTP code for the given key and counter.

    Parameters:
    - key str : A str of a base32 encoded key. (générated with pyotp.random_base32())
    - counter (int): The counter to use for OTP.
    - code_length (int): The length of the OTP code (default is 6).
    - hash_algorithm (str): The hash algorithm to use (default is SHA-1).

    Returns:
    - int: The OTP code.
    """
    key = base64.b32decode(user_secrets[user]['HOTP'])
    message = counter.to_bytes(8, byteorder='big')
    hotp = generate_hmac(key, message)
    hotp = truncate_hmac_for_totp(hotp)

    return hotp

def generate_hmac(key, message, hash_algorithm='sha1') -> bytes:
    """
    Compute the HMAC value for the given key and message.

    Parameters:
    - key (bytes): The key to use for HMAC.
    - message (bytes): The message to authenticate.
    - hash_algorithm (str): The hash algorithm to use 
        (default is SHA-1 to match the one used by freeOTP app).
    """
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


def truncate_hmac_for_totp(hmac_value:bytes, code_length:int=6) -> int:
    """
    Truncate the HMAC value for TOTP protocol.

    Parameters:
    - hmac_value (bytes): The HMAC value to truncate.
    - code_length (int): The length of the TOTP code (default is 6).

    Returns:
    - int: The truncated TOTP code.
    """
    # Extract the last byte and the 4 least significant bits
    # i.e with do a binay AND with 00001111
    # wich will 'remove' the lefts 4 bits
    offset = hmac_value[-1] & 0x0F

    # Extract a portion of 4 bytes from the HMAC value based on the offset
    truncated_bytes = hmac_value[offset:offset + 4]

    # Apply a mask to get an unsigned big-endian int of 31 bits
    # help : For the mask (7)16 = (0111)2, i.e remove the sign bit
    masked_value = int.from_bytes(truncated_bytes, byteorder='big') & 0x7FFFFFFF

    # Calculate the TOTP code using modulo 10^n
    totp_code = masked_value % (10 ** code_length)

    return totp_code
