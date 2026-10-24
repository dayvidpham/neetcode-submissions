class Solution:
    def subsets(self, nums: List[int]) -> List[List[int]]:
        # each number here is a node
        # its index in nums, can use to form a lower triangular visitation pattern

        ret = []
        
        n = len(nums)
        stack = [([], -1, n)]


        while stack:
            pre, pos, rem = stack.pop()

            if rem == 0:
                ret.append(pre)
            else:
                stack.append((pre, pos+1, rem-1))
                stack.append( ([nums[pos+1]] + pre, pos+1, rem-1) )
                
        return ret