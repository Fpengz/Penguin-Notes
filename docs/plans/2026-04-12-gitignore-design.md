# .gitignore Configuration Design - 2026-04-12

## Purpose
The purpose of this design is to create a robust and comprehensive `.gitignore` file for the `ml-scratch` project, which contains both Python source code and LaTeX documentation.

## Requirements
- **Python-Specific:** Ignore virtual environments, bytecode, and linter caches (e.g., `.venv/`, `__pycache__/`, `.ruff_cache/`).
- **LaTeX-Specific:** Ignore intermediate build files (`*.aux`, `*.log`, `*.out`, etc.) and `build/` directories within documentation folders.
- **Tracked Artifacts:** Explicitly **include** final `.pdf` files as requested by the user.
- **OS/Editor-Specific:** Ignore common system artifacts (e.g., `.DS_Store`) and editor-specific directories (e.g., `.vscode/`, `.idea/`).
- **Security:** Ensure sensitive environment variable files (e.g., `.env`) are ignored.

## Design Sections

### 1. Python & Environment Management
- Virtual Environment: `.venv/`
- Bytecode: `__pycache__/`, `*.py[cod]`, `*$py.class`
- Ruff Cache: `.ruff_cache/`
- Packaging: `build/`, `dist/`, `*.egg-info/`, `wheels/`

### 2. LaTeX Documentation
- Intermediate Files: `*.aux`, `*.log`, `*.out`, `*.toc`, `*.bbl`, `*.blg`, `*.synctex.gz`, `*.fdb_latexmk`, `*.fls`, `*.pdfsync`
- Build Directories: `docs/**/build/`, `func_surrogate/build/`
- **PDF Tracking:** `.pdf` files will **not** be ignored.

### 3. System & Editor Patterns
- macOS: `.DS_Store`, `.AppleDouble`, `.LSOverride`
- Editors: `.vscode/`, `.idea/`, `*.swp`, `*~`
- Secrets: `.env`, `.env.*`

## Success Criteria
- Running `git status` after applying the `.gitignore` should not show any of the specified ignored files or directories.
- Final PDF documents should be visible to `git` for tracking.
