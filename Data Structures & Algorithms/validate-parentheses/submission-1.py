class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        pairs = {
            '{': '}',
            '(': ')',
            '[': ']'
        }

        for c in s:
            if c in pairs:
                stack.append(c)
            else:
                if not stack or pairs[stack[-1]] != c:
                    return False
                else:
                    stack.pop()
        
        return len(stack) == 0