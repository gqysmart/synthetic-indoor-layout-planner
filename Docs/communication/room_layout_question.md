# Question: Room Layout Optimization — CSP → Multi-Agent → Performance Measure

I transform continuous layout geometry into a pixel-based constraint space using EDT and morphological operators. This allows the furniture layout problem to be treated as a discrete CSP / multi-agent optimization, rather than a continuous nonlinear optimization.

## Stage 1: Strong CSP (Hard Constraints)

**Discretization:**  
The continuous room shape is mapped to a pixel grid with a chosen resolution. Furniture actions are discrete translations and rotations.

**Hard constraints:**

1. **Boundary containment**  
   Furniture footprints must lie entirely within the room boundary.

2. **Non-overlap + clearance**  
   After applying clearance inflation, inflated footprints must not overlap.

3. **Accessibility (0.6 m minimum corridor width)**  
   From the door to each furniture item, there must be a 0.6 m–wide free-space path to at least one reachable face/point of the furniture.

**Current algorithm:**

- **Constraints (1) + (2)**  
  ```
  OverlapCost(L) = boundary_violation_area + inflated_overlap_area
  ```
  Use heuristic CSP / hill climbing with discrete moves (translate/rotate) to reduce `OverlapCost` to 0.

- **Constraint (3)**  
  Treat furniture as obstacles on the grid.  
  Use BFS / flood-fill + morphological dilation or EDT to check whether a 0.6 m–wide path exists from the door to each furniture item.

**Current pain points:**

1. Random initial layouts can reach legality, but the resulting designs lack diversity and aesthetic quality.  
2. After eliminating overlaps, there is no mechanism that motivates furniture to continue moving to satisfy accessibility.  
3. Once all hard constraints are satisfied, the system stops, often producing clustered or wall-hugging layouts.

---

## Stage 2: Multi-Agent Optimization for Better Layouts

Goal: treat each furniture item as an “agent” that collectively optimizes global layout quality.

**Human intuition:**  
Beds/desks/sofas are often pushed near walls, so naive agents will collapse to this trivial “everything sticks to the wall” pattern unless avoided.

**Open questions:**

1. How can “maximize usable free space” be converted into meaningful agent actions and reward signals?  
2. How can we avoid collapse into a single dominant strategy (e.g., always placing everything against a wall)?

---

## Stage 3: Performance Measure (PM) Definition

If **any** hard constraint is violated:

```
PM(L) = -∞   (or a large negative penalty)
```

Otherwise:

### Scoring Components

- `S_area(L)` — free-space saturation  
- `S_wall(L)` — penalty for excessive wall hugging  
- `S_interior(L)` — reward for meaningful interior occupation  
- `S_disp(L)` — dispersion / anti-clustering  
- `S_func(L)` — functional comfort zones  
- `S_corr(L)` — corridor quality (optional)  
- `S_align(L)` — alignment / symmetry

### Total Utility

```
PM(L) =
    w1*S_area +
    w2*S_wall +
    w3*S_interior +
    w4*S_disp +
    w5*S_func +
    w6*S_corr +
    w7*S_align
```

### Initial weight suggestion

```
w1 = 1.0
w2 = 0.6
w3 = 0.6
w4 = 0.3
w5 = 0.5
w6 = 0.2
w7 = 0.1
```

---

## Remaining Open Directions

- Lack of background in *multi-agent systems*, *global optimization*, and *search strategies*.  
- Unclear whether the problem is best treated as:  
  - a **pure CSP feasibility** problem,  
  - a **search/optimization** problem, or  
  - a **planning-based** problem with step-by-step reasoning.

