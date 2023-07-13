from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QListWidgetItem, QListWidget, QFileDialog, QLineEdit, QHBoxLayout, QLabel, QSizePolicy, QProgressDialog, QMessageBox
from PyQt6.QtCore import Qt
import os
import shutil

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

class App(QWidget):
    def __init__(self):
        super().__init__()

        self.title = 'Node Modules Cleaner'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('/logo.png'))
        # Create widgets
        self.layout = QVBoxLayout()
        self.select_directory_button = QPushButton('Select Directory')
        self.directory_display = QLineEdit()
        self.directory_display.setReadOnly(True)  # User cannot edit this field
        self.directory_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)  # Make width responsive

        self.directory_label = QLabel('Selected directory:')
        self.search_button = QPushButton('Search')
        self.delete_button = QPushButton('Delete')
        self.select_all_button = QPushButton('Select All')  # New button
        self.unselect_all_button = QPushButton('Unselect All')  # New button
        self.button_layout = QHBoxLayout()  # New layout for buttons
        self.modules_list = QListWidget()

        # Connect signals and slots
        self.select_directory_button.clicked.connect(self.select_directory)
        self.search_button.clicked.connect(self.search)
        self.delete_button.clicked.connect(self.delete)
        self.select_all_button.clicked.connect(self.select_all)
        self.unselect_all_button.clicked.connect(self.unselect_all)

        # Set button layout
        self.button_layout.addWidget(self.select_all_button)
        self.button_layout.addWidget(self.unselect_all_button)

        # Set main layout
        self.layout.addWidget(self.select_directory_button)
        self.layout.addWidget(self.directory_label)
        self.layout.addWidget(self.directory_display)
        self.layout.addWidget(self.search_button)
        self.layout.addWidget(self.delete_button)
        self.layout.addLayout(self.button_layout)  # Add button layout to main layout
        self.layout.addWidget(self.modules_list)
        self.setLayout(self.layout)
        self.modules_list.setAlternatingRowColors(True)

    def select_directory(self):
        self.directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.directory_display.setText(self.directory)  # Display the selected directory

    def search(self):
        self.modules_list.clear()
        progress = QProgressDialog("Searching...", "Cancel", 0, 100, self)  # New progress dialog
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setValue(0)
        progress.show()
        for i, (root, dirs, files) in enumerate(os.walk(self.directory)):
            progress.setValue((i % 100))  # Update progress dialog
            QApplication.processEvents()
            if progress.wasCanceled():
                break
            if 'node_modules' in dirs:
                item = QListWidgetItem(root + '/node_modules')
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)  # Add checkbox
                item.setCheckState(Qt.CheckState.Unchecked)  # Initially unchecked

                self.modules_list.addItem(item)

                # Prevent os.walk from going into 'node_modules' directories.
                dirs.remove('node_modules')
        progress.setValue(100)  # End progress dialog

    def delete(self):
        total_size = 0  # Initialize total size
        progress = QProgressDialog("Deleting...", "Cancel", 0, self.modules_list.count(), self)  # New progress dialog
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setValue(0)
        progress.show()
        for i in range(self.modules_list.count() - 1, -1, -1):  # Iterate in reverse order
            QApplication.processEvents()
            if progress.wasCanceled():
                break
            item = self.modules_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                if os.access(item.text(), os.W_OK):  # Check if we have write access to the directory
                    total_size += get_size(item.text())  # Add size of directory to total size
                    shutil.rmtree(item.text(), ignore_errors=True)
                    progress.setValue(self.modules_list.count() - i)  # Update progress dialog
                    self.modules_list.takeItem(i)
                else:  # If we don't have write access, show an error message
                    QMessageBox.critical(self, "Error", f"Don't have permission to delete {item.text()}")
        progress.reset()  # Reset the progress dialog
        QMessageBox.information(self, "Success", f"You successfully cleaned {total_size / (1024 * 1024):.2f}MB.")  # Show cleaned size

    def select_all(self):  # New slot
        for i in range(self.modules_list.count()):
            item = self.modules_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)

    def unselect_all(self):  # New slot
        for i in range(self.modules_list.count()):
            item = self.modules_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)


# Create the application
app = QApplication([])
ex = App()
ex.show()
app.exec()
