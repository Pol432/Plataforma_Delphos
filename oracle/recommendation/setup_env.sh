#!/bin/bash
# One-time environment setup (Python, MindSpore, packages)

echo "=================================================="
echo "Setting Up Environment"
echo "=================================================="
echo ""

# Python symlinks
echo "[1/4] Setting up Python symlinks..."
if [ ! -L /usr/bin/python ] || [ ! -e /usr/bin/python ]; then
    ln -sf /usr/bin/python3.10 /usr/bin/python
    ln -sf /usr/bin/python3.10 /usr/bin/python3
    echo "✓ Python symlinks created"
else
    echo "✓ Python symlinks already exist"
fi
echo ""

# MindSpore
# The pinned version lives in requirements.txt and is read from there, so this
# script and requirements.txt cannot drift apart.
REQUIREMENTS="/workspace/requirements.txt"
MINDSPORE_PIN=$(grep -oE '^mindspore==[0-9][^[:space:]#]*' "$REQUIREMENTS")

echo "[2/4] Checking MindSpore installation..."
if [ -z "$MINDSPORE_PIN" ]; then
    echo "✗ Could not read the mindspore pin from $REQUIREMENTS"
    exit 1
fi
WANTED="${MINDSPORE_PIN#mindspore==}"
INSTALLED=$(python -c "import mindspore; print(mindspore.__version__)" 2>/dev/null)
if [ "$INSTALLED" = "$WANTED" ]; then
    echo "✓ MindSpore already installed (version $INSTALLED)"
else
    [ -n "$INSTALLED" ] && echo "⚠ MindSpore $INSTALLED installed, want $WANTED — reinstalling"
    echo "Installing MindSpore $WANTED..."
    pip install "$MINDSPORE_PIN" -i https://repo.mindspore.cn/pypi/simple \
      --trusted-host repo.mindspore.cn \
      --extra-index-url https://repo.huaweicloud.com/repository/pypi/simple
    echo "✓ MindSpore installed"
fi
echo ""

# Dependencies
echo "[3/4] Installing Python packages..."
pip install -q -r "$REQUIREMENTS"

echo "✓ Packages installed"
echo ""

# Vendored model source
echo "[4/4] Checking vendored Wide&Deep source..."
MISSING=""
for f in src/wide_and_deep.py src/metrics.py; do
    [ -f "/workspace/$f" ] || MISSING="$MISSING $f"
done
if [ -z "$MISSING" ]; then
    echo "✓ Vendored model source present (src/wide_and_deep.py, src/metrics.py)"
    echo "  No clone of mindspore-ai/models is needed."
else
    echo "✗ Missing vendored source:$MISSING"
    echo "  These files are tracked in this repo — check out the full repository."
    exit 1
fi

echo ""
echo "=================================================="
echo "Environment Setup Complete!"
echo "=================================================="
echo ""
echo "Run './status.sh' to verify everything"
