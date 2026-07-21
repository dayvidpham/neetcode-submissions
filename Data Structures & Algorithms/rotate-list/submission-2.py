# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def rotateRight(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        if not head or not head.next or k == 0:
            return head

        # walk first, get N
        N = 1
        tail = head
        newHead = head
        while tail.next:
            tail = tail.next
            N += 1

        # create cycle
        tail.next = head

        k = k % N
        k = N - k

        for i in range(k):
            newHead = newHead.next

        head = newHead
        tail = head
        for i in range(N-1):
            tail = tail.next
        tail.next = None

        return newHead