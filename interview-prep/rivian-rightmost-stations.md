# Rivian Interview Kit — “Camera on the Right Wall” (Assembly-Line Visibility)

> **INTERVIEWER-ONLY DOCUMENT.** Do not screen-share this file. Section 1 is the
> candidate-safe material; sections 2–9 are the answer key, rubric, and test
> harness.

**Problem codename:** `rivian-rightmost-stations`
**Input shape:** `Optional[Workstation]`; each workstation has an integer
`station_id` and optional `left` / `right` downstream lane links
**Style:** verbally described problem, empty CodeShare editor
**Language:** Python 3
**Topics:** hierarchical data, breadth-first search, depth-first search with
depth tracking, level-order traversal
**Difficulty:** LeetCode Medium (interviewer mapping in §8)
**Target complexity:** O(n) time; O(n) worst-case space (or O(h) with DFS)
**Expected duration:** 30–40 minutes including follow-ups

---

## Table of contents

- [TL;DR](#tldr)
- [0. How to use this kit](#0-how-to-use-this-kit)
- [1. Candidate-facing material](#1-candidate-facing-material)
- [2. Reference solutions](#2-reference-solutions)
- [3. Interviewer answer key](#3-interviewer-answer-key)
- [4. Follow-ups](#4-follow-ups)
- [5. Scoring rubric](#5-scoring-rubric)
- [6. Mock dialogue](#6-mock-dialogue)
- [7. Test harness](#7-test-harness)
- [8. Problem family and difficulty tuning](#8-problem-family-and-difficulty-tuning)
- [9. Appendix: verification log](#9-appendix-verification-log)

---

## TL;DR

The candidate hears the problem verbally and gets an empty CodeShare, so the
*clarifying questions are part of the test*. The input is the first
`Workstation` in the line. The answer is the **rightmost workstation at each
stage**, top to bottom.

Core solution: level-order BFS and take the last workstation of each stage; or
a right-first DFS that records the first workstation seen at each new stage.
O(n) time.

The trap is that “rightmost” is **not** “always take the right-hand link.” A
workstation can be the rightmost one at its stage even if it sits in a left-hand
branch, when the right-hand side of the line ends sooner. Following only
right-hand links gives the wrong answer on layouts like:

```text
    10
   /  \
  20   30
  /
 40
```

Stage 3 contains only `40`, so the camera sees `40`; following the right-hand
links alone would return `[10, 30]` and miss it.

Hidden traps:

| Trap | What it catches |
|---|---|
| Following only right-hand links | Candidates who assume “rightmost” means “keep taking `.right`” |
| A left-hand branch deeper than the right | Missing workstations produced entirely by left-hand branches |
| Empty line | Indexing `start` before the `None` check |
| Unbalanced / left-only layout | Stage assumptions from full layouts |
| Returning workstations instead of IDs | Contract mismatch |
| Wrong order | Returning bottom-up or grouped by branch |
| Very deep line | Blind recursion / RecursionError |

Reference solutions: §2. Answer key: §3. Rubric: §5.

---

## 0. How to use this kit

| Section | Audience | Purpose |
|---|---|---|
| §1 | Candidate (read aloud / paste) | The problem as delivered |
| §2 | Interviewer | Reference implementations and complexity |
| §3 | Interviewer | Clarifications, omissions, hidden tests, hint ladder |
| §4 | Interviewer | Follow-ups if the candidate finishes early |
| §5 | Interviewer | Hire / no-hire calibration |
| §6 | Interviewer | Example dialogue and nudges |
| §7 | Interviewer | Ready-to-run tests and fuzzers |
| §8 | Interviewer | Related problems and difficulty knobs |
| §9 | Interviewer | Verification evidence for the code in this doc |

**Suggested time budget**

| Phase | Minutes |
|---|---|
| Read the problem, candidate asks questions | 3–5 |
| Candidate codes and explains | 12–18 |
| Candidate tests / walks through example | 5 |
| One or two follow-ups | 5–10 |
| Buffer / candidate questions | remainder |

**What you need open:** an empty CodeShare (or equivalent), this doc, and the
layout diagram in §1.2 to draw or paste. Optionally keep the test harness in §7
ready in a local terminal if you want to run their submission automatically.

---

## 1. Candidate-facing material

### 1.1 What you say out loud (60–90 seconds)

> Let’s do a Python problem. You’re a software engineer at Rivian, working on
> the system that monitors the assembly line. The line is made up of
> workstations. Each workstation has an integer station ID, and up to two
> workstations directly downstream of it: one in the left lane and one in the
> right lane.
>
> The first workstation is stage 1; its immediate downstream workstations are
> stage 2; theirs are stage 3; and so on. A fixed camera on the right wall of
> the plant sees, at each stage, only the rightmost workstation — everything
> further left at that stage is blocked from view.
>
> Given the first workstation in the line, return the station IDs the camera
> sees, ordered from the first stage to the last stage.
>
> Here’s an example. *(draw/paste the layout from §1.2)* The camera sees 10,
> 30, and 50. You’ll be writing it in the empty editor here. Any questions
> before you start?

**Do not** volunteer: the empty-line behavior, that the line may be very
unbalanced, that left-hand branches can supply the rightmost workstation at a
stage, or the input size. Those are the deliberate gaps — see §3.2.

### 1.2 Worked example (draw or paste this)

```text
          10
         /  \
       20    30
         \     \
         40    50
```

Stages and camera view:

| Stage | Workstations at that stage | Camera sees |
|---:|---|---:|
| 1 | 10 | 10 |
| 2 | 20, 30 | 30 |
| 3 | 40, 50 | 50 |

Return:

```text
[10, 30, 50]
```

### 1.3 Paste-ready stub (recommended)

Paste this into the empty editor so the candidate focuses on the algorithm
rather than on typing boilerplate. The `self`/`class Solution` shape matches
the LeetCode-style example you already have.

```python
from typing import List, Optional


class Workstation:
    def __init__(self, station_id: int, left=None, right=None):
        self.station_id = station_id
        self.left = left
        self.right = right


class Solution:
    def rightmostStations(self, start: Optional[Workstation]) -> List[int]:
        ...
```

### 1.4 Paste-ready statement (Python docstring version)

If you want the written prompt above the stub, use a docstring or `#`
comments. The `/* ... */` block from your charging example is not valid Python
and would break if the CodeShare file is ever executed or linted.

```python
r"""
You're a software engineer at Rivian, working on the system that monitors the
assembly line.

The line is made up of workstations. Each workstation has an integer station ID
and up to two workstations directly downstream of it: one in the left lane and
one in the right lane.

The first workstation is stage 1; its immediate downstream workstations are
stage 2; theirs are stage 3; and so on.

A fixed camera on the right wall of the plant sees, at each stage, only the
rightmost workstation -- every workstation further left at that stage is
blocked from view.

Given the first workstation in the line, return the station IDs the camera
sees, ordered from the first stage to the last stage.

Example:
            10
           /  \
         20    30
           \     \
           40    50

Return: [10, 30, 50]
"""
```

### 1.5 If the candidate asks for a second example

Give this simple three-workstation layout. It confirms the stage-by-stage
idea without leaking the deeper-left-branch trap.

```text
    10
   /  \
  20   30

=> [10, 30]
```

### 1.6 What to do once they start coding

- **Default:** paste the stub from §1.3 and let them fill in
  `rightmostStations`.
- **If you also want to evaluate API/design:** give only the verbal
  description and let them ask how workstations are represented. Then answer
  from §3.1.
- **If they ask to write a `main`/tests:** fine; do not stop them, but keep
  them focused on the function. The clock is for the algorithm.

### 1.7 Candidate-facing constraints (only if pressed)

If they insist on constraints before coding, you may say:

> Assume the layout is valid: each workstation appears once, the line never
> loops back on itself, and the left/right lane links are either `None` or
> another workstation. Station IDs are integers and may be negative. The first
> workstation may be missing. You don’t need to validate anything.

Do **not** say “the line can be very unbalanced” or “a workstation in a
left-hand branch can be the rightmost at its stage.” Those are the assumptions
a strong candidate should surface — see §3.2.

---

## 2. Reference solutions

All solutions assume `Workstation` from §1.3 is already defined.

### 2.1 Primary solution — level-order BFS

Process the tree one level at a time. The last node dequeued on each level is
the one the camera sees.

```python
from collections import deque
from typing import List, Optional


class Solution:
    def rightmostStations(self, root: Optional[Workstation]) -> List[int]:
        if root is None:
            return []

        result: List[int] = []
        queue = deque([root])

        while queue:
            level_size = len(queue)
            for i in range(level_size):
                node = queue.popleft()

                # Last node in this level is the rightmost one.
                if i == level_size - 1:
                    result.append(node.station_id)

                if node.left is not None:
                    queue.append(node.left)
                if node.right is not None:
                    queue.append(node.right)

        return result
```

**Why it works:** BFS visits all nodes at depth `d` before any node at depths
greater than `d`. Within a level, nodes are dequeued left-to-right, so the
last one is the rightmost.

**Complexity**

- Time: O(n) — each node enters and leaves the queue once.
- Space: O(w) where `w` is the maximum width of the tree; worst case O(n) for
  the last level.

### 2.2 Alternative — DFS, right child first

Keep track of the first node visited at each depth. Because the traversal
visits `right` before `left`, that first node is the rightmost one at its
depth. No queue and no explicit level loop.

```python
from typing import List, Optional


class Solution:
    def rightmostStations(self, root: Optional[Workstation]) -> List[int]:
        result: List[int] = []

        def dfs(node: Optional[Workstation], depth: int) -> None:
            if node is None:
                return
            if depth == len(result):
                # First node reached at this depth; right-first order makes
                # it the rightmost node at this depth.
                result.append(node.station_id)
            dfs(node.right, depth + 1)
            dfs(node.left, depth + 1)

        dfs(root, 0)
        return result
```

**Why it works:** a preorder traversal that explores the right subtree first
visits the rightmost node of depth `d` before any other node at depth `d`.
The `depth == len(result)` test means “this is the first time we have reached
this depth,” so we record exactly one node per depth.

**Complexity**

- Time: O(n) — every node is visited once.
- Space: O(h) for the recursion stack plus O(h) for the result, where `h` is
  the height. Worst case O(n) for a skewed tree.
- **Recursion limit:** a 5,000-node right chain raises `RecursionError` at
  Python’s default limit; use §2.3 or BFS if deep trees are in scope.

### 2.3 Iterative DFS, right child first (deep-tree safe)

The same right-first idea with an explicit stack. Push `left` before `right`
so that `right` is popped first.

```python
from typing import List, Optional


class Solution:
    def rightmostStations(self, root: Optional[Workstation]) -> List[int]:
        result: List[int] = []
        stack = [(root, 0)]

        while stack:
            node, depth = stack.pop()
            if node is None:
                continue

            if depth == len(result):
                result.append(node.station_id)

            # Push left first, then right, so right is processed first.
            stack.append((node.left, depth + 1))
            stack.append((node.right, depth + 1))

        return result
```

**Complexity:** O(n) time; O(h) stack space in the best case, O(n) worst case.
No Python recursion limit.

**Your original accepted submission.** The version that passed the original
LeetCode problem uses the standard `TreeNode` and `val`. It is the same
algorithm, with a 1-based depth and `len(view) < depth` instead of
`depth == len(result)`:

```python
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
```

Why the stack order matters: `left` is pushed before `right`, so `right` is
popped first. The first node reached at each depth is therefore the rightmost
one, and `len(view) < depth` records exactly that node. In this kit’s node
type, `node.val` becomes `node.station_id`; the 0-based variant above is the
same traversal. This exact submission was verified against the kit’s 10
deterministic cases, 5,000 random trees, and the 5,000-node chain (§9).

### 2.4 Comparison

| Approach | Time | Space | Pros | Cons |
|---|---:|---:|---|---|
| Level-order BFS | O(n) | O(width), worst O(n) | Directly matches the definition; easy to explain | Queue can hold a full level |
| Recursive DFS, right first | O(n) | O(height) | Short; elegant depth invariant | RecursionError on deep trees |
| Iterative DFS, right first | O(n) | O(height) | Same invariant, no recursion limit | Slightly less obvious ordering |
| Follow only `.right` pointers | O(height) | O(height) | Very fast | **Wrong** on unbalanced trees — not a valid solution |

**Expected interview answer:** 2.1 first (it matches the mental model), then
mention 2.2 as a space-efficient alternative when asked. A candidate who
immediately reaches for right-first DFS with the `depth == len(result)`
invariant is strong.

### 2.5 What a clean final solution looks like

- Empty check before touching `root.left` / `root.right`.
- One traversal, O(n), not one traversal per level recomputed.
- Uses actual tree depth, not the count of right children.
- Appends exactly one ID per non-empty level, in root-to-deepest order.
- Handles a node with only a left child, and a left subtree that is deeper
  than the right subtree.
- States the complexity and, if recursive, mentions the depth risk.
- Returns `[]` for `root is None` without a special-case crash.

### 2.6 The right-spine trap, concretely

```text
        10
       /  \
     20    30
     /
   40
```

- Following right children from the root: `10 → 30`; then stop. Result would be
  `[10, 30]`.
- Correct right-side view: level 0 = `10`; level 1 = `20, 30` → `30`; level 2 =
  `40` (only node, in the left subtree) → `40`. Result `[10, 30, 40]`.

This tree (`[10, 20, 30, 40]` in level-order) should be one of your first
hidden tests.

---

## 3. Interviewer answer key

### 3.1 Clarifying questions and intended answers

Award credit for questions that remove a real ambiguity, not for checkbox
questions. These are the ones that matter:

| Candidate asks | Answer to give | Why it matters |
|---|---|---|
| What is the input type? | The first `Workstation` in the line; each has an ID and two optional downstream lanes | They need to know the workstation shape |
| Should I define `Workstation`, or is it provided? | It’s provided in the stub: `station_id`, `left`, `right` | Avoids time lost inventing a class |
| What exactly does “seen from the right” mean? | The rightmost workstation at each stage, one per stage | Core definition |
| Is it the rightmost workstation globally or per stage? | Per stage, ordered from the first stage downward | Catches “right-hand link” misreadings |
| If a stage’s workstations come only from left-hand branches, are they visible? | Yes — the rightmost one at that stage is visible | The subtle trap |
| What should I return? | `List[int]` of `station_id`s, stage order | Catches returning workstations |
| What about an empty line? | Return `[]` | Tests the `None` guard |
| Can the line be unbalanced or left-only? | Yes; do not assume every stage is full | Catches full-line shortcuts |
| Can station IDs be negative? | Yes, they are arbitrary integers | Catches sentinel/`None` confusion |
| How large can the line be? | Up to ~10^5 workstations; it can be very deep | Invites complexity and recursion discussion |
| Are IDs unique? | Assume unique, but the algorithm doesn’t need it | Confirms output contract |

If they ask something not covered, answer consistently with “valid line layout,
return rightmost `station_id` per stage, empty line returns `[]`.”

### 3.2 Deliberate omissions

The spoken prompt intentionally leaves these out. Reveal them only when asked
or when they become relevant to a failing test.

| Omitted detail | Intended answer | Reveal when |
|---|---|---|
| Empty line | `[]` | They don’t guard `start is None`, or ask |
| Left-hand branches can supply a stage’s rightmost workstation | Yes, the per-stage rule wins | They follow only right-hand links, or ask |
| The line may be very unbalanced | Yes | They assume every stage is full |
| Input size / depth | Up to ~10^5, possibly very deep | They state complexity or choose recursion |
| ID sign | Arbitrary integers, may be negative | They assume positive IDs |
| Output order | First stage first, then downward | They start returning bottom-up |

The workstation/lane representation is **not** omitted: it is stated verbally
and in the stub, because the code can’t be written without it.

### 3.3 Hidden test cases and expected outputs

Use these after their solution passes the sample. The point is not to trick
them with exotic input; it is to test the assumptions they did or did not
surface.

| # | Case | Level-order input | Expected |
|---|---|---|---|
| 1 | Empty | `[]` | `[]` |
| 2 | Single node | `[10]` | `[10]` |
| 3 | Sample | `[10, 20, 30, None, 40, None, 50]` | `[10, 30, 50]` |
| 4 | Right-spine trap | `[10, 20, 30, 40]` | `[10, 30, 40]` |
| 5 | Only-right chain | `[10, None, 20]` | `[10, 20]` |
| 6 | Right subtree shallower | `[10, 20, 30, None, 40]` | `[10, 30, 40]` |
| 7 | Left-only chain | `[10, 20, None, 30, None, 40]` | `[10, 20, 30, 40]` |
| 8 | Deeper left subtree | `[10, 20, 30, 40, None, None, None, 50]` | `[10, 30, 40, 50]` |
| 9 | Perfect tree | `[10, 20, 30, 40, 50, 60, 70]` | `[10, 30, 70]` |
| 10 | Negative IDs | `[10, -20, -30, None, -40]` | `[10, -30, -40]` |

**What each catches**

- **#1/#2** — `None` handling and the one-node case.
- **#3** — baseline level-order behavior.
- **#4** — the right-spine trap; a correct result must include `40` even
  though it is reached by a left branch.
- **#5** — right chain; should be trivial, but checks the order.
- **#6** — right subtree exists at the top but is shallower; the deeper node
  comes from the left subtree.
- **#7** — degenerates to a left-only chain; every level is the left child.
- **#8** — the right side at depth 3 exists only beneath a left node.
- **#9** — a balanced/perfect tree; rightmost is the far-right leaf at each
  level.
- **#10** — negative IDs; no `-1` / 0 sentinels.

### 3.4 Common candidate mistakes

| Mistake | Symptom | How to probe |
|---|---|---|
| Follows only `.right` | Misses rightmost nodes in left subtrees | Test `[10, 20, 30, 40]` |
| BFS but appends every node | Output length = n, not height | Check result length vs. tree height |
| BFS but appends the first node per level | Returns left-side view | Ask them to re-read the sample |
| BFS level size captured after enqueueing children | Mixes levels; wrong boundaries | Trace the first two levels on the sample |
| Recursive DFS with left-first, append-only | Returns leftmost or partial view | Test an unbalanced tree |
| `depth > len(result)` instead of `==` | Skips depths after a gap (possible in DFS with early return) | Test a tree with a missing intermediate level |
| No `None` guard | `AttributeError` on empty input | Pass `None` |
| Returns `TreeNode`s / `Workstation`s | Contract mismatch | Restate `List[int]` |
| Bottom-up order | Reversed result | Compare with sample |
| Uses a stack but pushes right before left | Processes left first; may return wrong nodes | Trace the stack order |

### 3.5 Hint ladder (use sparingly)

Give the next hint only after the candidate is genuinely stuck for ~30
seconds. Each hint reveals progressively more.

1. “What should the output contain for the root level? What about the next
   level?” → one node per depth, top-down.
2. “How would you process the tree one level at a time?” → queue / BFS.
3. “If you use BFS, which node on the current level do you keep?” → the last
   one dequeued.
4. “Could a node in a left subtree ever be the rightmost at its depth?” → yes,
   if the right side is shallower.
5. “Without BFS, could you visit the right side first and track depth?” →
   right-first DFS with `depth == len(result)`.
6. “What if the tree is 100,000 levels deep?” → iterative DFS or BFS instead
   of recursion.

Do not hand over “BFS and take the last node of each level” as the first hint;
the modeling step (rightmost per depth) is the core signal.

### 3.6 What “correct” looks like in one sentence

> Traverse level by level (or right-first with a depth counter) and take
> exactly one node per depth — the rightmost one — in root-to-deepest order.

---

## 4. Follow-ups

Choose one or two based on time and performance. 4.1 is the natural
production-flavored follow-up; 4.2–4.5 extend the same level-order idea.

### 4.1 Deep tree / recursion limit

**Prompt:** “In production the line can be 100,000 stages deep. Does your
solution still work?”

**Expected answer:** BFS and iterative DFS are fine. A recursive DFS raises
`RecursionError` under Python’s ~1,000-frame default. Options:

1. Switch to BFS (§2.1). Best answer if they wrote DFS.
2. Use the iterative right-first DFS (§2.3).
3. `sys.setrecursionlimit(10**6)` — a band-aid; can still crash the C stack
   and is not a robust production answer. Accept but push for 1 or 2.

**Evidence:** the recursive reference raises `RecursionError` on a 5,000-node
right chain under Python 3.13’s default limit; BFS and iterative DFS compute
the correct result (see §9).

### 4.2 Left-side view

**Prompt:** “Now put the camera on the left wall. What changes?”

**Expected insight:** the same level-order traversal, but keep the **first**
node of each level. Alternatively, DFS left-first.

```python
from collections import deque
from typing import List, Optional


class Solution:
    def leftmostStations(self, root: Optional[Workstation]) -> List[int]:
        if root is None:
            return []

        result: List[int] = []
        queue = deque([root])

        while queue:
            level_size = len(queue)
            for i in range(level_size):
                node = queue.popleft()
                if i == 0:
                    result.append(node.station_id)
                if node.left is not None:
                    queue.append(node.left)
                if node.right is not None:
                    queue.append(node.right)

        return result
```

**Complexity:** O(n) time, O(width) space.

### 4.3 N-ary tree generalization

**Prompt:** “What if the line allows up to k downstream workstations instead
of exactly two?”

**Expected insight:** BFS still works; the rightmost node on a level is the
**last** node enqueued from the previous level. The traversal doesn’t care how
many children each node has.

```python
from collections import deque
from typing import List, Optional


class StationNode:
    def __init__(
        self,
        station_id: int,
        children: Optional[List["StationNode"]] = None,
    ):
        self.station_id = station_id
        self.children = children or []


class Solution:
    def rightmostStationsNary(
        self, root: Optional[StationNode]
    ) -> List[int]:
        if root is None:
            return []

        result: List[int] = []
        queue = deque([root])

        while queue:
            level_size = len(queue)
            for i in range(level_size):
                node = queue.popleft()
                if i == level_size - 1:
                    result.append(node.station_id)
                queue.extend(node.children)

        return result
```

**Complexity:** O(n) time, O(width) space.

### 4.4 Rightmost leaf per depth

**Prompt:** “The camera only photographs workstations that are leaves — no
downstream stations. For each depth, return the rightmost leaf, or `None` if
that depth has no leaf.”

```python
from collections import deque
from typing import List, Optional


class Solution:
    def rightmostLeafPerLevel(
        self, root: Optional[Workstation]
    ) -> List[Optional[int]]:
        if root is None:
            return []

        result: List[Optional[int]] = []
        queue = deque([root])

        while queue:
            level_size = len(queue)
            rightmost_leaf: Optional[int] = None
            for _ in range(level_size):
                node = queue.popleft()
                if node.left is None and node.right is None:
                    rightmost_leaf = node.station_id
                if node.left is not None:
                    queue.append(node.left)
                if node.right is not None:
                    queue.append(node.right)
            result.append(rightmost_leaf)

        return result
```

**Example:** `[10, 20, 30, 40]` → depth 0 has no leaf (`None`), depth 1 has
leaf `30`, depth 2 has leaf `40` → `[None, 30, 40]`.

**Complexity:** O(n) time, O(width) space.

### 4.5 k-th station from the right per level

**Prompt:** “Instead of the rightmost, return the k-th from the right at each
level; return `None` for levels narrower than k.”

```python
from collections import deque
from typing import List, Optional


class Solution:
    def kthFromRightPerLevel(
        self,
        root: Optional[Workstation],
        k: int,
    ) -> List[Optional[int]]:
        if root is None or k < 1:
            return []

        result: List[Optional[int]] = []
        queue = deque([root])

        while queue:
            level_size = len(queue)
            level_ids: List[int] = []
            for _ in range(level_size):
                node = queue.popleft()
                level_ids.append(node.station_id)
                if node.left is not None:
                    queue.append(node.left)
                if node.right is not None:
                    queue.append(node.right)

            result.append(level_ids[-k] if k <= len(level_ids) else None)

        return result
```

**Example:** perfect tree `[10, 20, 30, 40, 50, 60, 70]`, `k = 2` →
`[None, 20, 60]`.

**Complexity:** O(n) time, O(width) space.

### 4.6 Other variants you can improvise

- Return `(depth, station_id)` pairs instead of bare IDs.
- Return the view bottom-up instead of top-down.
- Return the rightmost node at every other depth.
- Return the **boundary** of the tree (left edge + leaves + right edge).
- Return the right-side view for each tree in a forest.
- Serialize/deserialize the tree plus the view in one pass.
- Streaming: the tree is revealed level by level, and new workstations can be
  attached — maintain the rightmost per level incrementally.

---

## 5. Scoring rubric

### 5.1 Dimensions

| Dimension | What to look for |
|---|---|
| Clarification | Confirms the node shape, return type, empty behavior, and the per-depth rule before coding. Doesn’t assume “rightmost = right child.” |
| Modeling | Maps “visible from the right” to “last node at each BFS level,” or right-first DFS + depth. |
| Algorithm | Chooses BFS or right-first DFS; explains the invariant and why it’s correct on unbalanced trees. |
| Correctness | Handles empty tree, one-node tree, left-only chains, and rightmost nodes inside left subtrees. |
| Complexity | States O(n) time and O(width) / O(height) space; notices recursion depth risk. |
| Code quality | Clear names, no duplicated traversal, clean level boundaries, type hints. |
| Testing | Walks through the sample arithmetic; tries an unbalanced case unprompted. |
| Communication | Narrates the invariant, responds to hints, can convert BFS ↔ DFS. |

### 5.2 Hire bands

| Band | Looks like |
|---|---|
| **Strong hire** | Asks 3+ meaningful clarifications; identifies per-depth rightmost; BFS or right-first DFS; handles empty and left-only; proactively flags the right-spine trap and recursion depth; clean code; can name the alternative traversal. |
| **Hire** | Understands the per-depth rule; reaches O(n) with minor hints; sample correct; one edge case; acceptable code. |
| **Lean no** | Follows only right children; assumes a complete tree; O(n log n) or repeated traversals; only tests the sample; needs multiple hints. |
| **No hire** | Cannot connect “rightmost per level” to level-order traversal; wrong output on the sample; no `None` handling; cannot explain complexity. |

### 5.3 Strong signals (any of these is a plus)

- Says “last node of each level” before writing code.
- Uses a `level_size` snapshot before iterating the queue.
- Tests `root = None` and a single node without being asked.
- Tests or discusses the right-spine trap (`[10, 20, 30, 40]`).
- Uses right-first DFS with `depth == len(result)`.
- Mentions BFS uses O(width) memory and DFS O(height).
- Volunteers the deep-tree recursion issue.
- Converts the solution to the left-side view immediately.

### 5.4 Red flags

- Writes `while root.right: ...` and stops.
- Assumes the tree is complete/perfect and indexes an array by level.
- Appends every node or the first node of each level.
- Updates `level_size` inside the child loop.
- Pushes children before recording the level boundary.
- Uses `depth >= len(result)` and assumes no gaps.
- Returns nodes or a nested list instead of IDs.
- Has no empty-tree guard.
- Cannot explain why right-first DFS records only one node per depth.

---

## 6. Mock dialogue

### 6.1 Strong candidate

> **Candidate:** Before I write anything — each node is a `Workstation` with an
> integer `station_id` and optional `left` and `right`, correct?
>
> **Interviewer:** Yes.
>
> **C:** And the camera sees the rightmost node at each depth, not just the
> right child chain?
>
> **I:** Correct. Per depth.
>
> **C:** If a level’s only nodes come from a left subtree, the rightmost of
> those is still visible?
>
> **I:** Yes.
>
> **C:** What should I return — IDs or nodes?
>
> **I:** `List[int]` of IDs, top to bottom.
>
> **C:** Empty tree?
>
> **I:** Return `[]`.
>
> **C:** Is the tree guaranteed balanced?
>
> **I:** No.
>
> **C:** Then I’ll do level-order BFS: for each level, process its nodes,
> record the last one, and enqueue children. O(n) time, O(width) space. Or I
> could do a right-first DFS with a depth counter and only record the first
> node seen at each new depth — O(height) space, but recursion depth could be
> an issue on a very deep tree.
>
> **I:** Which do you prefer?
>
> **C:** BFS is the safest for deep trees. I’ll write BFS and mention the DFS
> alternative.

*Calibration: strong-hire opening. They extracted the per-depth rule and the
right-spine trap before typing, and compared the two traversals.*

### 6.2 Weaker candidate (and how to nudge)

> **Candidate:** *(starts typing)* `while root: result.append(root.val);
> root = root.right` …
>
> **Interviewer:** Before you go further — what does “rightmost at each
> depth” mean for this tree? *(draws `[10, 20, 30, 40]`)*
>
> **C:** The rightmost per level… level 2 only has 40, under 20.
>
> **I:** So following `.right` from the root gets you what?
>
> **C:** 10 and 30. I’d miss 40. I need to look at levels, not the right
> spine. Could BFS.
>
> **I:** What would you keep from each level?
>
> **C:** The last node. I’ll track the queue size per level.

*Calibration: the nudge should be a question plus a counterexample, not a
correction. If they recover quickly and explain the fix, this can still land
at hire; if they need to be walked through every assumption, lean no.*

### 6.3 If the candidate asks no questions

Do not let them code for 10 minutes on assumptions. Prompt once, generically:

> “Is there anything about the input or output you want to confirm before you
> commit to an approach?”

If they still don’t ask, proceed; their solution will reveal the assumptions,
and you can test the hidden cases later. The absence of questions is itself
data — note it in the rubric.

---

## 7. Test harness

Everything below is designed to be pasted into a local file after the
candidate’s `Solution` class. All reference versions in this doc were run
against these tests; see §9.

### 7.1 Shared fixture

```python
from typing import List, Optional


class Workstation:
    def __init__(self, station_id: int, left=None, right=None):
        self.station_id = station_id
        self.left = left
        self.right = right


# ---------------------------------------------------------------------------
# Paste the candidate's Solution class here before running.
# ---------------------------------------------------------------------------
```

### 7.2 Deterministic test file

The file is standalone: it runs under pytest, or directly with
`python test_rightmost_stations.py` because the tests are plain asserts. The
`build_tree` helper accepts LeetCode-style level-order lists with `None` for
missing children.

```python
from collections import deque
from typing import List, Optional

# Copy the Workstation class and the candidate's Solution class here.

class Workstation:
    def __init__(self, station_id: int, left=None, right=None):
        self.station_id = station_id
        self.left = left
        self.right = right


def build_tree(values):
    """Build a binary tree from a LeetCode-style level-order list."""
    if not values or values[0] is None:
        return None

    root = Workstation(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()

        if i < len(values) and values[i] is not None:
            node.left = Workstation(values[i])
            queue.append(node.left)
        i += 1

        if i < len(values) and values[i] is not None:
            node.right = Workstation(values[i])
            queue.append(node.right)
        i += 1

    return root


def test_empty():
    assert Solution().rightmostStations(build_tree([])) == []


def test_single_node():
    assert Solution().rightmostStations(build_tree([10])) == [10]


def test_sample():
    root = build_tree([10, 20, 30, None, 40, None, 50])
    assert Solution().rightmostStations(root) == [10, 30, 50]


def test_right_spine_trap():
    root = build_tree([10, 20, 30, 40])
    assert Solution().rightmostStations(root) == [10, 30, 40]


def test_only_right_chain():
    root = build_tree([10, None, 20])
    assert Solution().rightmostStations(root) == [10, 20]


def test_right_subtree_shallower():
    root = build_tree([10, 20, 30, None, 40])
    assert Solution().rightmostStations(root) == [10, 30, 40]


def test_left_only_chain():
    root = build_tree([10, 20, None, 30, None, 40])
    assert Solution().rightmostStations(root) == [10, 20, 30, 40]


def test_deeper_left_subtree():
    root = build_tree([10, 20, 30, 40, None, None, None, 50])
    assert Solution().rightmostStations(root) == [10, 30, 40, 50]


def test_perfect_tree():
    root = build_tree([10, 20, 30, 40, 50, 60, 70])
    assert Solution().rightmostStations(root) == [10, 30, 70]


def test_negative_ids():
    root = build_tree([10, -20, -30, None, -40])
    assert Solution().rightmostStations(root) == [10, -30, -40]


if __name__ == "__main__":
    for _name, _fn in list(globals().items()):
        if _name.startswith("test_") and callable(_fn):
            _fn()
    print("all tests passed")
```

Run with:

```text
python -m pytest test_rightmost_stations.py -q
# or, if pytest isn't installed (the tests are plain asserts):
python test_rightmost_stations.py
```

### 7.3 Randomized brute-force validator

Use this to stress a solution beyond hand-written examples. It generates
random binary trees and compares against a slow but independent
left-to-right-per-level checker built with left-first DFS.

```python
import random
from collections import deque
from typing import Dict, List, Optional, Tuple

# Copy the Workstation class and the candidate's Solution class here.

class Workstation:
    def __init__(self, station_id: int, left=None, right=None):
        self.station_id = station_id
        self.left = left
        self.right = right


def brute_force(root: Optional[Workstation]) -> List[int]:
    """Collect nodes left-to-right at each depth, then take the last one."""
    levels: Dict[int, List[int]] = {}

    def dfs(node: Optional[Workstation], depth: int) -> None:
        if node is None:
            return
        levels.setdefault(depth, []).append(node.station_id)
        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)

    dfs(root, 0)
    return [levels[depth][-1] for depth in sorted(levels)]


def random_tree(n: int) -> Optional[Workstation]:
    if n == 0:
        return None

    root = Workstation(random.randint(-100, 100))
    slots: List[Tuple[Workstation, str]] = [(root, "left"), (root, "right")]

    for _ in range(n - 1):
        index = random.randrange(len(slots))
        parent, side = slots.pop(index)
        node = Workstation(random.randint(-100, 100))
        setattr(parent, side, node)
        slots.append((node, "left"))
        slots.append((node, "right"))

    return root


def main() -> None:
    random.seed(20261020)
    for trial in range(5_000):
        root = random_tree(random.randint(0, 80))
        expected = brute_force(root)
        actual = Solution().rightmostStations(root)
        assert actual == expected, (
            f"trial {trial} failed\n"
            f"expected={expected}\nactual={actual}"
        )
    print("5,000 random trees passed")


if __name__ == "__main__":
    main()
```

This exact checker was used to validate the reference implementations; see
§9.

### 7.4 Deep-chain stress test

Only meaningful if you intend the deep-tree constraint to be enforced. A
recursive DFS solution is expected to fail this; BFS and iterative DFS pass.

```python
from typing import List, Optional

# Copy the Workstation class and the candidate's Solution class here.

class Workstation:
    def __init__(self, station_id: int, left=None, right=None):
        self.station_id = station_id
        self.left = left
        self.right = right


n = 5_000
root = Workstation(0)
current = root
for i in range(1, n):
    current.right = Workstation(i)
    current = current.right

try:
    result = Solution().rightmostStations(root)
    assert result == list(range(n))
    print(f"deep chain n={n}: passed")
except RecursionError:
    print(f"deep chain n={n}: RecursionError (expected for recursive DFS)")
```

Note: Python’s default recursion limit is about 1,000 frames, so a recursive
DFS fails well before 5,000. BFS and the iterative right-first DFS pass at
n = 5,000.

### 7.5 Quick manual check of the sample

If you don’t want to run pytest during the interview, the arithmetic to verify
by hand is in §1.2. The values a correct solution must produce:

```text
depth 0: 10
depth 1: 30
depth 2: 50
=> [10, 30, 50]
```

---

## 8. Problem family and difficulty tuning

### 8.1 Related problems

This kit is a Rivian re-theme of a classic binary-tree question:

| Problem | Relationship |
|---|---|
| LeetCode 199 / NeetCode “Binary Tree Right Side View” | The original: return the rightmost value at each depth |
| LeetCode 102 Binary Tree Level Order Traversal | Same BFS skeleton; collect all nodes per level |
| LeetCode 103 Binary Tree Zigzag Level Order Traversal | BFS with alternating direction |
| LeetCode 513 Find Bottom Left Tree Value | Last level, leftmost node |
| LeetCode 1302 Deepest Leaves Sum | Last level, aggregate values |
| LeetCode 987 Vertical Order Traversal | Column-based ordering instead of level-based |

### 8.2 Why this question works

- The story (“right wall camera”) maps cleanly to “one node per depth.”
- The naive right-spine solution is tempting and demonstrably wrong on a
  small tree, which produces a useful discussion.
- BFS and DFS both work, with a genuine space tradeoff: O(width) vs. O(height).
- Follow-ups (left view, n-ary, leaf-only, k-th) all reuse the same level-order
  skeleton without becoming a different problem.
- No obscure data structures; failures are diagnostic.

### 8.3 Difficulty knobs

| Make it easier | Make it harder |
|---|---|
| Guarantee a complete/perfect tree | Allow arbitrary unbalanced trees |
| Guarantee at least one node | Allow `root = None` |
| Return node values with positive IDs | Include negative IDs / arbitrary values |
| Only the sample | Add left-only chains and deeper left subtrees |
| No follow-ups | Add left view, n-ary, leaf-only, k-th, boundary |
| Small, shallow trees | 10^5 nodes, depth 10^5 (recursion limit) |

### 8.4 Reusing the framing

If you want more problems in the same Rivian style, keep the same three-part
pattern you used for the charging question:

1. A Rivian domain scenario with a concrete object (workstations, vehicles,
   stations, entities).
2. A small formal input with an explicit example and expected return.
3. A Python signature that matches LeetCode conventions (`self`, type hints),
   delivered with an intentionally incomplete spec.

This document covers only this problem. Additional problems can reuse §5’s
rubric dimensions and §7’s harness structure.

---

## 9. Appendix: verification log

**Date:** 2026-10-20
**Environment:** Python 3.13.13
**What was verified:** every algorithm and follow-up implementation in this
document, against deterministic cases and randomized inputs, using the
`Workstation` input shape.

| Check | Result |
|---|---|
| Deterministic cases: empty, single, sample, right-spine trap, only-right chain, right subtree shallower, left-only chain, deeper left subtree, perfect tree, negative IDs | Pass (10 cases) for BFS, recursive DFS, iterative DFS |
| 5,000 random trees (0–80 nodes) vs. brute-force left-first DFS per level | Pass for BFS, recursive DFS, iterative DFS |
| Deep right chain n = 5,000 | Recursive DFS: `RecursionError` (expected). BFS and iterative DFS: correct `[0, 1, ..., 4999]` |
| Interviewer’s accepted LeetCode submission (`TreeNode` / `val`, 1-based depth) | Pass: 10 deterministic cases, 5,000 random trees, 5,000-node chain |
| Left-side-view follow-up | Pass |
| N-ary right-side-view follow-up | Pass |
| Rightmost-leaf-per-depth follow-up | Pass |
| k-th-from-right-per-level follow-up | Pass |
| Level-order `build_tree` helper, including `None` gaps | Pass on all deterministic cases |
| Every Python code block in this document compiles | Pass (15/15 blocks) |

The brute-force checker records nodes per depth in left-to-right order using a
left-first DFS, then takes the last entry; this is an independent formulation
from the BFS solution, so agreement across 5,000 random trees is meaningful.

Verification script outline (not part of the interview):

```python
# BFS, recursive DFS, and iterative DFS were each run against:
#   1. the 10 deterministic cases above;
#   2. brute_force() on 5,000 random trees;
#   3. a 5,000-node right chain (recursion-depth behavior).
# The interviewer's accepted LeetCode submission was also run against the same
# deterministic cases, random trees, and deep chain.
# Follow-ups were checked against hand-computed expectations.
```

### 9.1 Known limitations of this kit

- The statement assumes a valid line layout. If the actual interview expects
  validation of malformed input (loops, shared workstations, non-integer IDs),
  add those requirements explicitly; the reference code does not validate.
- The rightmost-leaf and k-th follow-ups return `None` placeholders for depths
  where no such node exists; that is a policy choice. Adjust the expected
  output if you specify a different contract.
- The n-ary follow-up defines `StationNode` separately because the standard
  stub has two downstream lanes. If you use it, paste that class instead of
  `Workstation`.
- The kit is written for Python 3; the type hints assume `Optional` / `List`
  from `typing`.

---

*End of interviewer kit.*
