# Wide&Deep Career Recommender - Quick Reference

## Daily Workflow

### Starting Work
```bash
# On host machine
docker start dao-recommender
docker exec -it dao-recommender bash

# Inside container
ws                # Navigate to workspace (alias)
start             # Start Jupyter Lab (alias)
token             # Get access token (alias)
```

Open browser: http://localhost:8888

### Ending Work
```bash
# Inside container
stop              # Stop services (alias)
exit

# On host (optional)
docker stop dao-recommender
```

## Helper Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `start_services.sh` | Start Jupyter Lab | `./start_services.sh` or `start` |
| `stop_services.sh` | Stop all services | `./stop_services.sh` or `stop` |
| `get_token.sh` | Get Jupyter token | `./get_token.sh` or `token` |
| `status.sh` | Check system status | `./status.sh` or `status` |
| `quick_test.sh` | Run environment tests | `./quick_test.sh` or `test` |
| `setup_env.sh` | Setup environment | `./setup_env.sh` |

## Bash Aliases

### Navigation
```bash
ws        # cd /workspace
wd        # cd to Wide&Deep model
nb        # cd /workspace/notebooks
dt        # cd /workspace/data
sc        # cd /workspace/scripts
```

### Service Management
```bash
start     # Start Jupyter Lab
stop      # Stop services
restart   # Restart services
token     # Get Jupyter token
```

### Status & Testing
```bash
status    # Show system status
test      # Run quick tests
test-ms   # Test MindSpore import
test-pd   # Test pandas import
test-np   # Test numpy import
```

### Jupyter
```bash
jlog      # View Jupyter logs (tail -f)
jcheck    # Check if Jupyter is running
```

### Utilities
```bash
ll        # ls -lah
tree2     # tree -L 2
dus       # Show directory sizes
pip-list  # List key Python packages
```

## Common Commands

### Check Python & MindSpore
```bash
python --version
python -c "import mindspore; print(mindspore.__version__)"
```

### View Logs
```bash
cat /workspace/logs/jupyter.log
tail -f /workspace/logs/jupyter.log
```

### Check Running Processes
```bash
ps aux | grep jupyter
ps aux | grep python
```

### Directory Navigation
```bash
# Vendored Wide&Deep model source
cd /workspace/src

# Your data
cd /workspace/data

# Your notebooks
cd /workspace/notebooks

# Your custom scripts
cd /workspace/scripts
```

## Troubleshooting

### Issue: Python command not found
```bash
ln -sf /usr/bin/python3.10 /usr/bin/python
```

### Issue: Jupyter won't start
```bash
stop
rm /workspace/logs/jupyter.log
start
```

### Issue: Import errors
```bash
pip install mindspore pandas numpy scikit-learn matplotlib
```

### Issue: Check what's taking space
```bash
dus                    # See directory sizes
df -h /workspace       # Check disk space
```

## Project Structure

```
/workspace/
├── checkpoints/              # Model checkpoints
├── data/
│   ├── raw/                 # Raw datasets (Kaggle, etc.)
│   │   ├── linkedin/
│   │   ├── salaries/
│   │   └── github/
│   ├── processed/           # Processed CSV files
│   └── mindrecord/          # MindSpore format datasets
├── logs/                    # Application logs
├── src/                     # Vendored Wide&Deep source (Apache 2.0, Huawei)
│   ├── wide_and_deep.py     #   WideDeepModel, NetWithLossClass, TrainStepWrap
│   └── metrics.py           #   AUCMetric
├── notebooks/               # Jupyter notebooks
├── scripts/                 # Training/preprocessing scripts
├── requirements.txt        # Python dependencies
├── start_services.sh        # Start Jupyter
├── stop_services.sh         # Stop services
├── get_token.sh            # Get Jupyter token
├── status.sh               # System status
├── quick_test.sh           # Run tests
└── setup_env.sh            # Environment setup
```

## Useful Python Snippets

### Import MindSpore
```python
import mindspore as ms
from mindspore import Tensor
import mindspore.numpy as mnp
```

### Import Wide&Deep
The model source is vendored in this repo under `src/`, so no clone of
`mindspore-ai/models` is required. From the repo root (`/workspace` inside the
container) it imports directly:

```python
from src.wide_and_deep import WideDeepModel
from src.metrics import AUCMetric
```

From a notebook in a subdirectory, put the repo root on the path first:

```python
import sys
from pathlib import Path

REPO_ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents]
                 if (p / "src" / "wide_and_deep.py").is_file())
sys.path.insert(0, str(REPO_ROOT))
```

### Load data
```python
import pandas as pd
df = pd.read_csv('/workspace/data/processed/some_file.csv')
```

## Next Steps

1. **Week 1**: Read documentation
2. **Week 2**: Download Kaggle datasets
3. **Week 3**: Preprocess data
4. **Week 4-6**: Model development & training
5. **Week 7**: Evaluation & deployment
