"""
Definition of Interval:
class Interval(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
"""

class Solution:
    # def _binarySearchInsert(self, inserted: List[Interval], interval: Interval) -> int:
    #     # Return inserted index
    #     left = 0
    #     n = len(inserted)
    #     right = n-1
# 
    #     while left <= right:
    #         mid = ((right-left) // 2) + left
    #         if inserted[mid].end <= interval.start:
# 
    #     return mid

    def canAttendMeetings(self, intervals: List[Interval]) -> bool:
        n = len(intervals)
        intervals.sort(key=lambda x: x.start)


        prevL, furthestR = -1, -1
        for lr in intervals:
            l = lr.start
            r = lr.end
            if l <= prevL or l < furthestR:
                return False
            prevL = l

            if r > furthestR:
                furthestR = r
            else:
                return False

        return True
