from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox
)

from generic_utilities import GenericUtilities 
import shutil

class ExportPdfUtilities:
    

     
    
    @staticmethod
    def download_python(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Python Files (*.py);;All Files (*)", options=options)
        if fileName:
            try:

                # Recupera l'ultimo file .bin creato
                bin_file_path = GenericUtilities.get_recent_intensity_tracing_file()
                # Determina i nomi dei file con le estensioni appropriate
                binFileName = f"{fileName}.bin"

                if bin_file_path:
                    shutil.copy(bin_file_path, binFileName)
                
                with open('plot_data_file.py', 'r') as file:
                    content = file.readlines()
                
                # Rimuove la funzione get_recent_intensity_tracing_file() e modifica il valore della variabile file_path
                new_content = []
                skip_function = False
                for line in content:
                    if 'def get_recent_intensity_tracing_file()' in line:
                        skip_function = True
                    elif skip_function and line.startswith('times ='):
                        skip_function = False
                    if not skip_function:
                        if 'times =' in line:
                            line = line+ f"\nfile_path = '{binFileName}'\n"  # Modifica il valore di file_path qui
                        new_content.append(line)
                
                # Scrive il nuovo contenuto nel file di destinazione
                with open(fileName, 'w') as file:
                    file.writelines(new_content)
                
                QMessageBox.information(self, "Save Successful", f"The file has been saved successfully: {fileName}")
            except Exception as e:
                QMessageBox.warning(self, "Save error", f"An error occurred while saving the file: {str(e)}")
    
              