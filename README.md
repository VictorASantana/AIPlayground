# AIPlayground

# Setting Up the Python Virtual Environment and Installing Dependencies

## 1. Create and Activate a Virtual Environment

To create a virtual environment named `.venv`, follow these steps:

### On macOS and Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### On Windows (CMD):
```cmd
python -m venv .venv
.venv\Scripts\activate
```

### On Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

After activation, your terminal should show a `(.venv)` prefix, indicating that the virtual environment is active.

## 2. Install Streamlit

Once the virtual environment is activated, install Streamlit by running:
```bash
pip install streamlit
```

## 3. Install Dependencies from `requirements.txt`

If you have a `requirements.txt` file with additional dependencies, install them using:
```bash
pip install -r requirements.txt
```

## 4. Verify the Installation

To ensure everything is installed correctly, you can check the installed packages with:
```bash
pip list
```

To confirm Streamlit is working, run:
```bash
streamlit hello
```

## 5. Deactivating the Virtual Environment

When you're done working in the virtual environment, deactivate it by running:
```bash
deactivate
```
This will return you to the system's default Python environment.

## Notes
- Ensure you have Python installed (recommended version: Python 3.8+).
- If `pip` is outdated, update it before installing dependencies:
  ```bash
  pip install --upgrade pip
  ```

