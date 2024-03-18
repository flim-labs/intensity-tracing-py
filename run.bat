py -3.9 -m venv .venv

rem activate the virtual environment
cmd /k ".venv\Scripts\activate"

pip install -r requirements.txt
python intensity_tracing.py