from collections import Counter

class Solution:
    def relativeSortArray(self, arr1: List[int], arr2: List[int]) -> List[int]:
        counts = Counter(arr1)
        ret = []
        for num in arr2:
            count = counts[num]
            ret += [num]*count
            del counts[num]

        ret += sorted(counts.elements())
        return ret