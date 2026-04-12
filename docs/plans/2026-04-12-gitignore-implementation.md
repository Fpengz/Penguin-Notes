# .gitignore Configuration Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a comprehensive `.gitignore` file for the `ml-scratch` repository that covers Python, LaTeX, and system artifacts while ensuring `.pdf` files are tracked.

**Architecture:** Replace the current minimal `.gitignore` with a detailed configuration organized by category (Python, LaTeX, System/Editor, Secrets).

**Tech Stack:** Git

---

### Task 1: Comprehensive .gitignore Update

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Read the existing .gitignore**
Done in research phase.

- [ ] **Step 2: Update .gitignore with full configuration**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.python-version
.venv/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Ruff & Linting
.ruff_cache/
.mypy_cache/
.pytest_cache/
.coverage
htmlcov/

# LaTeX
*.aux
*.fdb_latexmk
*.fls
*.log
*.out
*.toc
*.bbl
*.blg
*.synctex.gz
*.pdfsync
*.alg
*.loa
*.lof
*.lot
*.nav
*.snm
*.vrb
*.acn
*.acr
*.ist
*.glg
*.glo
*.gls
*.idx
*.ilg
*.ind
*.lof
*.lot
*.maf
*.mtc
*.mtc0
*.pyg

# Documentation Build Directories
docs/**/build/
func_surrogate/build/

# Jupyter Notebooks
.ipynb_checkpoints

# System
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Editors
.vscode/
.idea/
*.swp
*~

# Environment Variables
.env
.env.*
```

- [ ] **Step 3: Verify PDF tracking**

Run: `touch docs/test.pdf && git status`
Expected: `docs/test.pdf` should appear in "Untracked files".

Run: `rm docs/test.pdf`

- [ ] **Step 4: Commit the updated .gitignore**

Run: `git add .gitignore && git commit -m "chore: update .gitignore with comprehensive patterns"`
