from itertools import filterfalse
from collections import deque

class Solution:
    def islandPerimeter(self, grid: List[List[int]]) -> int:
        nrow, ncol = len(grid), len(grid[0])
        # down, right, up, left
        dirs = [(1,0), (0,1), (-1,0), (0,-1)]

        start = (-1,-1)
        for i in range(0, nrow):
            if start != (-1,-1):
                break

            if 1 not in grid[i]:
                continue

            for j in range(0, ncol):
                if grid[i][j] == 1:
                    start = (i, j)
                    break
            
        bfs = deque([start])
        seen = set()

        def is_water(rowcol):
            row, col = rowcol
            # out of bounds
            if row < 0 or row >= nrow:
                return True
            if col < 0 or col >= ncol:
                return True

            return grid[row][col] == 0

        perim = 0
        while bfs:
            curr = bfs.popleft()
            seen.add(curr)

            neighbors = list(filterfalse(is_water, [(curr[0]+xy[0], curr[1]+xy[1]) for xy in dirs]))
            perim += 4 - len(neighbors)

            for x in neighbors:
                if x not in seen:
                    bfs.append(x)
                    seen.add(x)
        
        return perim