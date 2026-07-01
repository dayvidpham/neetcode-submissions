class Solution:
    def canCompleteCircuit(self, gas: List[int], cost: List[int]) -> int:
        nets = [g-c for g, c in zip(gas, cost)]
        if sum(nets) < 0:
            return -1

        # guaranteed a solution. now linearized, can work left-to-right.
        start = 0
        tank = 0
        for i, net in enumerate(nets):
            if tank < 0:
                # reset from current
                start = i
                tank = 0
            tank += net
        return start