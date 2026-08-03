class Solution:
    def countBits(self, n: int) -> List[int]:
        output = [0 for _ in range(n+1)]
        for k in range(1, n+1):
            count = 0
            num = k
            while num > 0:
                count += (num & 1)
                num >>= 1
            output[k] = count
        return output