
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


# def ntt(arr, xs):
#     """
#     Number Theoretic Transform (NTT) of the sequence.
#     :param arr: Iterable sequence on which NTT is to be applied.
#     :param xs: Evaluation points (roots of unity).
#     :param P: Integer prime modulus for NTT.
#     :return: NTT of the sequence.
#     """
#     if len(arr) == 1:
#         return arr

#     n = len(arr) // 2
#     res0 = []
#     res1 = []
#     new_xs = []

#     for i in range(0, 2 * n, 2):
#         a = arr[i]
#         b = arr[i + 1]
#         x = xs[i]

#         res0.append((a + b) % P)
#         res1.append((a - b) * pow(2 * x, P - 2, P) % P)
#         new_xs.append(pow(x, 2, P))

#     return [sum(pair) % P for pair in zip(ntt(res0, new_xs), ntt(res1, new_xs))]

def ntt(arr, xs):
    n = len(arr)
    transform = [0] * n

    for i in range(n):
        transform[i] = sum(arr[j] * pow(xs[i], j, P) % P for j in range(n)) % P

    return transform


def some_algo_optimized(arr, xs):
    n = len(arr)
    transform = [0] * n
    mod_inv = [pow(x, P-2, P) for x in xs]  # Pre-compute modular inverses

    for i in range(n):
        xi_pow_j = 1  # Initialize to xs[i]**0
        for j in range(n):
            transform[i] += arr[j] * xi_pow_j
            xi_pow_j = (xi_pow_j * xs[i]) % P  # Update power for next iteration
        transform[i] %= P  # Apply modulo once per outer loop

    return transform
def optimized_ntt(arr, xs):
    """
    Number Theoretic Transform (NTT) of the sequence, optimized for speed.

    :param arr: Iterable sequence (polynomial coefficients) on which NTT is to be applied.
    :param xs: Precomputed evaluation points (roots of unity).
    :param P: Integer prime modulus for NTT.
    :return: NTT of the sequence.
    """
    n = len(arr)
    transform = [0] * n

    # Precompute powers of roots of unity (combine multiplication and modulo)
    powers_of_xs = [1] * n
    for i in range(1, n):
        powers_of_xs[i] = (powers_of_xs[i - 1] * xs[i]) % P

    # Unroll inner loop for potential cache locality improvement
    for i in range(n):
        s = 0
        j = 0
        while j < n:
            s = (s + arr[j] * powers_of_xs[(i * j) % n]) % P
            j += 2  # Process two elements per iteration for potential speedup

        transform[i] = s

    return transform
# gemini
def fft(arr, xs):
    if len(arr) == 1:
        return arr
    n = len(arr) // 2
    res0 = fft(arr[:n], xs[:n])
    res1 = fft(arr[n:], xs[:n])
    new_xs = [pow(x, -2, P) for x in xs[:n]]  # Invert roots of unity for FFT
    return [(a + b * x) / n for a, b, x in zip(res0, res1, new_xs)]

# chatgpt
# def fft(arr, xs):
#     if len(arr) == 1:
#         return arr
#     n = len(arr)
#     res_even = fft(arr[::2], xs[::2])
#     res_odd = fft(arr[1::2], xs[::2])  # Use the same roots of unity as in ifft
#     res = [0] * n
#     w = 1
#     for i in range(n // 2):
#         res[i] = (res_even[i] + w * res_odd[i]) % P
#         res[i + n // 2] = (res_even[i] - w * res_odd[i]) % P
#         w = (w * xs[1]) % P  # Update the roots of unity correctly
#     return res

# copilot
# def fft(arr, xs):
#     if len(arr) == 1:
#         return arr
#     n = len(arr) // 2
#     res0 = fft(arr[:n], xs[:n])
#     res1 = fft(arr[n:], xs[:n])
#     res = [0] * (2 * n)
#     for i in range(n):
#         res[i] = div_mod(res0[i] + xs[i] * res1[i], 1, P)
#         res[i + n] = div_mod(res0[i] - xs[i] * res1[i], 1, P)
#     return res

# Blob data taken from this blob on Goerli:
# https://etherscan.io/blob/0x017482460b39a8d4d52c22fee48adc76c2335cefdb2980fd6e3b7c65226ab171?bid=180082
# Read blob data from a file
with open('/Users/mohitdhattarwal/Desktop/madara-internship/madara-orch-test/test_blob_ 640641.txt', 'r') as file:
    blob_hex = file.read().strip()

# Convert the hexadecimal blob data to integers
data = [int(blob_hex[i:i+64], 16) for i in range(0, BLOB_LEN * 64, 64)]

# Write the data to a file, each integer on a new line
# with open("data_from_hex.txt", "w") as file:
#     for item in data:
#         file.write(str(item) + "\n")

# Generate the evaluation points xs
xs = [pow(z, int(bin(i)[2:].rjust(12, '0')[::-1], 2), P) for i in range(BLOB_LEN)]

# Perform IFFT on the data
res = ifft(data, xs)

# Write the state differences to a file
with open("state_diff_640641.txt", "w") as file:
    for item in res:
        file.write(str(item) + "\n")

# Perform FFT on the IFFT result
original_blob_hex = ntt(res, xs)

# Write the FFT result to a file
with open("data_just_after_ntt_640641.txt", "w") as file:
    for item in original_blob_hex:
        file.write(str(item) + "\n")

# # Convert the FFT result to a hexadecimal string
res = to_hex_string(original_blob_hex)

# # Perform IFFT on the FFT result to verify the original data is recovered
# reverse_res_data = ifft(original_blob_hex, xs)

# # Write the verification result to a file
# with open("state_diff_after_reverse_v3.txt", "w") as file:
#     for item in reverse_res_data:
#         file.write(str(item) + "\n")

# # Write the final hexadecimal string to a file
with open("should_original_blob_640641.txt", "w") as file:
    file.write(str(res) + "\n")



