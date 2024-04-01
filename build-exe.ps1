py -3.9 -m venv .venv-intensity-tracing
.venv-intensity-tracing\Scripts\Activate.ps1
pip install pyinstaller
pip install -r .\requirements.txt
pyinstaller --noconsole --onefile --icon .\assets\intensity-tracing-logo.png --add-data "assets/*:assets"  .\intensity_tracing.py
deactivate