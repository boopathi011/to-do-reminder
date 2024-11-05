# 📋 ToDoApp

This is a simple ToDo application built using Kivy, a Python framework for developing multitouch applications. The application allows you to add, edit, update, and remove tasks, as well as set reminders for each task.

## ✨ Features

- ➕ Add new tasks with optional reminder times.
- ✏️ Edit existing tasks.
- 🔄 Update tasks with new information.
- 🗑️ Remove tasks from the list.
- ⏰ Reminder functionality that checks for due tasks periodically.

## 🚀 Getting Started

### 📋 Prerequisites

Make sure you have Python installed on your machine. You will also need to install the Kivy framework. You can install Kivy using pip:

```sh
pip install kivy
```

### ▶️ Running the Application

Save the provided code in a file named `main.py`. To run the application, execute the following command in your terminal:

```sh
python main.py
```

## 🏗️ Application Structure

### 📝 KV Language

The layout of the application is defined using the KV language, which is embedded directly within the Python code. The relevant part of the KV code is:

```python
kv = '''
<TaskItem>:
    orientation: 'horizontal'
    CheckBox:
        size_hint_x: 0.1
        active: root.selected
        on_active: root.on_checkbox_active(self, self.active)
    Label:
        size_hint_x: 0.4
        text: root.task_text
    Label:
        size_hint_x: 0.2
        text: root.reminder
    Label:
        text: 'DONE'
        size_hint_x: 0.05
    CheckBox:
        id: done_checkbox
        size_hint_x: 0.1
        active: root.done_selected
        on_active: root.on_done_checkbox_active(self, self.active)
    Label:
        text: 'NOT YET'
        size_hint_x: 0.05
    CheckBox:
        id: not_yet_checkbox
        size_hint_x: 0.1
        active: root.not_yet_selected
        on_active: root.on_not_yet_checkbox_active(self, self.active)

<TaskList>:
    viewclass: 'TaskItem'
    RecycleBoxLayout:
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
'''
```

### 🐍 Python Code

The Python code defines the main logic of the application, including the `TaskItem`, `TaskList`, and `ToDoApp` classes.

#### 📄 TaskItem

This class represents an individual task item in the list. It has properties for the task text, reminder time, and the states of various checkboxes (selected, done, and not yet).

#### 📜 TaskList

This class is a custom RecycleView that holds and manages the list of tasks. It provides methods to disable other checkboxes when one is selected and to update the task list.

#### 🏠 ToDoApp

This is the main application class. It defines the user interface and provides methods for adding, editing, updating, and removing tasks. It also includes functionality for saving and loading tasks to/from a JSON file and checking reminders periodically.

## 💾 Saving and Loading Tasks

Tasks are saved to a file named `tasks.json` in the same directory as the application. When the application starts, it attempts to load tasks from this file. If the file does not exist, a new one will be created when tasks are added.

## ⏲️ Reminder Functionality

The application periodically checks for due tasks based on their reminder times. If a task's reminder time has passed, a message is printed to the console.

## 🛠️ Customizing the Application

Feel free to customize the application according to your needs. You can modify the layout, add new features, or integrate with other services.

## 📄 License

This application was built using the Kivy framework. For more information about Kivy, visit the [official Kivy website](https://kivy.org/).

---

I hope this README file helps you understand and use the ToDoApp effectively. If you have any questions or need further assistance, feel free to ask!
