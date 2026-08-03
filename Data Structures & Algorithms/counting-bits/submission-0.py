class Solution:
    def countBits(self, n: int) -> List[int]:
        output = [0]
        for k in range(1, n+1):
            count = 0
            while k > 0:
                count += (k & 1)
                k >>= 1
            output.append(count)
        return output