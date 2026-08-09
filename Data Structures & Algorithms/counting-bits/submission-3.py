class Solution:
    def countBits(self, n: int) -> List[int]:
        out = [0 for _ in range(n+1)]
        for k in range(1, n+1):
            out[k] += (k & 1) + out[k >> 1]

        return out