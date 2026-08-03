class Solution:
    def countBits(self, n: int) -> List[int]:
        output = [0 for _ in range(n+1)]
        for k in range(1, n+1):
            output[k] = (k & 1) + output[k >> 1]

        return output