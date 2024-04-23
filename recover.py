
# This script is a courtesy of @ArielElp
# It illustrates how to recover Starknet state diffs from an EIP-4844 blob.
# The script is not optimized for speed, and is intended for educational purposes only.

P = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001
# z is the generator of the group of evaluation points (EIP-4844 parameter)
z = 39033254847818212395286706435128746857159659164139250548781411570340225835782
BLOB_LEN = 4096

import numpy as np
from typing import List


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

def to_hex_string(fft_output: List[int]) -> str:
    return ''.join(format(num, 'x') for num in fft_output)

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

# Blob data taken from this blob on Goerli:
# https://etherscan.io/blob/0x017482460b39a8d4d52c22fee48adc76c2335cefdb2980fd6e3b7c65226ab171?bid=180082
# Read blob data from a file
with open('./blob4.txt', 'r') as file:
    blob_hex = file.read().strip()

# Convert the hexadecimal blob data to integers
data = [int(blob_hex[i:i+64], 16) for i in range(0, BLOB_LEN * 64, 64)]

# Write the data to a file, each integer on a new line
with open("data_from_hex.txt", "w") as file:
    for item in data:
        file.write(str(item) + "\n")

# Generate the evaluation points xs
xs = [pow(z, int(bin(i)[2:].rjust(12, '0')[::-1], 2), P) for i in range(BLOB_LEN)]

# Perform IFFT on the data
res = ifft(data, xs)

# Write the state differences to a file
with open("state_diff5.txt", "w") as file:
    for item in res:
        file.write(str(item) + "\n")

# Perform FFT on the IFFT result
original_blob_hex = fft(res, xs)

# Write the FFT result to a file
with open("data_just_after_fft.txt", "w") as file:
    for item in original_blob_hex:
        file.write(str(item) + "\n")

# Convert the FFT result to a hexadecimal string
res = to_hex_string(original_blob_hex)

# Perform IFFT on the FFT result to verify the original data is recovered
reverse_res_data = ifft(original_blob_hex, xs)

# Write the verification result to a file
with open("state_diff_after_reverse.txt", "w") as file:
    for item in reverse_res_data:
        file.write(str(item) + "\n")

# Write the final hexadecimal string to a file
with open("should_original_v2.txt", "w") as file:
    file.write(str(res) + "\n")



