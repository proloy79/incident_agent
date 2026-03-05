#!/bin/bash

mkdir -p src/ agenticai scripts configs data/raw data/processed data/cache checkpoints tests
cat > README.md <<'MD'
# agenticAI

This repository implements a toy AgenticAI agent. It uses a
src/ package layout and thin scripts that import from the `agenticai` package.
MD
cat > .gitignore <<'GI'
__pycache__/
*.pyc
.venv/
data/cache/
checkpoints/
runs/
*.pt
*.pth
GI
cat > requirements.txt <<'REQ'
numpy>=1.24
tqdm>=4.66
tensorboard>=2.13
REQ
cat > pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "agenticai"
version = "0.0.1"
description = "Agentic AI"
requires-python = ">=3.10"
dependencies = []

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
TOML
