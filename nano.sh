#!/bin/bash

# Script untuk membuat struktur proyek Python standar
# Membuat direktori dan file-file penting untuk proyek Python

# Menyesuaikan untuk Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    VENV_PATH=".venv/Scripts/activate"
    PYTHON_CMD="python"
else
    VENV_PATH=".venv/bin/activate"
    PYTHON_CMD="python3"
fi

echo "Membuat struktur proyek Python..."

# Membuat direktori virtual environment
echo "Membuat direktori .venv..."
mkdir -p .venv

# Membuat direktori .vscode dan file konfigurasi
echo "Membuat direktori .vscode dan file konfigurasi..."
mkdir -p .vscode
cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
EOF

cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
EOF

cat > .vscode/tasks.json << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run Python",
            "type": "shell",
            "command": "python",
            "args": ["${file}"],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared",
                "showReuseMessage": true,
                "clear": false
            }
        }
    ]
}
EOF

# Membuat file .gitignore
echo "Membuat file .gitignore..."
cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
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
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
env/

# IDE and editor files
.vscode/
.idea/
*.swp
*.swo
*~

# Environment variables
.env
.env.local

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Jupyter Notebook
.ipynb_checkpoints

# Coverage reports
.coverage
htmlcov/

# Pytest
.pytest_cache/

# Documentation
docs/_build/

# Distribution / packaging
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage

# Local configuration
config.json
secrets.json

# Data files (if not specifically needed in version control)
data/*.csv
data/*.json
data/*.xlsx
data/*.db
EOF

# Membuat file .env
echo "Membuat file .env..."
cat > .env << 'EOF'
# Environment variables
# Contoh:
# DATABASE_URL=sqlite:///app.db
# SECRET_KEY=your-secret-key
# DEBUG=True

EOF

# Membuat direktori docs
echo "Membuat direktori docs..."
mkdir -p docs
cat > docs/README.md << 'EOF'
# Dokumentasi Proyek

## Struktur Proyek

## Penggunaan

## Kontribusi

## Lisensi
EOF

# Membuat direktori src jika belum ada
echo "Membuat direktori src..."
mkdir -p src

# Membuat file __init__.py di src
touch src/__init__.py

# Membuat direktori tests
echo "Membuat direktori tests..."
mkdir -p tests
touch tests/__init__.py

# Membuat file requirements-dev.txt
echo "Membuat file requirements-dev.txt..."
cat > requirements-dev.txt << 'EOF'
# Development dependencies
pytest>=6.0
pytest-cov
black
flake8
mypy
jupyter
EOF

# Membuat file setup.py jika belum ada
if [ ! -f setup.py ]; then
    echo "Membuat file setup.py..."
    cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="project_name",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Tambahkan dependencies di sini dari requirements.txt
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A short description of your project",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/yourproject",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
EOF
fi

# Membuat file pyproject.toml jika belum ada
if [ ! -f pyproject.toml ]; then
    echo "Membuat file pyproject.toml..."
    cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "project_name"
version = "0.1.0"
description = "A short description of your project"
readme = "README.md"
authors = [{name = "Your Name", email = "your.email@example.com"}]
license = {text = "MIT"}
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
requires-python = ">=3.6"
dependencies = [
    # Tambahkan dependencies di sini
]

[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "pytest-cov",
    "black",
    "flake8",
    "mypy",
    "jupyter"
]

[tool.setuptools.packages.find]
where = ["src"]
EOF
fi

# Membuat file .pre-commit-config.yaml jika belum ada
if [ ! -f .pre-commit-config.yaml ]; then
    echo "Membuat file .pre-commit-config.yaml..."
    cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
EOF
fi

# Membuat file Makefile jika belum ada
if [ ! -f Makefile ]; then
    echo "Membuat file Makefile..."
    cat > Makefile << 'EOF'
.PHONY: install run test format lint clean

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Run the application
run:
	python src/main.py

# Run tests
test:
	pytest tests/

# Format code with black
format:
	black src/ tests/

# Lint code with flake8
lint:
	flake8 src/ tests/

# Clean up
clean:
	rm -rf __pycache__/
	rm -rf *.pyc
	rm -rf .pytest_cache/
	rm -rf .coverage
EOF
fi

# Membuat direktori assets untuk menyimpan file-file tambahan
echo "Membuat direktori assets..."
mkdir -p assets

# Membuat direktori config jika belum ada
if [ ! -d config ]; then
    echo "Membuat direktori config..."
    mkdir -p config
    cat > config/config.yaml << 'EOF'
# Konfigurasi aplikasi
app:
  name: "project_name"
  debug: false
  environment: "development"

database:
  host: "localhost"
  port: 5432
  name: "myapp_db"

logging:
  level: "INFO"
EOF
fi

# Fungsi untuk membuat virtual environment
create_venv() {
    echo "Membuat virtual environment..."
    $PYTHON_CMD -m venv .venv
    if [ $? -eq 0 ]; then
        echo "Virtual environment berhasil dibuat di .venv/"
    else
        echo "Gagal membuat virtual environment"
        exit 1
    fi
}

# Jika argumen --with-venv diberikan, buat virtual environment
if [ "$1" == "--with-venv" ]; then
    create_venv
fi

echo "Struktur proyek Python telah selesai dibuat!"
echo ""
echo "Struktur yang dibuat:"
echo "- .venv/ (direktori virtual environment)"
echo "- .vscode/ (konfigurasi VSCode)"
echo "- .gitignore (file untuk mengabaikan file-file yang tidak perlu ditrack)"
echo "- .env (file environment variables)"
echo "- docs/ (dokumentasi)"
echo "- src/ (sumber kode utama)"
echo "- tests/ (file-file pengujian)"
echo "- requirements-dev.txt (dependencies untuk development)"
echo "- setup.py (file setup untuk packaging)"
echo "- pyproject.toml (konfigurasi modern untuk packaging)"
echo "- .pre-commit-config.yaml (konfigurasi pre-commit hooks)"
echo "- Makefile (perintah-perintah otomatisasi)"
echo "- assets/ (file-file aset)"
echo "- config/ (file-file konfigurasi)"
echo ""
echo "Untuk memulai proyek:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "1. Buat virtual environment: python -m venv .venv (atau jalankan skrip ini dengan argumen --with-venv)"
    echo "2. Aktifkan virtual environment: .venv\Scripts\activate"
    echo "3. Install dependencies: pip install -r requirements.txt"
else
    echo "1. Buat virtual environment: python3 -m venv .venv (atau jalankan skrip ini dengan argumen --with-venv)"
    echo "2. Aktifkan virtual environment: source .venv/bin/activate"
    echo "3. Install dependencies: pip install -r requirements.txt"
fi
echo "4. Tambahkan kode Anda ke direktori src/"
echo "5. Tambahkan pengujian Anda ke direktori tests/"