py -3.12 -m venv .venv-intensity-tracing
.venv-intensity-tracing\Scripts\Activate.ps1
pip install pyinstaller
pip install -r .\requirements.txt
pip install flim_labs-1.0.62-cp312-none-win_amd64.whl
pip install PyQt6 --force-reinstall
pyinstaller --onefile --icon .\assets\intensity-tracing-logo.png --add-data "assets/*:assets" --add-data "export_data_scripts/*:export_data_scripts" --hidden-import=matplotlib.backends.backend_ps --hidden-import=matplotlib.backends.backend_agg  .\intensity_tracing.py
deactivate