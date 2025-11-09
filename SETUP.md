# Setup Instructions

## Virtual Environment Setup

### 1. Activate the Virtual Environment

**On Linux/Mac:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

After activation, your prompt should show `(venv)` at the beginning.

### 2. Verify Virtual Environment is Active

Check that you're using the venv's Python:
```bash
which python
# Should show: /proj/sprint/schema-translator/venv/bin/python
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python -c "import aiosqlite, fastapi, uvicorn, openai; print('✅ All packages installed')"
```

### 5. Run the Server

```bash
python -m uvicorn app.main:app --reload --port 8000
```

## Troubleshooting

### Issue: Packages not found after activating venv

**Solution:** Install packages directly into venv:
```bash
./venv/bin/pip install -r requirements.txt
```

### Issue: Wrong Python version

**Solution:** Recreate venv:
```bash
deactivate  # if venv is active
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Command not found after activating venv

**Solution:** Ensure PATH includes venv:
```bash
source venv/bin/activate
echo $PATH | grep venv
```

## Quick Start (One-liner)

```bash
cd /proj/sprint/schema-translator && source venv/bin/activate && pip install -r requirements.txt && python -m uvicorn app.main:app --reload --port 8000
```

