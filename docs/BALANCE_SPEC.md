# Vantage XP Tower Defense — Balance Specification

This file resolves the experience-progression invariants referenced by `PROJECT_PLAN.md`.

## Finite enemy XP budget
Each enemy owns exactly one authored `xpBudget`. Damage, control, finishing weight, Beacon support attribution, and late-build catch-up all draw from that same budget. `xpPaid` can never exceed `xpBudget`; regeneration, shield regeneration, split children, and repeated status applications cannot create additional XP.

## Damage contribution
Effective damage unlocks `xpBudget × effectiveDamage / (initialHP + initialShield)`. Overkill is excluded because effective damage is capped by remaining HP/shield. A lethal contribution receives a 1.05 weighting before the enemy-budget cap; this is a small finishing weight, not bonus XP outside the budget.

## Useful-control contribution
A tower applying slow or hard control can claim a bounded portion of the same enemy budget. Each tower is capped to 6% of one enemy's budget from control. Each application requests `xpBudget × min(2.5%, slowAmount × effectiveDuration × coefficient)`, with coefficient 0.022 for ordinary slow and 0.035 for hard control after diminishing returns/boss resistance. Reapplications remain subject to the per-tower cap and remaining enemy budget.

## Beacon support attribution
Beacon support redistributes part of a supported tower's already-unlocked contribution; it does not create XP. The combined support share is capped at 16%, overlapping Beacons use diminishing weights, max-level Beacons do not siphon XP, max-level attackers do not power-level Beacons, and Beacons do not recursively buff/support other Beacons.

## Late-build catch-up
Catch-up is per tower and only applies to a tower placed after wave 0 when it begins below the expected level floor. The expected floors are intentionally conservative so level 15 remains rare:

- waves 1–4: L1
- waves 5–8: L2
- waves 9–12: L3
- waves 13–16: L4
- waves 17–20: L5
- waves 21–24: L6
- waves 25–27: L7
- waves 28–29: L8
- waves 30–31: L9

At construction the target XP is frozen to the threshold of that wave's expected floor. While the tower is below that target and no more than five waves have elapsed since construction, its own damage/control contribution weight is multiplied by `1 + min(0.40, 0.40 × remainingGap / targetXP)`. Because the weighted contribution is still capped by the enemy's remaining `xpBudget`, catch-up redistributes a finite budget rather than minting XP. Catch-up expires immediately at the target or after five waves.

## Determinism
All formulas above use simulation state only. No wall-clock time, rendering frame rate, or game-speed setting may affect XP allocation or tower combat results.
