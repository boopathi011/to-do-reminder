from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.metrics import dp
from kivy.lang import Builder
import json
import os
from datetime import datetime, timedelta
from kivy.clock import Clock

# Embed the KV code directly
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
Builder.load_string(kv)

class TaskItem(BoxLayout):
    task_text = StringProperty("")
    reminder = StringProperty("")
    selected = BooleanProperty(False)
    done_selected = BooleanProperty(False)
    not_yet_selected = BooleanProperty(False)
    
    def on_checkbox_active(self, checkbox, value):
        self.selected = value

    def on_done_checkbox_active(self, checkbox, value):
        if value:
            self.parent.parent.disable_other_checkboxes(self, 'done')
        self.done_selected = value

    def on_not_yet_checkbox_active(self, checkbox, value):
        if value:
            self.parent.parent.disable_other_checkboxes(self, 'not_yet')
        self.not_yet_selected = value

class TaskList(RecycleView):
    def __init__(self, **kwargs):
        super(TaskList, self).__init__(**kwargs)
        self.data = []
        self.selected_item = None

    def disable_other_checkboxes(self, selected_item, selected_type):
        # Deselect previously selected checkbox in the same task item
        if self.selected_item and self.selected_item != selected_item:
            if self.selected_item.done_selected:
                self.selected_item.done_selected = False
            elif self.selected_item.not_yet_selected:
                self.selected_item.not_yet_selected = False

        # Update the reference to the newly selected item
        self.selected_item = selected_item

        # Update the checkboxes of the selected item
        if selected_type == 'done':
            selected_item.done_selected = True
            selected_item.not_yet_selected = False
        elif selected_type == 'not_yet':
            selected_item.not_yet_selected = True
            selected_item.done_selected = False

class ToDoApp(App):
    def build(self):
        self.tasks = {}
        self.reminder_interval = 60  # Interval to check reminders in seconds
        
        self.main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.input_field = TextInput(hint_text="Enter a task", size_hint=(1, 0.1))
        self.main_layout.add_widget(self.input_field)

        self.reminder_field = TextInput(hint_text="Enter reminder time (e.g., 14:30)", size_hint=(1, 0.1))
        self.main_layout.add_widget(self.reminder_field)

        self.button_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        self.add_button = Button(text="Add Task")
        self.edit_button = Button(text="Edit Task")
        self.update_button = Button(text="Update Task")
        self.remove_button = Button(text="Remove Task")
        self.button_layout.add_widget(self.add_button)
        self.button_layout.add_widget(self.edit_button)
        self.button_layout.add_widget(self.update_button)
        self.button_layout.add_widget(self.remove_button)
        self.main_layout.add_widget(self.button_layout)

        self.task_list = TaskList(size_hint=(1, 0.8))
        self.main_layout.add_widget(self.task_list)

        self.add_button.bind(on_press=self.add_task)
        self.edit_button.bind(on_press=self.edit_task)
        self.update_button.bind(on_press=self.update_task)
        self.remove_button.bind(on_press=self.remove_task)

        self.load_tasks()

        # Schedule the reminder check function to run periodically
        Clock.schedule_interval(self.check_reminders, self.reminder_interval)

        return self.main_layout

    def add_task(self, instance):
        task_text = self.input_field.text.strip()
        reminder_time = self.reminder_field.text.strip()
        if task_text:
            if task_text not in self.tasks:
                self.tasks[task_text] = {"task_text": task_text, "reminder_time": reminder_time}
                self.task_list.data.append({"task_text": str(task_text), "reminder": str(reminder_time)})  # Ensure task_text and reminder are strings
                self.input_field.text = ""
                self.reminder_field.text = ""
                self.save_tasks()
            else:
                print(f"Task '{task_text}' already exists.")

    def edit_task(self, instance):
        selected_items = [item for item in self.task_list.children[0].children if isinstance(item, TaskItem) and item.selected]
        if selected_items:
            selected_item = selected_items[0]
            self.input_field.text = selected_item.task_text
            self.reminder_field.text = selected_item.reminder

    def update_task(self, instance):
        selected_items = [item for item in self.task_list.children[0].children if isinstance(item, TaskItem) and item.selected]
        if selected_items:
            task_text = self.input_field.text.strip()
            reminder_time = self.reminder_field.text.strip()
            if task_text:
                current_task = selected_items[0].task_text
                index = next((i for i, item in enumerate(self.task_list.data) if item['task_text'] == current_task), None)
                if index is not None:
                    self.task_list.data[index]['task_text'] = str(task_text)  # Ensure task_text is a string
                    self.task_list.data[index]['reminder'] = str(reminder_time)  # Ensure reminder is a string
                    self.task_list.refresh_from_data()
                    self.input_field.text = ""
                    self.reminder_field.text = ""
                    self.save_tasks()

    def remove_task(self, instance):
        selected_items = [item for item in self.task_list.children[0].children if isinstance(item, TaskItem) and item.selected]
        if selected_items:
            task_text = selected_items[0].task_text
            self.tasks.pop(task_text, None)
            self.task_list.data = [task for task in self.task_list.data if task['task_text'] != task_text]
            self.task_list.refresh_from_data()
            self.save_tasks()

    def save_tasks(self):
        with open('tasks.json', 'w') as file:
            json.dump(self.tasks, file)

    def load_tasks(self):
        if os.path.exists('tasks.json'):
            with open('tasks.json', 'r') as file:
                self.tasks = json.load(file)
                print(f"Loaded tasks: {self.tasks}")  # Debugging line
                if isinstance(self.tasks, dict):
                    # Ensure each task is a dictionary
                    self.task_list.data = [
                        {"task_text": task["task_text"], "reminder": task.get("reminder_time", "")}
                        for task in self.tasks.values() if isinstance(task, dict) and "task_text" in task
                    ]
                    self.task_list.refresh_from_data()
                else:
                    print("Error: Loaded tasks is not a dictionary.")
        else:
            print("No existing tasks found.")

    def check_reminders(self, dt):
        now = datetime.now()
        for task in self.tasks.values():
            reminder_time_str = task.get("reminder_time")
            if reminder_time_str:
                try:
                    reminder_time = datetime.strptime(reminder_time_str, "%H:%M").time()
                    if now.time() >= reminder_time:
                        print(f"Reminder: {task['task_text']} is due!")
                        # Remove the reminder after it triggers
                        task["reminder_time"] = ""
                        self.save_tasks()
                except ValueError:
                    print(f"Invalid reminder time format for task '{task['task_text']}'.")

if __name__ == "__main__":
    ToDoApp().run()
