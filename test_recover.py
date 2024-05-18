import math

P = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001

def fft(xs, nums):
    N = len(xs)
    if N == 1:
        return nums
    else:
        even_xs = xs[::2]
        odd_xs = xs[1::2]
        even_nums = fft(even_xs, nums[::2])
        odd_nums = fft(odd_xs, nums[1::2])
        factor = [pow(math.e, -2j * math.pi * k / N, P) for k in range(N // 2)]
        return [(even_nums[k] + factor[k] * odd_nums[k]) % P for k in range(N // 2)] + \
               [(even_nums[k] - factor[k] * odd_nums[k]) % P for k in range(N // 2)]

def ifft(xs, nums):
    N = len(xs)
    if N == 1:
        return nums
    else:
        even_xs = xs[::2]
        odd_xs = xs[1::2]
        even_nums = ifft(even_xs, nums[::2])
        odd_nums = ifft(odd_xs, nums[1::2])
        factor = [pow(math.e, 2j * math.pi * k / N, P) for k in range(N // 2)]
        return [((even_nums[k] + factor[k] * odd_nums[k]) % P) / 2 for k in range(N // 2)] + \
               [((even_nums[k] - factor[k] * odd_nums[k]) % P) / 2 for k in range(N // 2)]

# Example usage:
xs = [i for i in range(4096)]  # Replace with your actual evaluation points
z = 39033254847818212395286706435128746857159659164139250548781411570340225835782
xs = [pow(z, int(bin(i)[2:].rjust(12, '0')[::-1], 2), P) for i in range(4096)]
nums = [i for i in range(4096)]  # Replace with your actual data array
fft_result = fft(xs, nums)
ifft_result = ifft(xs, fft_result)

print(fft_result, ifft_result)
# The results are modulo P
