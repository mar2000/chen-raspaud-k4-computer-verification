# Computer verification for the Chen--Raspaud conjecture, case k = 4

This repository contains the **public reproducibility code** accompanying the manuscript

> Maria Nazarczuk, *Towards the Chen--Raspaud conjecture for k=4*.

The mathematical proof is computer-assisted only in a finite collection of local checks in the Kneser graph `K(9,4)`.  The repository contains two exact, stand-alone C++ verifiers and an independent Python implementation used as a cross-check.

## What is certified

### `cpp/verify_revised_reductions.cpp`

Exact exhaustive verifier for the rooted star-replacement reductions used in the proof.  It checks the finite families of local types that remain after the elementary counting bounds.  In particular, among positive-excess degree-3 types the only non-reducible type is `(3,3,4)`, while all relevant positive-excess types of degrees 4 and 5 are eliminated; the remaining higher-degree cases are handled by the counting argument in the paper.

Expected final line:

```text
ALL EXACT C++ STAR CHECKS PASSED
```

### `cpp/verify_334_support.cpp`

Independent exact verifier for the exceptional type `(3,3,4)`.  It directly enumerates colors of `K(9,4)` at the two ends of the relevant 4-thread and verifies the finite compatibility statement used by the charging argument.

Expected final line:

```text
ALL EXACT C++ 334 SUPPORT CHECKS PASSED
```

### `scripts/verify_revised_reductions.py`

Independent Python cross-check based on the finite-state implementation in `src/k9_4/`.  This script is **not needed as the sole certificate**: the two C++ programs above are the exact stand-alone verifiers used for the crucial finite checks.

Expected final line:

```text
ALL REVISED REDUCTION CHECKS PASSED
```

## Requirements

- A C++20 compiler (tested with `g++`).
- Python 3.10+.
- Python dependencies from `requirements.txt` for the cross-check and tests.

For a clean Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Reproduce all checks

```bash
./run_all_checks.sh
```

The script compiles both exact C++ verifiers, runs them, executes the Python cross-check, and then runs the unit tests.

## Repository layout

```text
cpp/        exact stand-alone C++ verifiers
scripts/    independent Python cross-check
src/k9_4/   finite-state implementation for K(9,4)
tests/      unit tests
artifacts/  reference terminal outputs from the verified release
```

## Scope and chronology

The code in this public package is the cleaned reproducibility subset of a larger exploratory project ended in April 2026.  Historical exploratory scripts are intentionally omitted here because they are not required to verify the statements used in the final proof.

The proof was developed independently.  The manuscript itself records the chronology and distinguishes the proof from later work that appeared while the manuscript was being completed.
