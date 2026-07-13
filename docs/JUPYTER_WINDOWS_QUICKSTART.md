# Jupyter quickstart on Windows

Local working directory used by the project author:

```text
C:\Users\abc\Desktop\New Folder (2)\New folder\PROVISNAL RELATED
```

## 1. Open Anaconda Prompt or PowerShell

```powershell
cd "C:\Users\abc\Desktop\New Folder (2)\New folder\PROVISNAL RELATED"
git clone https://github.com/Parveen117/EMK-material-response-public.git
cd EMK-material-response-public
```

If the folder already exists:

```powershell
cd "C:\Users\abc\Desktop\New Folder (2)\New folder\PROVISNAL RELATED\EMK-material-response-public"
git pull origin main
```

## 2. Create a clean environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pytest jupyter pandas matplotlib
```

## 3. Run the tests

```powershell
python -m pytest -q
```

## 4. Generate the demo output

```powershell
python src\emk_lambda_material_response_v1.py
```

The generated file is:

```text
outputs\material_response_v1_demo.csv
```

Compare it with:

```text
outputs\material_response_v1_expected.csv
```

## 5. Launch Jupyter

```powershell
jupyter notebook
```

In a notebook cell:

```python
import sys
from pathlib import Path

repo_root = Path.cwd()
sys.path.insert(0, str(repo_root / "src"))

from emk_lambda_material_response_v1 import demo_materials, evaluate_material

responses = [evaluate_material(material) for material in demo_materials()]
[(r.name, r.response_label, r.lambda_curvature, r.reciprocity_gap) for r in responses]
```

To inspect the frozen output:

```python
import pandas as pd

expected = pd.read_csv("outputs/material_response_v1_expected.csv")
expected
```

## Interpretation warning

The bundled materials are synthetic proxy descriptors. They demonstrate deterministic behavior of the computational framework; they are not direct experimental measurements or validated claims about the named materials.
