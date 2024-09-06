import sys
import os
import csv
import shutil
from collections import defaultdict
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QFileDialog, QLabel, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class CopyRenameApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Copy and Rename Photos')
        self.setGeometry(100, 100, 400, 300)
        
        self.setWindowIcon(QIcon('whiteraven.jpg')) 
        
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.result_label = QLabel('')
        self.result_label.setFixedWidth(350)  
        self.result_label.setWordWrap(True)   
        self.layout.addWidget(self.result_label)

        self.csv_file_label = QLabel('CSV File:')
        self.csv_file_edit = QLineEdit()
        self.csv_file_button = QPushButton('Browse...')
        self.csv_file_button.clicked.connect(self.select_csv_file)
        self.layout.addWidget(self.csv_file_label)
        self.layout.addWidget(self.csv_file_edit)
        self.layout.addWidget(self.csv_file_button)

        self.input_dir_label = QLabel('Input Directory:')
        self.input_dir_edit = QLineEdit()
        self.input_dir_button = QPushButton('Browse...')
        self.input_dir_button.clicked.connect(self.select_input_dir)
        self.layout.addWidget(self.input_dir_label)
        self.layout.addWidget(self.input_dir_edit)
        self.layout.addWidget(self.input_dir_button)

        self.output_dir_label = QLabel('Output Directory:')
        self.output_dir_edit = QLineEdit()
        self.output_dir_button = QPushButton('Browse...')
        self.output_dir_button.clicked.connect(self.select_output_dir)
        self.layout.addWidget(self.output_dir_label)
        self.layout.addWidget(self.output_dir_edit)
        self.layout.addWidget(self.output_dir_button)

        self.single_folder_dir_label = QLabel('Single Folder Directory:')
        self.single_folder_dir_edit = QLineEdit()
        self.single_folder_dir_button = QPushButton('Browse...')
        self.single_folder_dir_button.clicked.connect(self.select_single_folder_dir)
        self.layout.addWidget(self.single_folder_dir_label)
        self.layout.addWidget(self.single_folder_dir_edit)
        self.layout.addWidget(self.single_folder_dir_button)

        self.filename_template_label = QLabel('Filename Template:')
        self.filename_template_edit = QLineEdit('%Last Name%_%First Name%.jpg')
        self.layout.addWidget(self.filename_template_label)
        self.layout.addWidget(self.filename_template_edit)

        self.run_button = QPushButton('Run')
        self.run_button.clicked.connect(self.run_copy_rename)
        self.layout.addWidget(self.run_button)

        self.result_label = QLabel('')
        self.result_label.setFixedWidth(350)  
        self.result_label.setWordWrap(True)

        self.copyright_label = QLabel('© Shar Hess and Dev Pipeline LLC')
        self.layout.addWidget(self.copyright_label)
        # self.setMinimumSize(550, 400)

    def select_csv_file(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Select CSV File', '', 'CSV Files (*.csv)')
        if file:
            self.csv_file_edit.setText(file)

    def select_input_dir(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Input Directory')
        if directory:
            self.input_dir_edit.setText(directory)

    def select_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if directory:
            self.output_dir_edit.setText(directory)

    def select_single_folder_dir(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Single Folder Directory')
        if directory:
            self.single_folder_dir_edit.setText(directory)

    def run_copy_rename(self):
        csv_file = self.csv_file_edit.text()
        input_dir = self.input_dir_edit.text()
        output_dir = self.output_dir_edit.text()
        single_folder_dir = self.single_folder_dir_edit.text()
        filename_template = self.filename_template_edit.text()

        result = copy_rename(csv_file, input_dir, output_dir, single_folder_dir, filename_template)
        QMessageBox.information(self, 'Result', result)
        self.result_label.setText(result)

def copy_rename(csv_file, input_dir, output_dir, single_folder_dir, filename_template='%Last Name%_%First Name%.jpg'):
    photo_dict = {}
    processed_image_numbers = set()
    all_image_numbers = set()
    duplicates = defaultdict(list)

    try:
        with open(csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Image#']:
                    image_number = row['Image#']
                    all_image_numbers.add(image_number)
                    duplicates[image_number].append(row)

                    photo_dict[image_number] = row
    except Exception as e:
        return f"Error reading CSV file '{csv_file}': {e}"

    duplicate_image_numbers = [num for num, rows in duplicates.items() if len(rows) > 1]
    if duplicate_image_numbers:
        duplicate_message = f"Duplicate Image Numbers: {', '.join(duplicate_image_numbers)}"
    else:
        duplicate_message = "No duplicate image numbers found."

    try:
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        
        if not os.path.isdir(single_folder_dir):
            os.makedirs(single_folder_dir)
    except Exception as e:
        return f"Error creating output directories: {e}"

    imagenames = []
    try:
        for entry in os.scandir(input_dir):
            if entry.path.endswith(".jpg") and entry.is_file():
                imagenames.append(entry.name)
    except Exception as e:
        return f"Error scanning input directory '{input_dir}': {e}"

    for img in imagenames:
        try:
            first_underscore = img.find('_')
            if first_underscore == -1 or img.find('.') == -1:
                raise ValueError("Filename must contain at least one underscore and one period")
            
            start_index = first_underscore + 1
            end_index = img.find('.')
            num_segment = img[start_index:end_index].strip()
            
            if num_segment in photo_dict:
                person = photo_dict[num_segment]
                
                old_filepath = os.path.join(input_dir, img)

                temp_filename = []
                for i in filename_template.split('%'):
                    if i in person.keys():
                        temp_filename.append(person[i])
                    else:
                        temp_filename.append(i)
                new_filename = ''.join(temp_filename)

                grade_folder_name = f"grade_{person['Grade']}"
                if person['Grade'] == 'Faculty':
                    grade_folder_name = 'Faculty'
                
                grade_folder_dir = os.path.join(output_dir, grade_folder_name)
                teacher_folder_name = person['Teacher'].replace(", " , "_")
                teacher_folder_dir = os.path.join(grade_folder_dir, teacher_folder_name)
                
                if not os.path.isdir(grade_folder_dir):
                    os.makedirs(grade_folder_dir)
                
                if not os.path.isdir(teacher_folder_dir):
                    os.makedirs(teacher_folder_dir)
               
                if person['Grade'] == 'Faculty':
                    new_filepath_nested = os.path.join(output_dir, 'Faculty', new_filename)
                else:
                    new_filepath_nested = os.path.join(output_dir, grade_folder_name, teacher_folder_name, new_filename)

                shutil.copy(old_filepath, new_filepath_nested)
                
                new_filepath_single = os.path.join(single_folder_dir, new_filename)
                shutil.copy(old_filepath, new_filepath_single)
                
                processed_image_numbers.add(num_segment)
            else:
                print(f"Segment '{num_segment}' not found in dictionary keys.")
        
        except Exception as e:
            print(f"Error processing file '{img}': {e}")

    missing_image_numbers = all_image_numbers - processed_image_numbers
    if missing_image_numbers:
        missing_message = f"Missing image numbers from CSV: {', '.join(missing_image_numbers)}"
        return f"{missing_message}\n{duplicate_message}"
    return "Processing complete."

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CopyRenameApp()
    window.show()
    sys.exit(app.exec_())
