class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        N = len(nums)
        dp = [1 for _ in range(N)]
        for start in range(N):
            for cand in range(start+1, N):
                if nums[start] < nums[cand]:
                    dp[cand] = max(1+dp[start], dp[cand])
        return max(dp)