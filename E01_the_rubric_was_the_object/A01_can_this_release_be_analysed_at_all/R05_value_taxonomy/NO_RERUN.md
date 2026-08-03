Threshold-sweep cells (`a05_t*.json`) predate later edits to `run.py` and are **not** re-run.

They are the same category the queue freezes as "r25 metric cells": a sweep produces one file per
setting, and refreshing them all means re-running the sweep, which the freeze forbids. The
default-setting result carries the round's live conclusion; the swept cells are historical
artifacts of a frozen line.

**What this means for a reader:** a cell's numbers are correct for the setting and code that
produced them. They should not be read as this round's current conclusion, and the sweep as a
whole is frozen (see FROZEN.md).
