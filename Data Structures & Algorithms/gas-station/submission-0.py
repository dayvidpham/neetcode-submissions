class Solution:
    def canCompleteCircuit(self, gas: List[int], cost: List[int]) -> int:
        diffs = [g-c for g, c in zip(gas, cost)]
        if sum(diffs) < 0:
            return -1
            
        tank = -1
        ans = -1
        for i in range(len(diffs)):
            if tank < 0:
                ans = i
                tank = 0

            diff = diffs[i]
            tank += diff
            
        return ans