import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QHBoxLayout, QLabel, QCheckBox, QMessageBox, QButtonGroup, QMainWindow, QTimeEdit, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer, QTime, pyqtSignal
import pygame

class TaskItem(QWidget):
    reminder_off = pyqtSignal(str)  # Signal to indicate reminder should be turned off

    def __init__(self, text):
        super().__init__()
        self.checkbox_done = QCheckBox("✅")
        self.checkbox_wrong = QCheckBox("❌")
        self.label = QLabel(text)
        
        # Create a button group to ensure only one checkbox is selected at a time
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.checkbox_done)
        self.button_group.addButton(self.checkbox_wrong)
        
        # Connect the button group's signal to handle checkbox changes
        self.button_group.buttonClicked.connect(self.on_checkbox_clicked)
        
        # Layout for the task item
        layout = QHBoxLayout()
        layout.addWidget(self.checkbox_done)
        layout.addWidget(self.checkbox_wrong)
        layout.addWidget(self.label)
        layout.setSpacing(10)  # Increased spacing for better touch interaction
        layout.setContentsMargins(10, 5, 10, 5)  # Set margins for padding
        
        self.setLayout(layout)
        
    def setText(self, text):
        self.label.setText(text)
        
    def text(self):
        return self.label.text()
    
    def on_checkbox_clicked(self, button):
        # Ensure only the clicked checkbox is selected, the other gets deselected
        if button == self.checkbox_done:
            self.checkbox_wrong.setChecked(False)
            self.reminder_off.emit(self.text())  # Emit signal to turn off reminder
        else:
            self.checkbox_done.setChecked(False)

class ToDoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List App")
        self.setGeometry(100, 100, 400, 600)  # Adjusted height for more space on mobile
        
        # Initialize Pygame mixer for sound playback
        pygame.mixer.init()
        
        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        # Layouts and widgets
        self.input_field = QLineEdit()
        self.add_button = QPushButton("Add Task")
        self.edit_button = QPushButton("Edit Task")
        self.update_button = QPushButton("Update Task")
        self.remove_button = QPushButton("Remove Task")
        self.task_list = QListWidget()
        
        # Reminder widgets
        self.reminder_time = QTimeEdit()
        self.reminder_button = QPushButton("Set Reminder")
        self.ringtone_button = QPushButton("Choose Ringtone")
        self.ringtone_path = None
        
        # Adding widgets to the layout
        self.layout.addWidget(self.input_field)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.edit_button)
        self.layout.addWidget(self.update_button)
        self.layout.addWidget(self.remove_button)
        self.layout.addWidget(self.task_list)
        self.layout.addWidget(QLabel("Reminder Time:"))
        self.layout.addWidget(self.reminder_time)
        self.layout.addWidget(self.reminder_button)
        self.layout.addWidget(self.ringtone_button)
        
        # Toggle button for theme switching
        self.theme_toggle_button = QPushButton("Switch to Dark Theme")
        self.layout.addWidget(self.theme_toggle_button)
        self.theme_toggle_button.clicked.connect(self.toggle_theme)
        
        # Dictionary to keep track of tasks
        self.task_widgets = {}
        self.current_edit_task = None
        
        # Connecting button clicks to their respective methods
        self.add_button.clicked.connect(self.add_task)
        self.edit_button.clicked.connect(self.start_edit_task)
        self.update_button.clicked.connect(self.update_task)
        self.remove_button.clicked.connect(self.remove_task)
        self.reminder_button.clicked.connect(self.set_reminder)
        self.ringtone_button.clicked.connect(self.choose_ringtone)
        
        # Initially disable the update button
        self.update_button.setEnabled(False)

        # Default theme
        self.current_theme = 'light'
        self.set_theme(self.current_theme)

        # Timer setup for reminders
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_reminders)
        self.timer.start(60000)  # Check every minute
        
        # Load tasks from file
        self.load_tasks()

    def add_task(self):
        task = self.input_field.text().strip()
        if task:
            # Check if task already exists
            if task in self.task_widgets:
                QMessageBox.warning(self, "Duplicate Task", "This task is already in the list!")
            else:
                item = QListWidgetItem(self.task_list)
                task_item = TaskItem(task)
                task_item.reminder_off.connect(self.turn_off_reminder)  # Connect the signal to handle reminder turn-off
                item.setSizeHint(task_item.sizeHint())
                self.task_list.setItemWidget(item, task_item)
                self.task_widgets[task] = (item, None)  # No reminder initially
                self.input_field.clear()
                self.current_edit_task = None  # Reset the task being edited
                self.update_button.setEnabled(False)  # Disable update button
                # Save tasks to file
                self.save_tasks()
        else:
            QMessageBox.warning(self, "Empty Input", "Please enter a task!")

    def start_edit_task(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a task to edit!")
            return

        # Get the first selected item (assuming single selection)
        selected_item = selected_items[0]
        task_item = self.task_list.itemWidget(selected_item)
        self.input_field.setText(task_item.text())  # Load selected item text into input field
        
        # Set the current task to be edited
        self.current_edit_task = task_item.text()
        self.task_list.takeItem(self.task_list.row(selected_item))
        
        # Enable the update button and disable the add button
        self.update_button.setEnabled(True)
        self.add_button.setEnabled(False)

    def update_task(self):
        new_task = self.input_field.text().strip()
        if new_task:
            # Check if the new task already exists
            if new_task in self.task_widgets and new_task != self.current_edit_task:
                QMessageBox.warning(self, "Duplicate Task", "This task is already in the list!")
            else:
                # Remove the old item from task_widgets and list
                if self.current_edit_task in self.task_widgets:
                    old_item = self.task_widgets.pop(self.current_edit_task)
                    self.task_list.takeItem(self.task_list.row(old_item[0]))
                    
                    # Create and add new task item
                    new_item = QListWidgetItem(self.task_list)
                    task_item = TaskItem(new_task)
                    task_item.reminder_off.connect(self.turn_off_reminder)  # Connect the signal to handle reminder turn-off
                    new_item.setSizeHint(task_item.sizeHint())
                    self.task_list.setItemWidget(new_item, task_item)
                    
                    # Add the new task to the dictionary
                    self.task_widgets[new_task] = (new_item, None)  # No reminder initially
                    self.input_field.clear()
                    self.current_edit_task = None  # Reset task being edited
                    self.update_button.setEnabled(False)  # Disable update button
                    self.add_button.setEnabled(True)  # Re-enable add button
                    # Save tasks to file
                    self.save_tasks()
                else:
                    QMessageBox.warning(self, "Edit Error", "Error updating the task!")
        else:
            QMessageBox.warning(self, "Empty Input", "Please enter a new task!")

    def remove_task(self):
        # Get selected items
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a task to remove!")
            return
        
        # Remove selected items
        for item in selected_items:
            task_text = self.task_list.itemWidget(item).text()
            if task_text in self.task_widgets:
                self.task_widgets.pop(task_text)
            self.task_list.takeItem(self.task_list.row(item))
        self.update_button.setEnabled(False)  # Disable update button after removal
        self.add_button.setEnabled(True)  # Re-enable add button
        # Save tasks to file
        self.save_tasks()

    def set_reminder(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a task to set a reminder!")
            return

        reminder_time = self.reminder_time.time().toString("HH:mm")  # Use same format for consistency
        task_item = self.task_list.itemWidget(selected_items[0])
        task_text = task_item.text()
        # Save the reminder time with the task
        if task_text in self.task_widgets:
            self.task_widgets[task_text] = (self.task_widgets[task_text][0], reminder_time)
            self.save_tasks()
            QMessageBox.information(self, "Reminder Set", f"Reminder for '{task_text}' set at {reminder_time}.")
        else:
            QMessageBox.warning(self, "Set Reminder Error", "Task not found!")

    def choose_ringtone(self):
        options = QFileDialog.Options()
        ringtone_file, _ = QFileDialog.getOpenFileName(self, "Choose Ringtone", "", "Audio Files (*.wav *.mp3);;All Files (*)", options=options)
        if ringtone_file:
            self.ringtone_path = ringtone_file
            QMessageBox.information(self, "Ringtone Selected", f"Ringtone set to: {self.ringtone_path}")

    def turn_off_reminder(self, task_text):
        """ Turn off the reminder for the given task """
        if task_text in self.task_widgets:
            self.task_widgets[task_text] = (self.task_widgets[task_text][0], None)
            self.save_tasks()

    def check_reminders(self):
        current_time = QTime.currentTime().toString("HH:mm")  # Use same format as used in `set_reminder`
        for task_text, (item, reminder_time) in self.task_widgets.items():
            if reminder_time == current_time:
                self.play_ringtone()
                QMessageBox.information(self, "Reminder", f"Reminder for task: '{task_text}' is due now!")

    def play_ringtone(self):
        """ Play the selected ringtone """
        if self.ringtone_path:
            try:
                pygame.mixer.music.load(self.ringtone_path)
                pygame.mixer.music.play()
            except Exception as e:
                QMessageBox.warning(self, "Playback Error", f"Failed to play the ringtone: {e}")
        else:
            QMessageBox.warning(self, "No Ringtone", "No ringtone is set.")

    def toggle_theme(self):
        # Toggle between light and dark themes
        if self.current_theme == 'light':
            self.set_theme('dark')
        else:
            self.set_theme('light')

    def set_theme(self, theme):
        if theme == 'dark':
            self.setStyleSheet("""
                QWidget {
                    background-color: #2E2E2E;
                    color: #E0E0E0;
                    font-family: Arial, sans-serif;
                }
                QLineEdit, QPushButton, QListWidget, QTimeEdit {
                    background-color: #3E3E3E;
                    color: #E0E0E0;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton {
                    font-size: 16px;
                }
                QListWidget {
                    border: 1px solid #555555;
                }
                QCheckBox {
                    color: #E0E0E0;
                }
                QLabel {
                    font-size: 18px;
                }
            """)
            self.theme_toggle_button.setText("Switch to Light Theme")
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #F0F0F0;
                    color: #000000;
                    font-family: Arial, sans-serif;
                }
                QLineEdit, QPushButton, QListWidget, QTimeEdit {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton {
                    font-size: 16px;
                }
                QListWidget {
                    border: 1px solid #CCCCCC;
                }
                QCheckBox {
                    color: #000000;
                }
                QLabel {
                    font-size: 18px;
                }
            """)
            self.theme_toggle_button.setText("Switch to Dark Theme")
        self.current_theme = theme

    def save_tasks(self):
        try:
            tasks_to_save = {}
            for task_text, (item, reminder_time) in self.task_widgets.items():
                tasks_to_save[task_text] = reminder_time
            with open('tasks.json', 'w') as file:
                json.dump(tasks_to_save, file, indent=4)
        except Exception as e:
            print(f"Failed to save tasks: {e}")

    def load_tasks(self):
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as file:
                saved_tasks = json.load(file)
                self.task_widgets = {}
                
                # Add tasks to the list widget
                for task_text, reminder_time in saved_tasks.items():
                    list_item = QListWidgetItem(self.task_list)
                    task_item = TaskItem(task_text)
                    task_item.reminder_off.connect(self.turn_off_reminder)  # Connect signal for reminder turn-off
                    list_item.setSizeHint(task_item.sizeHint())
                    self.task_list.setItemWidget(list_item, task_item)
                    
                    # Store reminder time in the task_widgets dictionary
                    self.task_widgets[task_text] = (list_item, reminder_time)
        else:
            self.task_widgets = {}  # Initialize an empty task list

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ToDoApp()
    window.show()
    sys.exit(app.exec_())
