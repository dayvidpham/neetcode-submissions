class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        if len(nums) == 1:
            return 1

        memo = [[-1 for _ in range(len(nums))] for _ in range(len(nums))]
        def dfs(curr: int, prev: int) -> int:
            # base case.
            # cannot iterate further: end of list
            if curr == len(nums):
                #print(f"dfs({curr}, {prev}), reached base case end of list")
                return 0

            if memo[curr][prev] != -1:
                #print(f"dfs({curr}, {prev}), using memo[({curr}, {prev})]: {memo[curr][prev]}")
                return memo[curr][prev]

            # three cases.
            # 1. start fresh from here.
            #   - dfs(curr, -1)
            #   - this is the base case. then we calculate dfs(curr, curr)
            # 2a. continue subseq, but don't take this curr
            #   - dfs(curr+1, prev)
            # 2b. continue subseq, but take this curr
            #   - 1 + dfs(curr+1, curr)
            #   - grew by 1, so +1

            # 2. continue subseq
            # 2a. don't take this curr
            skip = dfs(curr+1, prev)
            ret = skip
            if prev == -1 or nums[prev] < nums[curr]:
                # 2b. take this curr
                take = 1 + dfs(curr+1, curr)
                ret = max(skip, take)

            if ret > memo[curr][prev]:
                memo[curr][prev] = ret
            
            #print(f"\tdfs({curr}, {prev}), grew: {grew}, skip: {skip}, take: {take}, ret: {ret}")
            #print(memo)
            return ret

        return dfs(0, -1)