P = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001
# z is the generator of the group of evaluation points (EIP-4844 parameter)
z = 39033254847818212395286706435128746857159659164139250548781411570340225835782
BLOB_LEN = 4096

import numpy as np
from typing import List
import time


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

# @note: here is the start of another version of NTT and it's not working
def ntt(a, p):
  
  n = len(a)
  if n == 1:
    return a

  root = pow(g, (p - 1) // n, p)

  half = n // 2
  A0 = ntt(a[:half], p)
  A1 = ntt(a[half:], p)
  y = [0] * n
  for i in range(half):
    w = pow(root, i, p)
    y[i] = (A0[i] + w * A1[i]) % p
    y[i + half] = (A0[i] - w * A1[i]) % p
  return y

def inv_ntt(y, p):
  return ntt(y[::-1], p) 

def evaluate_ntt(a, x, p):

  n = len(a)
  x_NTT = ntt(x, p)  
  a_NTT = ntt(a, p) 
  y_NTT = [(a_NTT[i] * x_NTT[i]) % p for i in range(n)]

  return inv_ntt(y_NTT, p)
# @note: here is the end of another version of NTT and it's not working

# @note: this is the start of brute force algo
def classic_ntt(arr, xs):
    n = len(arr)
    transform = [0] * n

    for i in range(n):
        transform[i] = sum(arr[j] * pow(xs[i], j, P) % P for j in range(n)) % P

    return transform
# @note: this is the end of brute force algo

# @note: this is the start of the most optimized algo
def some_algo_optimized_v2(arr, xs):
    n = len(arr)
    transform = [0] * n

    for i in range(n):
        for j in reversed(range(n)):
            transform[i] = (transform[i] * xs[i] + arr[j]) % P

    return transform
# @note: this is the end of the most optimized algo


# @note: this is the start of the sligthly optimized algo
def some_algo_optimized(arr, xs):
    n = len(arr)
    transform = [0] * n

    for i in range(n):
        xi_pow_j = 1  
        for j in range(n):
            transform[i] += arr[j] * xi_pow_j
            xi_pow_j = (xi_pow_j * xs[i]) % P  
        transform[i] %= P 

    return transform
# @note: this is the start of the sligthly optimized algo


with open('./test_blob_ 640646.txt', 'r') as file:
    blob_hex = file.read().strip()

data = [int(blob_hex[i:i+64], 16) for i in range(0, BLOB_LEN * 64, 64)]

xs = [pow(z, int(bin(i)[2:].rjust(12, '0')[::-1], 2), P) for i in range(BLOB_LEN)]

res = ifft(data, xs)



g = 2  # Primitive root of unity (check for existence for different primes)

start_time = time.time()
result = evaluate_ntt(res, xs, P)
end_time = time.time()
print(f"evaluate_ntt took {end_time - start_time:.6f} seconds to calculate.")

# Start the timer for classic_ntt
start_time = time.time()
result2 = classic_ntt(res, xs)
with open("data_just_after_ntt_640646.txt", "w") as file:
    for item in result2:
        file.write(str(item) + "\n")
end_time = time.time()
print(f"classic_ntt took {end_time - start_time:.6f} seconds to calculate.")

# Start the timer for some_algo_optimized
start_time = time.time()
result3 = some_algo_optimized(res, xs)
end_time = time.time()
print(f"some_algo_optimized took {end_time - start_time:.6f} seconds to calculate.")

start_time = time.time()
result4 = some_algo_optimized_v2(res, xs)
end_time = time.time()
print(f"some_algo_optimized took {end_time - start_time:.6f} seconds to calculate.")

print("Is result equal for ev_ntt: ", result==result2)
print("Is result equal for optimized ntt: ", result3==result2)
print("Is result equal for optimized ntt v2: ", result4==result2)