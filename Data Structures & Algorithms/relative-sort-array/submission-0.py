from collections import Counter

class Solution:
    def relativeSortArray(self, arr1: List[int], arr2: List[int]) -> List[int]:
        counts = Counter(arr1)
        result = []
        for i in range(len(arr2)):
            num = arr2[i]
            count = counts[num]
            result += [num for _ in range(count)]
            del counts[num]

        for num in sorted(counts.keys()):
            result += [num for _ in range(counts[num])]
            
        return result