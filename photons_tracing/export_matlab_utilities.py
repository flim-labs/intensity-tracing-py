from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox
)

from generic_utilities import GenericUtilities 
import shutil

class ExportMatlabUtilities:
    
    @staticmethod
    def download_matlab(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*)", options=options)
        if fileName:
            try:

                bin_file_path = GenericUtilities.get_recent_intensity_tracing_file()
                binFileName = f"{fileName}.bin"

                if bin_file_path:
                    shutil.copy(bin_file_path, binFileName)
                
                with open('plot_data_file.m', 'r') as file:
                    content = file.readlines()
                
                new_content = []
                skip_function = False
                for line in content:
                    
                    if '% Get most recent intensity tracing .bin file from your local computer' in line:
                        skip_function = True
                    elif skip_function and line.startswith('metadata ='):
                        skip_function = False
                    if not skip_function:
                        if 'metadata =' in line:
                            line = line+ f"\nfile_path = '{binFileName}'\n"
                
                
                with open(f"{fileName}.m", 'w') as file:
                    file.writelines(new_content)
                
                QMessageBox.information(self, "Save Successful", f"The file has been saved successfully: {fileName}")
            except Exception as e:
                QMessageBox.warning(self, "Save error", f"An error occurred while saving the file: {str(e)}")
    
              