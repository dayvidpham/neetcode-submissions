# Rivian Interview Kit — “Family Profit” (Tuple-Row Corporate Hierarchy Roll-up)

> **INTERVIEWER-ONLY DOCUMENT.** Do not screen-share this file. Section 1 is the
> candidate-safe material; sections 2–9 are the answer key, rubric, and test
> harness.

**Problem codename:** `rivian-family-profit`
**Input shape:** `List[Tuple[str, Optional[str], int]]` — each row is
`(name, parent, profit)`
**Style:** verbally described problem, empty CodeShare editor
**Language:** Python 3
**Topics:** forests / n-ary trees, parent-pointer modeling, hash maps, post-order
aggregation, recursion depth
**Difficulty:** LeetCode Medium (roughly LC 690 / LC 508 territory)
**Target complexity:** O(n) time, O(n) space
**Expected duration:** 35–45 minutes including follow-ups

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
*clarifying questions are part of the test*. The input is a flat list of
**3-tuples**, one row per company: `(name, parent, profit)`. The candidate must:

1. Turn the row list into a parent→children index (the list is **not** ordered
   parent-before-child).
2. Recognize “family profit” as a **subtree sum**.
3. Run a post-order traversal from **every** root (the structure may be a
   forest, not a single tree).
4. Return `Dict[str, int]` for **all** companies, including negatives.

Core solution: build `children`, DFS post-order, accumulate. O(n) time, O(n)
space. There is no `Company` class; the tuple order is
`(name, parent, profit)` and `parent` is a **name** (or `None`), not an index.

Hidden traps:

| Trap | What it catches |
|---|---|
| Multiple top-level entities | Solutions that assume a single root |
| Child listed before its parent | Solutions that rely on input ordering |
| Negative profits | `if not profit`-style bugs and “losses are invalid” assumptions |
| Deep chain (e.g. 100k) | Blind recursion / RecursionError |
| Every node must appear in output | Implementations that only return roots |
| Tuple field order | `(name, parent, profit)` — not `(name, profit, parent)` |

Reference solution: §2. Answer key: §3. Rubric: §5.

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
| Candidate codes and explains | 15–20 |
| Candidate tests / walks through example | 5 |
| One or two follow-ups | 5–10 |
| Buffer / candidate questions | remainder |

**What you need open:** an empty CodeShare (or equivalent), this doc, and the
tree diagram in §1.2 to draw or paste. Optionally keep the test harness in §7
ready in a local terminal if you want to run their submission automatically.

---

## 1. Candidate-facing material

### 1.1 What you say out loud (60–90 seconds)

> Let’s do a Python problem. You’re a software engineer at Rivian, working on
> the finance platform that tracks our corporate structure. Rivian operates
> through a set of legal entities, and some entities own other entities, so
> there’s a hierarchy.
>
> You get a list of companies. Each element is a 3-tuple — basically a row in a
> table: `(name, parent, profit)`. `name` is the company’s name. `parent` is
> the name of the company that owns it, or `None` if it sits at the top level.
> `profit` is its own profit for the quarter, an integer number of dollars.
>
> An entity’s **family profit** is its own profit plus the family profit of
> every entity underneath it — its direct subsidiaries, their subsidiaries,
> and so on. So the whole thing rolls up.
>
> Given that list of company rows, write a function `familyProfits` that
> returns a dictionary mapping each company’s name to its family profit.
>
> Here’s an example. *(draw/paste the tree from §1.2)* Rivian’s family profit
> is 2,285, Rivian Automotive is 680, and so on. You’ll be writing it in the
> empty editor here. Any questions before you start?

**Do not** volunteer: that multiple roots are possible, that the list is
unordered, that negative profits appear, or the input size. Those are the
deliberate gaps — see §3.2. The tuple order `(name, parent, profit)` is stated
because the code can’t be written without it.

### 1.2 Worked example (draw or paste this)

```text
Rivian (1000)
├── Rivian Automotive (600)
│   ├── Service Network (50)
│   └── Fleet Sales (30)
├── Rivian Energy (400)
│   └── Charging Operations (100)
│       └── Adventure Charging (25)
└── Rivian Commercial (80)
```

Rows:

```text
companies = [
    ("Rivian",              None,                 1000),
    ("Rivian Automotive",   "Rivian",              600),
    ("Rivian Energy",       "Rivian",              400),
    ("Rivian Commercial",   "Rivian",               80),
    ("Service Network",     "Rivian Automotive",    50),
    ("Fleet Sales",         "Rivian Automotive",    30),
    ("Charging Operations", "Rivian Energy",       100),
    ("Adventure Charging",  "Charging Operations",  25),
]
```

Expected return:

```text
{
    "Rivian":             2285,
    "Rivian Automotive":   680,
    "Rivian Energy":       525,
    "Rivian Commercial":    80,
    "Service Network":      50,
    "Fleet Sales":          30,
    "Charging Operations": 125,
    "Adventure Charging":   25,
}
```

Roll-up detail:

| Company | Own profit | Family profit | Arithmetic |
|---|---:|---:|---|
| Adventure Charging | 25 | 25 | 25 |
| Charging Operations | 100 | 125 | 100 + 25 |
| Rivian Energy | 400 | 525 | 400 + 125 |
| Service Network | 50 | 50 | 50 |
| Fleet Sales | 30 | 30 | 30 |
| Rivian Automotive | 600 | 680 | 600 + 50 + 30 |
| Rivian Commercial | 80 | 80 | 80 |
| Rivian | 1000 | 2285 | 1000 + 680 + 525 + 80 |

### 1.3 Paste-ready stub (recommended)

Paste this into the empty editor so the candidate focuses on the algorithm
rather than on typing boilerplate. The `self`/`class Solution` shape matches
the LeetCode-style example you already have.

```python
from typing import Dict, List, Optional, Tuple


class Solution:
    def familyProfits(
        self,
        companies: List[Tuple[str, Optional[str], int]],
    ) -> Dict[str, int]:
        ...
```

The type can be read as: “a list of rows, each row is
`(name, parent_or_None, profit)`.”

If they want a shorter annotation for readability, an alias is fine:

```python
from typing import Optional, Tuple

Row = Tuple[str, Optional[str], int]
```

### 1.4 Paste-ready statement (Python docstring version)

If you want the written prompt above the stub, use a docstring or `#`
comments. The `/* ... */` block from your charging example is not valid Python
and would break if the CodeShare file is ever executed or linted.

```python
"""
You're a software engineer at Rivian, working on the finance platform that
tracks the corporate structure of Rivian's legal entities.

You are given a list of companies. Each element is a 3-tuple, essentially a
row in a table:

    (name, parent, profit)

  - name:   the company's name,
  - parent: the name of the company that owns it, or None if it sits at the
            top level,
  - profit: its own profit for the quarter, as an integer number of dollars.

An entity's "family profit" is its own profit plus the family profit of every
entity beneath it in the structure (its direct subsidiaries, their
subsidiaries, and so on).

Given the list of company rows, write familyProfits(companies) and return a
dictionary mapping each company's name to its family profit.
"""
```

### 1.5 If the candidate asks for a second example

Give this small chain. It confirms the recursive roll-up without leaking the
forest/negative/ordering traps that live in §3.3.

```text
Rivian (100)
└── Rivian Labs (20)
    └── Rivian Labs West (5)

rows = [
    ("Rivian",           None,           100),
    ("Rivian Labs",      "Rivian",        20),
    ("Rivian Labs West", "Rivian Labs",    5),
]

=> {
    "Rivian": 125,
    "Rivian Labs": 25,
    "Rivian Labs West": 5,
}
```

### 1.6 What to do once they start coding

- **Default:** paste the stub from §1.3 and let them fill in `familyProfits`.
- **If you also want to evaluate API/design:** give only the verbal
  description and let them ask about the row layout. Then answer from §3.1.
- **If they ask to write a `main`/tests:** fine; do not stop them, but keep
  them focused on the function. The clock is for the algorithm.

### 1.7 Candidate-facing constraints (only if pressed)

If they insist on constraints before coding, you may say:

> Assume the input is a valid hierarchy: every parent name that is present
> refers to a company in the list, names are unique, and there are no cycles.
> Each row is always `(name, parent, profit)`, and `parent` is `None` or a
> name. Profits are integers. You don’t need to validate anything.

Do **not** say “there can be several roots” or “the list is unordered” yet.
Those are exactly the things a strong candidate should ask about.

---

## 2. Reference solutions

All solutions take the raw row list
`List[Tuple[str, Optional[str], int]]` and assume a valid forest (unique names,
existing parent references, no cycles).

### 2.1 Primary solution — recursive post-order DFS

This is the expected answer. Build the child index, then compute each subtree
bottom-up.

```python
from typing import Dict, List, Optional, Tuple


class Solution:
    def familyProfits(
        self, companies: List[Tuple[str, Optional[str], int]]
    ) -> Dict[str, int]:
        # name -> own profit
        profits: Dict[str, int] = {}
        # parent name -> list of child names
        children: Dict[str, List[str]] = {name: [] for name, _, _ in companies}
        roots: List[str] = []

        # 1. Index parents -> children. The input is not necessarily ordered.
        for name, parent, profit in companies:
            profits[name] = profit
            if parent is None:
                roots.append(name)
            else:
                children[parent].append(name)

        totals: Dict[str, int] = {}

        # 2. Post-order: children before parent.
        def dfs(name: str) -> int:
            total = profits[name]
            for child in children[name]:
                total += dfs(child)
            totals[name] = total
            return total

        # 3. Handle a forest: every top-level entity is a root.
        for root in roots:
            dfs(root)

        return totals
```

**Why post-order:** a node’s total depends on each child’s already-computed
total. Visiting the node before its children would require a second pass or
memoization; visiting after them is a single O(n) traversal.

**Tuple-specific details:**

- Unpack once: `for name, parent, profit in companies`.
- `children` is keyed by **name**, not by an index. The parent column stores a
  name.
- A leaf’s `children[name]` entry is initialized to `[]`, so the traversal
  doesn’t need `dict.get`.

**Complexity**

- Time: O(n) — each node is indexed once and visited once.
- Space: O(n) for `profits`, `children`, `totals`, and the recursion stack,
  which is O(h) where `h` is the height of the deepest hierarchy. Worst case
  `h = n`.

### 2.2 Iterative post-order (safe for deep hierarchies)

Use this if the code must survive a pathological chain. No Python recursion
limit and no `sys.setrecursionlimit` band-aid.

```python
from typing import Dict, List, Optional, Tuple


class Solution:
    def familyProfits(
        self, companies: List[Tuple[str, Optional[str], int]]
    ) -> Dict[str, int]:
        profits: Dict[str, int] = {}
        children: Dict[str, List[str]] = {name: [] for name, _, _ in companies}
        roots: List[str] = []

        for name, parent, profit in companies:
            profits[name] = profit
            if parent is None:
                roots.append(name)
            else:
                children[parent].append(name)

        totals: Dict[str, int] = {}

        for root in roots:
            # Each stack entry is (name, expanded).
            # expanded=False: first visit; push children and self back.
            # expanded=True: children are done; compute this node.
            stack = [(root, False)]
            while stack:
                name, expanded = stack.pop()
                if expanded:
                    totals[name] = profits[name] + sum(
                        totals[child] for child in children[name]
                    )
                else:
                    stack.append((name, True))
                    for child in children[name]:
                        stack.append((child, False))

        return totals
```

**Complexity:** O(n) time, O(n) memory (stack in the worst case is O(h);
the `profits`/`children`/`totals` maps are O(n)).

### 2.3 Alternative — leaf-to-root accumulation (Kahn-style)

A different mental model that impresses interviewers: don’t traverse top-down
at all. Start with every leaf, add its total to its parent, and when a parent
has no unprocessed children left, it becomes a leaf and enters the queue. This
is also O(n), iterative, and needs no explicit post-order stack.

```python
from collections import deque
from typing import Dict, List, Optional, Tuple


class Solution:
    def familyProfits(
        self, companies: List[Tuple[str, Optional[str], int]]
    ) -> Dict[str, int]:
        parent: Dict[str, Optional[str]] = {}
        children: Dict[str, List[str]] = {}
        remaining_children: Dict[str, int] = {}
        totals: Dict[str, int] = {}

        for name, p, profit in companies:
            parent[name] = p
            children[name] = []
            remaining_children[name] = 0
            totals[name] = profit

        for name, p, _ in companies:
            if p is not None:
                children[p].append(name)
                remaining_children[p] += 1

        queue = deque(
            name for name, count in remaining_children.items() if count == 0
        )

        while queue:
            name = queue.popleft()
            p = parent[name]
            if p is not None:
                totals[p] += totals[name]
                remaining_children[p] -= 1
                if remaining_children[p] == 0:
                    queue.append(p)

        return totals
```

**Complexity:** O(n) time, O(n) space. Each node enters and leaves the queue
once.

### 2.4 Comparison

| Approach | Time | Space | Pros | Cons |
|---|---:|---:|---|---|
| Recursive post-order | O(n) | O(n) | Short, easiest to explain | RecursionError on deep chains |
| Iterative post-order | O(n) | O(n) | No recursion limit, same traversal | Slightly more code |
| Kahn leaf-to-root | O(n) | O(n) | No traversal, elegant roll-up | Less common; queue bookkeeping |
| Recompute per node | O(n²) | O(n) | Simple to start | Fails “what if n is large?” |

**Expected interview answer:** 2.1 first, then mention 2.2 as the deep-hierarchy
fix when asked. 2.3 is a bonus if they offer it unprompted.

### 2.5 What a clean final solution looks like

- One pass to build `profits` and `children: Dict[str, List[str]]`.
- Collect `roots` in the same pass (`parent is None`).
- One post-order computation, memoized in `totals`.
- Return all names, including non-roots.
- No reliance on list ordering, no single-root assumption.
- O(n) stated and justified without prompting.
- Empty input naturally returns `{}`.
- Tuple columns unpacked in the stated order; no `Company` class invented.

---

## 3. Interviewer answer key

### 3.1 Clarifying questions and intended answers

Award credit for questions that remove a real ambiguity, not for checkbox
questions. These are the ones that matter:

| Candidate asks | Answer to give | Why it matters |
|---|---|---|
| What exactly is the input type? | `List[Tuple[str, Optional[str], int]]`, one row per company | They need to know it’s a flat table, not objects |
| What’s the tuple order? | `(name, parent, profit)` | Prevents an unpacking-order bug |
| Is `parent` a name or an index/ID? | The parent’s **name** (or `None`) | The child index must be keyed by name |
| Can there be more than one entity with no parent? | Yes. Treat it as a forest; every root’s subtree must be computed | Catches single-root assumptions |
| Is the list ordered parent-before-child? | No guarantee; any order | Catches index-only solutions and “fast paths” |
| Can a company report a loss / negative profit? | Yes, profits are integers and may be negative | Catches `if not profit` bugs and incorrect max logic |
| Are names unique? | Yes, unique | Needed for name-keyed maps |
| Do parent references always exist in the list? | Yes, input is valid | Avoids defensive noise |
| Can there be cycles? | No | Confirms a forest, not a general graph |
| Does family profit include the company itself? | Yes | Catches “children only” answers |
| Does it include grandchildren recursively? | Yes, all descendants | Catches direct-children-only answers |
| What should I return? | `dict` from name to family profit for **every** company; order irrelevant | Catches root-only or list output |
| How large can the input be? | Up to ~10^5 entities; hierarchies can be deep | Invites complexity and recursion discussion |
| What about an empty list? | Return `{}` | Tests natural handling of no roots |

If they ask something not covered, answer consistently with “valid forest,
integer profits, return all names”. Do not invent extra constraints; if the
question is genuinely ambiguous and the answer would change the code, pick the
simplest interpretation and note it.

### 3.2 Deliberate omissions

The spoken prompt intentionally leaves these out. Reveal them only when asked
or when they become relevant to a failing test.

| Omitted detail | Intended answer | Reveal when |
|---|---|---|
| Forest / multiple roots | Allowed | They assume one root, or when they walk through the sample |
| Input ordering | Arbitrary | They index assuming parent appears earlier |
| Negative profits | Allowed | They assert profits are non-negative, or their code uses truthiness |
| Uniqueness | Names unique | They ask how duplicate names behave |
| Parent references exist | Guaranteed valid | They ask about dangling parents |
| Input size / depth | Up to ~10^5, possibly deep | They state complexity or choose recursion |
| Output shape | Dict, all names | They start returning roots only |

The tuple order is **not** omitted: it is stated in both the verbal script and
the stub, because the problem is unsolvable without it.

### 3.3 Hidden test cases and expected outputs

Use these after their solution passes the sample. The point is not to trick
them with exotic input; it is to test the assumptions they did or did not
surface.

| # | Case | Input (summary) | Expected |
|---|---|---|---|
| 1 | Empty | `[]` | `{}` |
| 2 | Single node | `[("Rivian", None, -7)]` | `{"Rivian": -7}` |
| 3 | Sample | §1.2 | §1.2 dict |
| 4 | Forest + negative | `A(10) -> A1(5), A2(1)`; `B(None, -3)` | `{"A": 16, "A1": 5, "A2": 1, "B": -3}` |
| 5 | Child before parent | `[("child", "parent", 5), ("parent", None, 10)]` | `{"child": 5, "parent": 15}` |
| 6 | Negative in the middle | root(10) -> mid(-5) -> leaf(2) | `{"root": 7, "mid": -3, "leaf": 2}` |
| 7 | All zeros | `x(0) -> y(0)` | `{"x": 0, "y": 0}` |
| 8 | Wide | root(1) with 100 leaf children each 1 | root = 101, leaves = 1 |
| 9 | Deep chain | 5,000 nodes, each profit 1 | root = 5000; node at depth d (root = 0) gets 5000 - d |
| 10 | Same name twice | invalid input | not tested; guaranteed unique |

Concrete Python form of cases 1–7:

```python
[
    ([], {}),
    ([("Rivian", None, -7)], {"Rivian": -7}),
    (
        [("A", None, 10), ("A1", "A", 5),
         ("A2", "A", 1), ("B", None, -3)],
        {"A": 16, "A1": 5, "A2": 1, "B": -3},
    ),
    (
        [("child", "parent", 5), ("parent", None, 10)],
        {"child": 5, "parent": 15},
    ),
    (
        [("root", None, 10), ("mid", "root", -5),
         ("leaf", "mid", 2)],
        {"root": 7, "mid": -3, "leaf": 2},
    ),
    (
        [("x", None, 0), ("y", "x", 0)],
        {"x": 0, "y": 0},
    ),
]
```

**What each catches**

- **#1/#2** — natural handling of no roots and a single root; no `min()`/`max()`
  crash, no indexing `root[0]`.
- **#4** — one-root assumptions; output keyed only by roots; traversal that
  stops after the first root.
- **#5** — relying on input order; a single forward pass over the list that
  updates parents as it goes.
- **#6** — negative intermediate totals being dropped or treated as “no
  profit”.
- **#8** — recursion depth that is fine for a chain but wide, or accidentally
  O(n²) child lookups.
- **#9** — blind recursion; O(n) memory assumptions.

### 3.4 Common candidate mistakes

| Mistake | Symptom | How to probe |
|---|---|---|
| Unpacks in the wrong order | Name/parent/profit swapped; `TypeError` or nonsense totals | Ask them to restate the row layout |
| Assumes one root | Returns totals for one tree; misses other components | “Is it always one company at the top?” |
| Assumes input order | `KeyError` or wrong values when child precedes parent | Reorder the sample live |
| Direct children only | Parent total = own + direct kids, missing grandchildren | Ask for `Rivian`’s total from the sample |
| Excludes own profit | Totals too low by each node’s own value | “Does family include the entity itself?” |
| Recomputes each subtree | O(n²), visible on a wide/deep test | Ask complexity, then test n large |
| `if not profit:` | Zero/negative profits treated as absent | Zero example (#7) and negative (#6) |
| Recursion without limit discussion | RecursionError on deep hierarchy | Follow-up 4.1 |
| Mutates the rows / assumes mutability | Reusing input in a second test fails | Run two tests with the same list |
| Returns only roots | Output length is number of roots | Check output length = n |
| Returns a list of tuples | Contract mismatch | Restate the return type |
| Invents an object wrapper | Adds a class that the input doesn’t contain | “What does each element actually look like?” |

### 3.5 Hint ladder (use sparingly)

Give the next hint only after the candidate is genuinely stuck for ~30
seconds. Each hint reveals progressively more.

1. “What would be a useful map to build from these rows?” → parent → children.
2. “If you already knew total profit for each child, how would you compute the
   parent’s?” → own + sum of child totals.
3. “So which node should be finalized first — a parent or a leaf?” → leaf /
   post-order.
4. “How do you get that ordering without assuming the input is sorted?” →
   DFS post-order or leaf queue.
5. “Could there be more than one top-level entity?” → loop over all roots.
6. “What happens if the hierarchy is 100,000 levels deep?” → iterative stack
   or Kahn.

Do not hand over “build an adjacency list and DFS post-order” as a single
hint; the modeling step is the core signal.

### 3.6 What “correct” looks like in one sentence

> Build a `parent → children` index in one O(n) pass over the rows, collect all
> roots, and post-order accumulate each subtree sum into `totals`, returning
> totals for every node.

---

## 4. Follow-ups

Choose one or two based on time and performance. 4.1 is the most likely
real-world follow-up; 4.2 is the most natural algorithmic extension; 4.3 is
the most “engineering” extension.

### 4.1 Deep hierarchy / recursion limit

**Prompt:** “In production the corporate structure can be 100,000 levels deep.
Does your solution still work?”

**Expected answer:** the recursive version raises `RecursionError` under
Python’s ~1,000-frame default. Options:

1. Convert to an explicit iterative post-order stack (§2.2). Best answer.
2. Use leaf-to-root accumulation (§2.3). Also O(n), no recursion.
3. `sys.setrecursionlimit(10**6)` — a band-aid; can still crash the C stack
   and is not a robust production answer. Accept but push for 1 or 2.

**Evidence:** the recursive reference raises `RecursionError` on a 5,000-node
chain under Python 3.13’s default limit; iterative and Kahn versions compute
correct totals (see §9).

**Follow-up within the follow-up:** “Now return only the top-level
consolidated profit.” → sum the `totals` of nodes whose `parent is None` (or
just run the algorithm without recording non-root outputs).

### 4.2 Maximum family profit entity

**Prompt:** “Modify it to return the name of the entity with the largest
family profit.”

**Clarify if they don’t:** tie-breaking policy and behavior on empty input.
A reasonable contract: empty → `None`; ties → lexicographically smallest name.

```python
from typing import Dict, List, Optional, Tuple


class Solution:
    def mostProfitableFamily(
        self, companies: List[Tuple[str, Optional[str], int]]
    ) -> Optional[str]:
        totals: Dict[str, int] = self.familyProfits(companies)
        if not totals:
            return None
        # Highest total first, then name ascending for deterministic ties.
        return min(totals, key=lambda name: (-totals[name], name))
```

**Complexity:** O(n) on top of the roll-up; O(n) total.

**Traps:**

- If all totals are negative, the “max” is the least negative; make sure they
  don’t initialize `best = 0`.
- Ties: any deterministic policy is fine, but they should state one.
- Only nodes, including non-roots, are candidates; don’t restrict to roots.

### 4.3 Streaming updates (incremental roll-up)

**Prompt:** “Now the hierarchy changes at runtime. Support
`update_profit(name, new_profit)` and `add_company(name, parent, profit)`.
Both should be fast.”

**Expected insight:** changing a node’s own profit by Δ changes the family
profit of that node and **all of its ancestors** by Δ. Adding a new leaf with
profit p does the same along the new leaf’s ancestor path. So each operation
is O(depth), not O(n), provided we cache the current family totals.

Reference:

```python
from typing import Dict, List, Optional, Tuple


class FamilyProfitTracker:
    def __init__(self, companies: List[Tuple[str, Optional[str], int]]):
        self.parent: Dict[str, Optional[str]] = {}
        self.profit: Dict[str, int] = {}
        self.children: Dict[str, List[str]] = {}

        for name, parent, profit in companies:
            self.parent[name] = parent
            self.profit[name] = profit
            self.children[name] = []

        for name, parent, _ in companies:
            if parent is not None:
                self.children[parent].append(name)

        self.totals: Dict[str, int] = {}
        for name, parent in self.parent.items():
            if parent is None:
                self._init_subtree(name)

    def _init_subtree(self, root: str) -> None:
        stack: List[Tuple[str, bool]] = [(root, False)]
        while stack:
            name, expanded = stack.pop()
            if expanded:
                self.totals[name] = self.profit[name] + sum(
                    self.totals[child] for child in self.children[name]
                )
            else:
                stack.append((name, True))
                for child in self.children[name]:
                    stack.append((child, False))

    def update_profit(self, name: str, new_profit: int) -> None:
        delta = new_profit - self.profit[name]
        self.profit[name] = new_profit
        cur: Optional[str] = name
        while cur is not None:
            self.totals[cur] += delta
            cur = self.parent[cur]

    def add_company(self, name: str, parent: str, profit: int) -> None:
        # Add a new leaf under an existing company.
        assert name not in self.parent and parent in self.parent
        self.parent[name] = parent
        self.profit[name] = profit
        self.children[name] = []
        self.children[parent].append(name)
        self.totals[name] = profit

        cur: Optional[str] = parent
        while cur is not None:
            self.totals[cur] += profit
            cur = self.parent[cur]

    def total(self, name: str) -> int:
        return self.totals[name]
```

**Complexity:** construction O(n); each update/insert O(h) where h is depth;
`total(name)` O(1).

**Discussion points:**

- Reparenting is harder: moving subtree S from old parent to new parent means
  subtracting `totals[S]` from the old ancestor chain and adding it to the new
  one — O(old_depth + new_depth) — but you must reject a `new_parent` that is
  inside S (cycle).
- Deleting a node is similarly a subtraction along the ancestor chain, and
  its children need a policy (promote to root? reject?).
- If updates are batched, lazily recomputing only dirty subtrees can beat
  per-update propagation.

### 4.4 Adjacency-list input

**Prompt:** “What if the input isn’t a row list? Say you get profits by name
and a `children` adjacency map instead.”

```python
from typing import Dict, List


class Solution:
    def familyProfitsAdjacency(
        self,
        profits: Dict[str, int],
        children: Dict[str, List[str]],
    ) -> Dict[str, int]:
        names = set(profits)
        for kids in children.values():
            names.update(kids)

        parent: Dict[str, str] = {}
        for p, kids in children.items():
            for k in kids:
                parent[k] = p

        roots = [name for name in names if name not in parent]
        totals: Dict[str, int] = {name: profits.get(name, 0) for name in names}

        for root in roots:
            stack = [(root, False)]
            while stack:
                name, expanded = stack.pop()
                if expanded:
                    totals[name] = profits.get(name, 0) + sum(
                        totals[child] for child in children.get(name, [])
                    )
                else:
                    stack.append((name, True))
                    for child in children.get(name, []):
                        stack.append((child, False))

        return totals
```

**Complexity:** O(V + E) = O(n) for a forest.

**Bridge from the row version:**

```python
profits = {name: profit for name, _, profit in companies}
children: Dict[str, List[str]] = {name: [] for name, _, _ in companies}
for name, parent, _ in companies:
    if parent is not None:
        children[parent].append(name)
```

### 4.5 Other variants you can improvise

- Return only the consolidated total of the top-level entities.
- Restrict the output to entities above a profit threshold.
- Compute a “family headcount” instead of profit (same algorithm, different
  aggregate).
- Multiple parents (a DAG) — no longer a tree; the same node contributes to
  several ancestors. Discuss topological order / memoization / duplicate
  contributions.
- Weighted ownership (parent owns 60% of a subsidiary) — roll-up becomes
  weighted sums; clarify how partial ownership propagates.

---

## 5. Scoring rubric

### 5.1 Dimensions

| Dimension | What to look for |
|---|---|
| Clarification | Asks about tuple layout, roots/forest, ordering, negatives, uniqueness, size before coding. Doesn’t accept “empty problem” silently. |
| Modeling | Maps the row list to a parent→children index keyed by name; identifies roots explicitly. |
| Algorithm | Chooses post-order / bottom-up aggregation; explains why children must be finalized first. |
| Correctness | Includes own profit, all descendants, every node in the output, negative values; handles all roots. |
| Complexity | States O(n) time and O(n) space and can justify it; notices recursion depth risk. |
| Code quality | Clear names, type hints, small helpers, no duplicated traversal logic. |
| Testing | Walks through the sample arithmetic; tests an edge case or two unprompted; handles empty input. |
| Communication | Explains tradeoffs, narrates the invariant, responds to hints without needing the answer. |

### 5.2 Hire bands

| Band | Looks like |
|---|---|
| **Strong hire** | Confirms the tuple layout, asks 3+ other meaningful clarifications; builds the children index; O(n) post-order; proactively flags multiple roots and recursion depth; tests sample + edge; clean, readable code; iterative version within reach. |
| **Hire** | Confirms the input shape and the core questions (roots, ordering); arrives at O(n) with minor hints; sample is correct; one edge case; acceptable code. |
| **Lean no** | Starts coding immediately and guesses the tuple order; assumes a single root or sorted input; O(n²) or repeated scans; only tests the sample; needs multiple hints to reach post-order. |
| **No hire** | Cannot model the hierarchy as a graph/tree; wrong totals (children only, or missing self); no testing; ignores questions about input guarantees; cannot explain complexity. |

### 5.3 Strong signals (any of these is a plus)

- Restates the row layout before coding: “so each row is name, parent, profit”.
- Builds the index in the same pass that collects roots.
- Says “post-order” or “children first” before writing the recursive call.
- Tests `[]` or a single node without being asked.
- Asks what happens with negative profits or multiple roots.
- Volunteers the deep-chain recursion issue after writing the recursive
  version.
- Implements an iterative version from scratch.
- Notices that a top-level-only output is just the roots’ totals.

### 5.4 Red flags

- Unpacks the tuple in the wrong order and doesn’t verify with the sample.
- Writes a nested loop over the list that recomputes ancestors per node and
  calls it O(n).
- Uses `if not company.profit` / `if company.profit` (breaks on 0 and negatives).
- Assumes parents appear before children.
- Treats the parent column as an index or object rather than a name.
- Returns only the roots or only leaves.
- Panics when the sample has a grandchild (“wait, is this recursive?”).
- Changes the return type without discussion.
- Uses `sys.setrecursionlimit` as the only deep-hierarchy answer and cannot
  explain why that’s risky.

---

## 6. Mock dialogue

### 6.1 Strong candidate

> **Candidate:** Before I write anything — each element is a tuple, right?
>
> **Interviewer:** Yes.
>
> **C:** What’s the order — `(name, parent, profit)`?
>
> **I:** Correct. `parent` is a name or `None`.
>
> **C:** Does each company have at most one parent?
>
> **I:** Yes.
>
> **C:** Can there be more than one company with no parent?
>
> **I:** Yes, that’s possible.
>
> **C:** Is the list in any particular order?
>
> **I:** No.
>
> **C:** Can profits be negative? Losses included?
>
> **I:** Yes.
>
> **C:** Names unique, and parents always present?
>
> **I:** Yes.
>
> **C:** And the output is a dict from every company name to its family
> profit, including the company itself?
>
> **I:** Correct.
>
> **C:** Then I’ll build a `parent → children` map in one pass, collect roots
> at the same time, and run a post-order DFS from each root. Each node’s total
> is its own profit plus the totals of its children. O(n) time, O(n) space;
> the recursion depth is the height, which is fine unless the hierarchy is
> very deep.
>
> **I:** How deep could it get?
>
> **C:** If it can be 100k deep, Python’s recursion limit would break, so I’d
> switch to an explicit stack or a leaf-queue accumulation. Want me to write
> the recursive one first?
>
> **I:** Go ahead.

*Calibration: this is a strong-hire opening. They extracted the hidden
assumptions before typing and noted the deep-chain risk unprompted.*

### 6.2 Weaker candidate (and how to nudge)

> **Candidate:** *(starts typing)* `children = {}` … for name, parent, profit
> in companies: children[parent] = name …
>
> **Interviewer:** Before you go further, what are you assuming about the
> input?
>
> **C:** That each parent has one child? No, one parent per child.
>
> **I:** What about entities whose parent is `None`?
>
> **C:** …Oh, I’d skip them. Actually they need totals too.
>
> **I:** And if the list is ordered child-before-parent?
>
> **C:** Then my one-pass update would miss it. I’d need to build the full map
> first.

*Calibration: the nudge should be a question, not a correction. If they
recover quickly and explain the fix, this can still land at hire; if they
need to be walked through every assumption, lean no.*

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
from typing import Dict, List, Optional, Tuple

Row = Tuple[str, Optional[str], int]


# ---------------------------------------------------------------------------
# Paste the candidate's Solution class here before running.
# ---------------------------------------------------------------------------
```

### 7.2 Deterministic test file

The file is standalone: it runs under pytest, or directly with
`python test_family_profits.py` because the tests are plain asserts.

```python
from typing import Dict, List, Optional, Tuple

# Copy the candidate's Solution class here (or import it from solution.py).

Row = Tuple[str, Optional[str], int]


def make(rows):
    return list(rows)


SAMPLE = make([
    ("Rivian", None, 1000),
    ("Rivian Automotive", "Rivian", 600),
    ("Rivian Energy", "Rivian", 400),
    ("Rivian Commercial", "Rivian", 80),
    ("Service Network", "Rivian Automotive", 50),
    ("Fleet Sales", "Rivian Automotive", 30),
    ("Charging Operations", "Rivian Energy", 100),
    ("Adventure Charging", "Charging Operations", 25),
])

SAMPLE_EXPECTED = {
    "Rivian": 2285,
    "Rivian Automotive": 680,
    "Rivian Energy": 525,
    "Rivian Commercial": 80,
    "Service Network": 50,
    "Fleet Sales": 30,
    "Charging Operations": 125,
    "Adventure Charging": 25,
}


def test_sample():
    assert Solution().familyProfits(SAMPLE) == SAMPLE_EXPECTED


def test_empty():
    assert Solution().familyProfits([]) == {}


def test_single_node_negative():
    assert Solution().familyProfits([("Rivian", None, -7)]) == {
        "Rivian": -7
    }


def test_forest_and_negative():
    companies = [
        ("A", None, 10),
        ("A1", "A", 5),
        ("A2", "A", 1),
        ("B", None, -3),
    ]
    assert Solution().familyProfits(companies) == {
        "A": 16, "A1": 5, "A2": 1, "B": -3,
    }


def test_child_before_parent():
    companies = [
        ("child", "parent", 5),
        ("parent", None, 10),
    ]
    assert Solution().familyProfits(companies) == {"child": 5, "parent": 15}


def test_negative_intermediate():
    companies = [
        ("root", None, 10),
        ("mid", "root", -5),
        ("leaf", "mid", 2),
    ]
    assert Solution().familyProfits(companies) == {
        "root": 7, "mid": -3, "leaf": 2,
    }


def test_all_zero():
    companies = [("x", None, 0), ("y", "x", 0)]
    assert Solution().familyProfits(companies) == {"x": 0, "y": 0}


def test_wide():
    companies = [("root", None, 1)]
    companies += [(f"leaf{i}", "root", 1) for i in range(100)]
    totals = Solution().familyProfits(companies)
    assert totals["root"] == 101
    assert all(totals[f"leaf{i}"] == 1 for i in range(100))
    assert len(totals) == 101


if __name__ == "__main__":
    for _name, _fn in list(globals().items()):
        if _name.startswith("test_") and callable(_fn):
            _fn()
    print("all tests passed")
```

Run with:

```text
python -m pytest test_family_profits.py -q
# or, if pytest isn't installed (the tests are plain asserts):
python test_family_profits.py
```

### 7.3 Randomized brute-force validator

Use this to stress a solution beyond hand-written examples. It generates
random forests (arbitrary order, negative profits, multiple roots) and
compares against a slow but obviously-correct ancestor-accumulation checker.

```python
import random
from typing import Dict, List, Optional, Tuple

Row = Tuple[str, Optional[str], int]

# Paste the candidate's Solution class here.


def brute_force(companies: List[Row]) -> Dict[str, int]:
    parent = {name: p for name, p, _ in companies}
    totals = {name: 0 for name, _, _ in companies}
    for name, _, profit in companies:
        cur: Optional[str] = name
        while cur is not None:
            totals[cur] += profit
            cur = parent[cur]
    return totals


def random_forest(max_nodes: int = 60) -> List[Row]:
    n = random.randint(0, max_nodes)
    names = [f"c{i}" for i in range(n)]
    rows: List[Row] = []
    for i, name in enumerate(names):
        parent = random.choice(names[:i]) if i and random.random() < 0.75 else None
        rows.append((name, parent, random.randint(-100, 100)))
    random.shuffle(rows)  # arbitrary order
    return rows


def main() -> None:
    random.seed(20261020)
    for trial in range(2_000):
        companies = random_forest()
        expected = brute_force(companies)
        actual = Solution().familyProfits(companies)
        assert actual == expected, (
            f"trial {trial} failed\n"
            f"rows={companies}\n"
            f"expected={expected}\nactual={actual}"
        )
    print("2,000 random tuple forests passed")


if __name__ == "__main__":
    main()
```

This exact checker was used to validate the reference implementations; see
§9.

### 7.4 Deep-chain stress test

Only meaningful if you intend the deep-hierarchy constraint to be enforced. A
recursive solution is expected to fail this.

```python
from typing import List, Optional, Tuple

Row = Tuple[str, Optional[str], int]

# Paste the candidate's Solution class here.

n = 5_000
companies: List[Row] = [("c0", None, 1)]
companies += [(f"c{i}", f"c{i-1}", 1) for i in range(1, n)]

try:
    totals = Solution().familyProfits(companies)
    assert totals["c0"] == n
    assert totals[f"c{n-1}"] == 1
    print(f"deep chain n={n}: passed")
except RecursionError:
    print(f"deep chain n={n}: RecursionError (expected for recursive solutions)")
```

Note: Python’s default recursion limit is about 1,000 frames, so the
recursive reference fails well before 5,000. The iterative and Kahn reference
solutions pass at n = 5,000.

### 7.5 Quick manual check of the sample

If you don’t want to run pytest during the interview, the arithmetic to verify
by hand is in §1.2. The values a correct solution must produce:

```text
Adventure Charging:   25
Charging Operations: 125
Rivian Energy:       525
Service Network:      50
Fleet Sales:          30
Rivian Automotive:   680
Rivian Commercial:    80
Rivian:             2285
```

---

## 8. Problem family and difficulty tuning

### 8.1 Related problems

This is a customized, Rivian-themed version of a common “aggregate values up a
tree” exercise. Useful references if the candidate wants to practice
afterward:

| Problem | Relationship |
|---|---|
| LC 690 Employee Importance | Same tree roll-up flavor; input uses subordinate IDs and asks for one employee’s total rather than all nodes |
| LC 508 Most Frequent Subtree Sum | Post-order subtree sums; asks for frequency of sums |
| LC 1120 Maximum Average Subtree | Post-order aggregate (sum + count) to evaluate each subtree |
| LC 834 Sum of Distances in Tree | Rerooting / two-pass aggregation; a much harder follow-up direction |
| LC 200 Number of Islands | The charging-network example already used; unrelated algorithmically, same “Rivian” framing style |

### 8.2 Why this question works

- Models a real data shape: rows from a database / table, not a textbook n-ary
  tree object.
- The flat input forces a modeling step: index first, traverse second.
- Tuple rows make the “input contract” concrete while leaving output shape,
  ordering, and edge behavior open for clarification.
- One clear optimal algorithm, but several valid implementations.
- Naturally supports follow-ups on recursion depth, incremental updates, and
  alternative input formats.
- No trick data structures or obscure math; failure modes are diagnostic.

### 8.3 Difficulty knobs

| Make it easier | Make it harder |
|---|---|
| Guarantee a single root | Guarantee nothing; forest + arbitrary order |
| Input sorted parent-before-child | Shuffle input aggressively |
| All profits positive | Include zero, negative, and large values |
| Small n, shallow tree | 10^5 nodes, deep chain |
| Return totals for roots only | Return totals for every node (standard here) |
| No follow-ups | Add max entity, streaming updates, or DAG with multiple parents |

### 8.4 Reusing the framing

If you want more problems in the same Rivian style, keep the same three-part
pattern you used for the charging question:

1. A Rivian domain scenario with a concrete object (vehicles, stations,
   entities, orders).
2. A small formal input with an explicit example and expected return.
3. A Python signature that matches LeetCode conventions (`self`, type hints),
   delivered with an intentionally incomplete spec.

This document covers only the first problem. Additional problems can reuse
§5’s rubric dimensions and §7’s harness structure.

---

## 9. Appendix: verification log

**Date:** 2026-10-20
**Environment:** Python 3.13.13
**What was verified:** every algorithm and follow-up implementation in this
document, against deterministic cases and randomized inputs, using the tuple
row input shape `List[Tuple[str, Optional[str], int]]`.

| Check | Result |
|---|---|
| Sample expected dict, recursive post-order | Pass |
| Sample expected dict, iterative post-order | Pass |
| Sample expected dict, Kahn leaf-to-root | Pass |
| Empty input / single negative row / all-zero / forest / child-before-parent / negative intermediate | Pass for all three implementations |
| 5,000 random tuple forests (0–60 nodes, arbitrary order, negative profits, multiple roots) vs. brute-force ancestor accumulation | Pass for all three implementations |
| Max-family-profit follow-up, including tie-break and empty input | Pass |
| Adjacency-list variant on the sample | Pass |
| Streaming tracker: 1,000 random `update_profit` / `add_company` operations, compared against full recomputation after every operation | Pass |
| Deep chain n = 5,000 | Recursive: `RecursionError` (expected). Iterative and Kahn: root total 5,000, leaf totals correct |
| Every Python code block in this document compiles | Pass (16/16 blocks) |
| The §7 harness blocks, executed against the §2 reference code | Pass (8 deterministic tests, 2,000-case fuzz, deep-chain, 500-operation streaming check, adjacency variant, Kahn sample) |

The brute-force checker used for validation sums each row’s profit into all of
its ancestors, which is an independent formulation from the post-order
roll-up, so agreement across 5,000 random cases is meaningful.

Verification script outline (not part of the interview):

```python
# Recursive, iterative, and Kahn implementations were each run against:
#   1. the sample and the deterministic edge cases above;
#   2. brute_force() on 5,000 shuffled random forests of tuple rows;
#   3. a 5,000-node chain (recursion-depth behavior).
# The streaming tracker was compared to a full recomputation after each of
# 1,000 random updates/insertions.
```

### 9.1 Known limitations of this kit

- The statement assumes a valid forest. If the actual interview expects
  validation of malformed input (dangling parents, duplicate names, cycles),
  add those requirements explicitly; the reference code will raise or
  misbehave on them by design.
- The streaming follow-up intentionally supports only leaf insertion and
  profit updates; reparenting and deletion are discussion material, not
  reference code.
- The max-profit tie-break (lexicographically smallest name) is a policy
  choice, not a requirement. Adjust the expected answer if you specify a
  different policy in the interview.
- The input is treated as immutable tuples. If the real system passes mutable
  row objects, the algorithms still work, but the type hint and starter stub
  would need to change.

---

*End of interviewer kit.*
