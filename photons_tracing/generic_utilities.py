import os

class GenericUtilities:

    @staticmethod
    def get_recent_intensity_tracing_file():
        data_folder = os.path.join(os.environ["USERPROFILE"], ".flim-labs", "data")
        files = [f for f in os.listdir(data_folder) if f.startswith("intensity-tracing")]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(data_folder, x)), reverse=True)
        return os.path.join(data_folder, files[0]) 