class Solution:
    def isPalindrome(self, s: str) -> bool:
        if len(s) == 1:
            return True

        s = s.lower()
        n = len(s)
        l = 0
        r = n-1

        ignore = lambda c: not c.isalnum()

        while l < r:
            while ignore(s[l]) and l < r:
                l += 1
            while ignore(s[r]) and r > l:
                r -= 1
            if s[l] != s[r]:
                return False

            l += 1
            r -= 1

        return True