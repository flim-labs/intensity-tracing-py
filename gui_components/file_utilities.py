import os
import re
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, '..'))

class FileUtils:
    @staticmethod
    def get_recent_intensity_tracing_file():
        data_folder = os.path.join(os.environ["USERPROFILE"], ".flim-labs", "data")
        files = [f for f in os.listdir(data_folder) if f.startswith("intensity-tracing")]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(data_folder, x)), reverse=True)
        return os.path.join(data_folder, files[0])
    
    @staticmethod   
    def get_recent_time_tagger_file():
        data_folder = os.path.join(os.environ["USERPROFILE"], ".flim-labs", "data")
        files = [
            f
            for f in os.listdir(data_folder)
            if f.startswith("time_tagger_intensity")
        ]
        files.sort(
            key=lambda x: os.path.getmtime(os.path.join(data_folder, x)), reverse=True
        )
        return os.path.join(data_folder, files[0])   
    
     
    @staticmethod
    def clean_filename(filename):
        # Keep only letters, numbers and underscores
        filename = filename.replace(" ", "_")
        return re.sub(r'[^a-zA-Z0-9_]', '', filename)      

