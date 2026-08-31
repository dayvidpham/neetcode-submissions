class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        n = len(nums)
        if n == 0:
            return 0

        tail = len(nums)-1
        for i, x in enumerate(nums):
            while nums[tail] == val:
                tail -= 1
                if tail < 0:
                    return 0

            #print(i, nums)
            #print("\t",tail)
            #print(i, x, tail, nums[tail])
            if i > tail:
                return tail + 1
            if x == val:
                nums[i], nums[tail] = nums[tail], nums[i]
                tail -= 1
            #print(i, x, tail, nums[tail])
            #print(i, nums)
        
        return tail + 1