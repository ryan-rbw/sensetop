#!/bin/bash
# Environment detection script for SenseTop multi-environment development
# Run this before starting work to determine your current environment

echo "========================================"
echo "SenseTop Environment Detection"
echo "========================================"
echo ""

# Detect OS
echo "1. Operating System:"
if [[ -f /proc/device-tree/model ]]; then
    MODEL=$(cat /proc/device-tree/model 2>/dev/null)
    echo "   Device: $MODEL"
    if [[ "$MODEL" == *"Raspberry Pi 5"* ]]; then
        ENV_TYPE="TARGET_HARDWARE"
        echo "   → Raspberry Pi 5 detected ✓"
    else
        ENV_TYPE="DEVELOPMENT"
        echo "   → Not Raspberry Pi 5"
    fi
else
    ENV_TYPE="DEVELOPMENT"
    echo "   Platform: $(uname -s) $(uname -m)"
    echo "   → Development machine"
fi
echo ""

# Check for Sense HAT hardware
echo "2. Sense HAT Hardware:"
if command -v i2cdetect &> /dev/null; then
    I2C_OUTPUT=$(i2cdetect -y 1 2>/dev/null)
    if echo "$I2C_OUTPUT" | grep -qE "(1c|5f|6a)"; then
        HAS_HARDWARE=true
        echo "   I2C devices detected:"
        echo "$I2C_OUTPUT" | grep -E "(1c|5f|6a)" | sed 's/^/     /'
        echo "   → Sense HAT hardware present ✓"
    else
        HAS_HARDWARE=false
        echo "   → No Sense HAT hardware detected"
    fi
else
    HAS_HARDWARE=false
    echo "   → i2c-tools not installed (no hardware detection possible)"
fi
echo ""

# Check Python version
echo "3. Python Environment:"
PYTHON_VERSION=$(python3 --version 2>&1)
echo "   $PYTHON_VERSION"
if python3 -c "import sensetop" 2>/dev/null; then
    echo "   → sensetop module importable ✓"
else
    echo "   → sensetop not installed (run 'pip install -e .' or 'make install-dev')"
fi
echo ""

# Check for git repository
echo "4. Git Repository:"
if git rev-parse --is-inside-work-tree &> /dev/null; then
    BRANCH=$(git branch --show-current)
    echo "   Current branch: $BRANCH"
    STATUS=$(git status --porcelain | wc -l)
    if [ "$STATUS" -eq 0 ]; then
        echo "   Working tree: clean ✓"
    else
        echo "   Working tree: $STATUS modified files"
    fi
else
    echo "   → Not in a git repository"
fi
echo ""

# Check for required tools
echo "5. Development Tools:"
MISSING_TOOLS=()

# Core tools (all environments)
for tool in python3 git pip; do
    if command -v $tool &> /dev/null; then
        echo "   ✓ $tool"
    else
        echo "   ✗ $tool (REQUIRED)"
        MISSING_TOOLS+=("$tool")
    fi
done

# Development tools (optional but recommended)
DEV_TOOLS=(pytest black pylint flake8 isort mypy)
MISSING_DEV=()
for tool in "${DEV_TOOLS[@]}"; do
    if command -v $tool &> /dev/null; then
        echo "   ✓ $tool"
    else
        MISSING_DEV+=("$tool")
    fi
done

if [ ${#MISSING_DEV[@]} -gt 0 ]; then
    echo "   ℹ  Optional dev tools missing: ${MISSING_DEV[*]}"
fi

# Hardware tools (only for Pi)
if [ "$ENV_TYPE" == "TARGET_HARDWARE" ]; then
    if command -v i2cdetect &> /dev/null; then
        echo "   ✓ i2c-tools"
    else
        echo "   ✗ i2c-tools (recommended for Pi)"
        MISSING_TOOLS+=("i2c-tools")
    fi
fi
echo ""

# Summarize environment
echo "========================================"
echo "ENVIRONMENT SUMMARY"
echo "========================================"
if [ "$ENV_TYPE" == "TARGET_HARDWARE" ] && [ "$HAS_HARDWARE" == true ]; then
    echo "Environment Type: TARGET HARDWARE (Raspberry Pi 5)"
    echo ""
    echo "✓ You can test with real Sense HAT sensors"
    echo "✓ Run: python -m sensetop"
    echo "✓ Use for hardware validation and verification"
    echo ""
    echo "⚠ WARNING: Do not perform heavy development here"
    echo "⚠ Use development machine for coding, testing, commits"
    echo "⚠ Pull code from GitHub, validate, report issues"
elif [ "$ENV_TYPE" == "DEVELOPMENT" ]; then
    echo "Environment Type: DEVELOPMENT"
    echo ""
    echo "✓ Use mocked sensors for development"
    echo "✓ Run: make demo or python run_local_demo.py"
    echo "✓ Full development workflow: code, test, lint, commit, push"
    echo "✓ All tests should pass with mocks"
    echo ""
    if [ "$HAS_HARDWARE" == true ]; then
        echo "Note: Sense HAT detected but not on Raspberry Pi 5"
        echo "      → Treat as development environment"
    fi
else
    echo "Environment Type: UNKNOWN"
    echo ""
    echo "⚠ Could not definitively determine environment"
    echo "→ Default to DEVELOPMENT workflow"
    echo "→ Use mocks for safety"
fi
echo "========================================"
echo ""

# Installation instructions if tools are missing
if [ ${#MISSING_TOOLS[@]} -gt 0 ] || [ ${#MISSING_DEV[@]} -gt 0 ]; then
    echo "INSTALLATION INSTRUCTIONS"
    echo "========================================"

    if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
        echo ""
        echo "⚠ Missing required tools: ${MISSING_TOOLS[*]}"
        echo ""
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            if [ -f /etc/debian_version ]; then
                echo "Install on Debian/Ubuntu/Raspberry Pi OS:"
                echo "  sudo apt update"
                echo "  sudo apt install -y python3-full python3-pip git i2c-tools"
            else
                echo "Install using your package manager (yum, dnf, pacman, etc.)"
            fi
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            echo "Install on macOS:"
            echo "  brew install python3 git"
        fi
    fi

    if [ ${#MISSING_DEV[@]} -gt 0 ]; then
        echo ""
        echo "ℹ  Optional development tools missing: ${MISSING_DEV[*]}"
        echo ""
        echo "Install using pipx (recommended):"
        echo "  sudo apt install -y pipx"
        echo "  pipx ensurepath"
        echo "  # Log out and back in, then:"
        for tool in "${MISSING_DEV[@]}"; do
            echo "  pipx install $tool"
        done
        echo ""
        echo "Or install via apt (if available):"
        echo "  sudo apt install -y python3-pytest python3-pytest-cov"
        echo ""
        echo "What is pipx?"
        echo "  pipx installs Python tools in isolated environments"
        echo "  while making them globally available. Safer than"
        echo "  'pip install --break-system-packages'."
    fi

    echo ""
    echo "After installing, re-run this script to verify."
    echo "========================================"
fi
