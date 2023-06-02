import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class FileSearchThread(QThread):
    # The pyqtSignal is defined outside the __init__ method because it is a class attribute, not an instance attribute. 
    # It is defined at the class level and can be accessed by all instances of the class.
    search_progress = pyqtSignal(int)
    search_completed = pyqtSignal(list)

    def __init__(self, file_name, root_directory):
        
        super().__init__()
        self.file_name = file_name
        self.root_directory = root_directory
        

    def run(self):
        results = self.find_files(self.file_name, self.root_directory)
        self.search_completed.emit(results)

    def find_files(self, file_name, root_directory):
        results = []
        total_files = 0
        searched_files = 0

        for root, dirs, files in os.walk(root_directory):
            total_files += len(files)

        for root, dirs, files in os.walk(root_directory):
            for file in files:
                if file_name in file:
                    results.append(os.path.join(root, file))
                searched_files += 1
                progress = int((searched_files / total_files) * 100)
                self.search_progress.emit(progress)

        return results


class FileSearchWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        win = QWidget()
        hbox1 = QHBoxLayout()

        # Can you use layout?
        file_search = self.setWindowTitle("File Search")
        self.setGeometry(100, 100, 400, 350)
        hbox1.addWidget(file_search)
        hbox1.addStretch()

        file_name_text = self.input_label = QLabel("Enter file name:", self)
        self.input_label.setGeometry(10, 20, 120, 30)
        # hbox.addWidget(enter_box)

        self.input_text = QLineEdit(self)
        self.input_text.setGeometry(130, 20, 200, 30)

        self.root_button = QPushButton("Select Root Folder", self)
        self.root_button.setGeometry(130, 70, 200, 30)
        self.root_button.clicked.connect(self.select_root_folder)

        search_button = self.search_button = QPushButton("Search", self)
        self.search_button.setGeometry(150, 120, 100, 30)
        self.search_button.clicked.connect(self.start_search)
        hbox1.addWidget(search_button)
        hbox1.addStretch()


        self.progress_label = QLabel("Progress:", self)
        self.progress_label.setGeometry(20, 170, 100, 30)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(130, 170, 240, 30)
        self.progress_bar.setValue(0)

        self.result_label = QLabel("Found File Paths:", self)
        self.result_label.setGeometry(20, 220, 200, 30)

        self.result_text = QTextEdit(self)
        self.result_text.setGeometry(20, 250, 350, 80)
        self.result_text.setReadOnly(True)

        self.root_directory = ""

        self.file_search_thread = None

        win.setLayout(hbox1)
        win.show

    def select_root_folder(self):
        root_directory = QFileDialog.getExistingDirectory(self, "Select Root Folder")
        if root_directory:
            self.root_directory = root_directory

    def start_search(self):
        file_name = self.input_text.text()

        if not file_name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a file name.")
            return

        if not self.root_directory:
            QMessageBox.warning(self, "Invalid Input", "Please select a root folder.")
            return

        self.progress_bar.setValue(0)
        self.result_text.clear()

        self.file_search_thread = FileSearchThread(file_name, self.root_directory)
        self.file_search_thread.search_progress.connect(self.update_progress)
        self.file_search_thread.search_completed.connect(self.display_results)
        self.file_search_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_results(self, results):
        if results:
            self.result_text.setPlainText("\n".join(results))
        else:
            self.result_text.setPlainText("No files found.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileSearchWindow()
    window.show()
    sys.exit(app.exec_())
