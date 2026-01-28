python -m venv .venv-intensity-tracing    
.\.venv-intensity-tracing\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m pip install -r .\requirements.txt
python -m pip install PyQt6 --force-reinstall
pyinstaller --onefile --icon .\assets\intensity-tracing-logo.png --add-data "assets/*:assets" --add-data "export_data_scripts/*:export_data_scripts" --hidden-import=matplotlib.backends.backend_ps --hidden-import=matplotlib.backends.backend_agg  .\intensity_tracing.py
deactivate