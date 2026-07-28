class Solution:
    def hammingWeight(self, n: int) -> int:
        ones = 0
        while n > 0:
            if n & 1 == 1:
                ones += 1
            n >>= 1
        return ones