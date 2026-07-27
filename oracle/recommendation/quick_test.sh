#!/bin/bash
# Quick environment test

echo "=================================================="
echo "Running Quick Environment Tests"
echo "=================================================="
echo ""

# Test 1: Python
echo "[1/5] Testing Python..."
if python -c "print('Hello from Python')" 2>&1; then
    echo "✓ Python OK"
else
    echo "✗ Python FAILED"
fi
echo ""

# Test 2: MindSpore
echo "[2/5] Testing MindSpore..."
if python -c "import mindspore; print('MindSpore version:', mindspore.__version__)" 2>&1; then
    echo "✓ MindSpore OK"
else
    echo "✗ MindSpore FAILED"
fi
echo ""

# Test 3: Common packages
echo "[3/5] Testing packages (pandas, numpy, sklearn)..."
if python -c "import pandas, numpy, sklearn; print('All packages imported')" 2>&1; then
    echo "✓ Packages OK"
else
    echo "✗ Packages FAILED"
fi
echo ""

# Test 4: Wide&Deep model
echo "[4/5] Testing Wide&Deep model access..."
MISSING=""
for f in src/wide_and_deep.py src/metrics.py; do
    [ -f "/workspace/$f" ] || MISSING="$MISSING $f"
done
if [ -z "$MISSING" ]; then
    echo "✓ Vendored Wide&Deep source found (src/wide_and_deep.py, src/metrics.py)"
else
    echo "✗ Vendored Wide&Deep source NOT FOUND:$MISSING"
    echo "  These files are tracked in this repo — check out the full repository."
fi
echo ""

# Test 5: Jupyter
echo "[5/5] Testing Jupyter Lab..."
if pgrep -f "jupyter-lab" > /dev/null; then
    echo "✓ Jupyter Lab is running"
else
    echo "✗ Jupyter Lab is NOT running"
    echo "  Run: ./start_services.sh"
fi

echo ""
echo "=================================================="
echo "Tests Complete!"
echo "=================================================="
