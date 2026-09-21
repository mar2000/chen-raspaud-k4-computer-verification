#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

mkdir -p build

echo "[1/4] Exact C++ verifier: rooted star replacement"
g++ -std=c++20 -O2 cpp/verify_revised_reductions.cpp -o build/verify_star
./build/verify_star

echo "[2/4] Exact C++ verifier: support for type (3,3,4)"
g++ -std=c++20 -O2 cpp/verify_334_support.cpp -o build/verify_334
./build/verify_334

echo "[3/4] Independent Python cross-check"
PYTHONPATH=src python3 scripts/verify_revised_reductions.py

echo "[4/4] Unit tests"
PYTHONPATH=src python3 -m pytest -q tests

echo "ALL PUBLIC REPOSITORY CHECKS PASSED"
