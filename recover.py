
# This script is a courtesy of @ArielElp
# It illustrates how to recover Starknet state diffs from an EIP-4844 blob.
# The script is not optimized for speed, and is intended for educational purposes only.

P = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001
# z is the generator of the group of evaluation points (EIP-4844 parameter)
z = 39033254847818212395286706435128746857159659164139250548781411570340225835782
BLOB_LEN = 4096

import numpy as np
from typing import List


def to_hex_string(fft_output: List[int]) -> str:
    return ''.join(format(num, 'x') for num in fft_output)


def inverse_fft(res):
    # Perform IFFT on the result 'res'
    inverse_transform = np.fft.fft(res)
    
    # Convert the complex numbers to integers
    inverse_integers = np.round(inverse_transform).astype(int)
    
    # Convert the integers to hexadecimal strings
    blob_hex = ''.join(format(val, 'x').zfill(64) for val in inverse_integers)
    
    return blob_hex

def ifft(arr, xs):
    if len(arr) == 1:
        return arr
    n = len(arr) // 2
    res0 = []
    res1 = []
    new_xs = []
    for i in range(0, 2 * n, 2):
        a = arr[i]
        b = arr[i + 1]
        x = xs[i]
        res0.append(div_mod(a + b, 2, P))
        res1.append(div_mod(a - b, 2 * x, P))
        new_xs.append(pow(x, 2, P))
    return sum(zip(ifft(res0, new_xs), ifft(res1, new_xs)), ())

def div_mod(a, b, P):
    return (a * pow(b, P - 2, P)) % P


# def fft(arr, xs):
#     if len(arr) == 1:
#         return arr
#     n = len(arr) // 2
#     even_terms = fft(arr[0::2], xs[0::2])
#     odd_terms = fft(arr[1::2], xs[0::2])
#     combined = [0] * len(arr)
#     for i in range(n):
#         even = even_terms[i]
#         odd = odd_terms[i]
#         combined[i] = (even + odd * pow(xs[i], 1, P)) % P
#         combined[i + n] = (even - odd * pow(xs[i], 1, P)) % P
#     return combined


def fft(arr, xs):
    if len(arr) == 1:
        return arr
    n = len(arr) // 2
    res0 = fft(arr[:n], xs[:n])
    res1 = fft(arr[n:], xs[:n])
    res = [0] * (2 * n)
    for i in range(n):
        res[i] = div_mod(res0[i] + xs[i] * res1[i], 1, P)
        res[i + n] = div_mod(res0[i] - xs[i] * res1[i], 1, P)
    return res

# def fft(arr, xs):
#     if len(arr) == 1:
#         return arr
#     n = len(arr) // 2
#     res0 = fft(arr[:n], xs[:n])
#     res1 = fft(arr[n:], xs[:n])
#     res = [0] * (2 * n)
#     for i in range(n):
#         res[i] = (res0[i] + xs[i] * res1[i]) % P
#         res[i + n] = (res0[i] - xs[i] * res1[i]) % P
#     return res

# The div_mod function is not needed for the fft function

# Blob data taken from this blob on Goerli:
# https://goerli.blobscan.com/blob/0x01394306d3a5e6456771c2a4689e98269d220636723a877e44f19e11f6e57e6d
# Read blob_hex from a file
with open('./blob4.txt', 'r') as file:
    blob_hex = file.read().strip()

data = [int(blob_hex[i:i+64], 16) for i in range(0, BLOB_LEN * 64, 64)]
# print(data)
with open("data_from_hex.txt", "w") as file:
  for item in data:
    file.write(str(item) + "\n")
xs = [pow(z, int(bin(i)[2:].rjust(12, '0')[::-1], 2), P) for i in range(BLOB_LEN)]
res = ifft(data, xs)

with open("state_diff5.txt", "w") as file:
  for item in res:
    file.write(str(item) + "\n")


original_blob_hex = fft(res, xs)

with open("data_just_after_fft.txt", "w") as file:
  for item in original_blob_hex:
    file.write(str(item) + "\n")
res = to_hex_string(original_blob_hex)


# reverse_data = [int(res[i:i+64], 16) for i in range(0, BLOB_LEN * 64, 64)]
reverse_res_data = ifft(original_blob_hex, xs)

with open("state_diff_after_reverse.txt", "w") as file:
  for item in reverse_res_data:
    file.write(str(item) + "\n")
    
with open("should_original_v2.txt", "w") as file:
    file.write(str(res) + "\n")
# print("Original blob_hex:\n", original_blob_hex)
# print(res, len(res))



