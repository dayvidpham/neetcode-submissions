# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

class Solution:
    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:
        view = []
        if not root:
            return view

        dfs = [(root, 1)]
        while dfs:
            node, depth = dfs.pop()
            if len(view) < depth:
                view.append(node.val)
            
            if node.left:
                dfs.append((node.left, depth+1))
            if node.right:
                dfs.append((node.right, depth+1))

        return view