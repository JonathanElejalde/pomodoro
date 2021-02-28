# Open the designer from console: pyqt5-tools designer
# Pass the designer to python code: pyuic5 template.ui -o template.py -x

import sys
import winsound
import time

from functools import partial
from queries import Pomodoro
from PomodoroUI import PomodoroUI
from RecallsUI import Recalls

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QMessageBox,
)
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Todo's
# Pointing to the same database
# Add docstring
# try to improve the code


class MainPomodoro:
    def __init__(self):
        # Interface
        self.main_window = QMainWindow()
        self.pomodoro_ui = PomodoroUI()
        self.pomodoro_ui.setupUi(self.main_window)
        self.recall_window = QtWidgets.QWidget()
        self.recall_ui = Recalls()
        self.recall_ui.setupUi(self.recall_window)

        # Query manager
        self.pomodoro_manager = Pomodoro()
        # Track variables for queries and confirmation purposes
        self.category_id = None
        self.project_id = None
        self.project_name = None
        self.satisfaction = None

        ##### Buttons ######
        # Start the app in home
        self.pomodoro_ui.stacked_widget.setCurrentWidget(self.pomodoro_ui.home)
        self.pomodoro_ui.create_pomodoro_btn.clicked.connect(
            self.show_categories)
        self.pomodoro_ui.start_pomodoro_btn.clicked.connect(self.start_timer)

        # Add new category
        self.pomodoro_ui.add_new_cat_btn.clicked.connect(self.add_category)
        self.pomodoro_ui.add_proj_btn.clicked.connect(self.add_project)

        # End or Cancel a project
        self.pomodoro_ui.end_proj_btn.clicked.connect(
            lambda x: self.end_project(self.project_id, self.project_name))
        self.pomodoro_ui.cancel_proj_btn.clicked.connect(
            lambda x: self.cancel_project(self.project_id, self.project_name))

        # open a new dialog if clicked add recall
        self.pomodoro_ui.add_recall_btn.clicked.connect(self.start_recall)

        # Allows to go back
        self.pomodoro_ui.previous_window_btn1.clicked.connect(
            self.previous_window)
        self.pomodoro_ui.previous_window_btn2.clicked.connect(
            self.previous_window)
        self.pomodoro_ui.previous_window_btn3.clicked.connect(
            self.previous_window)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_categories(self):
        # Clear layout
        self.clear_layout(self.pomodoro_ui.cat_layout)

        # Add the categories
        font = QtGui.QFont()
        font.setPointSize(12)
        buttons = dict()

        # Get the categories
        categories = self.pomodoro_manager.get_categories()

        # Add the categories to the interface
        for id, category in categories:
            buttons[category] = QPushButton(category)
            buttons[category].setFont(font)
            self.pomodoro_ui.cat_layout.addWidget(buttons[category])
            buttons[category].clicked.connect(partial(self.show_projects, id))

        self.pomodoro_ui.stacked_widget.setCurrentWidget(
            self.pomodoro_ui.categories)

    def show_projects(self, category_id):
        # Track the category id
        self.category_id = category_id

        # Clear layout
        self.clear_layout(self.pomodoro_ui.proj_layout)

        font = QtGui.QFont()
        font.setPointSize(12)
        # Get the projects
        projects = self.pomodoro_manager.get_projects(category_id)
        buttons = dict()

        # Add the projects to the interface
        for i, project in enumerate(projects):
            project_id, project_name = project

            # add buttons
            buttons[project_name] = QPushButton(project_name)
            buttons[project_name].setFont(font)
            self.pomodoro_ui.proj_layout.addWidget(buttons[project_name])
            buttons[project_name].clicked.connect(
                partial(self.show_timer, project_id, project_name))

        self.pomodoro_ui.stacked_widget.setCurrentWidget(
            self.pomodoro_ui.projects)

    def show_timer(self, project_id, project_name):
        # Track project_id and project_name
        self.project_id = project_id
        self.project_name = project_name

        self.pomodoro_ui.current_proj.setText(project_name)
        self.pomodoro_ui.stacked_widget.setCurrentWidget(
            self.pomodoro_ui.timer)

    def start_timer(self):
        self.pomodoro_ui.pomodoro_added_label.setText("")
        self.pomodoro_timer = Timer()
        self.pomodoro_timer.change_time.connect(self.set_timer)
        self.pomodoro_timer.change_label.connect(self.set_label)
        self.pomodoro_timer.finished.connect(self.qualify_pomodoro)
        self.pomodoro_timer.start()

    def start_recall(self):
        self.recall_window.show()

    def qualify_pomodoro(self):
        message = QMessageBox.question(
            self.main_window,
            "Pomodoro's satisfaction",
            "Did you feel good in this pomodoro",
            QMessageBox.Yes | QMessageBox.No,
        )

        if message == QMessageBox.Yes:
            self.satisfaction = 1
        elif message == QMessageBox.No:
            self.satisfaction = 2

        # Save the pomodoro into the database
        self.pomodoro_manager.add_pomodoro(self.category_id, self.project_id,
                                           self.satisfaction)
        self.pomodoro_ui.pomodoro_added_label.setText("The pomodoro was added")

    def set_timer(self, time_left):
        self.pomodoro_ui.timer_label.setText(time_left)

    def set_label(self, label):
        self.pomodoro_ui.working_resting_label.setText(label)

    def add_category(self):
        category = self.pomodoro_ui.new_category_text.text()
        self.pomodoro_manager.create_category(category)

        # Refresh the category view
        self.show_categories()
        self.pomodoro_ui.new_category_text.setText("")

    def add_project(self):
        project = self.pomodoro_ui.new_project_text.text()
        self.pomodoro_manager.create_project(project, self.category_id)

        # Refresh the project view
        self.show_projects(self.category_id)
        self.pomodoro_ui.new_project_text.setText("")

    def end_project(self, project_id, project_name):
        message = QMessageBox.question(
            self.main_window,
            "End project",
            f"Do you want to end project {project_name}",
            QMessageBox.Yes | QMessageBox.No,
        )

        if message == QMessageBox.Yes:
            self.pomodoro_manager.end_project(project_id)
            self.pomodoro_manager.conn.commit()
            # Return to projects
            self.show_projects(self.category_id)

    def cancel_project(self, project_id, project_name):

        message = QMessageBox.question(
            self.main_window,
            "Cancel project",
            f"Do you want to cancel project {project_name}",
            QMessageBox.Yes | QMessageBox.No,
        )

        if message == QMessageBox.Yes:
            self.pomodoro_manager.cancel_project(project_id)
            self.pomodoro_manager.conn.commit()
            # Return to projects
            self.show_projects(self.category_id)

    def show(self):
        self.main_window.show()

    def previous_window(self):
        self.pomodoro_ui.stacked_widget.setCurrentIndex(
            (self.pomodoro_ui.stacked_widget.currentIndex() - 1) % 4)


class Timer(QThread):

    _end_sound = "countdown.wav"
    change_time = pyqtSignal(str)
    change_label = pyqtSignal(str)

    def __init__(self, working=25, resting=5):
        super().__init__()
        self.working = working
        self.resting = resting

    def run(self):
        # Start working timer
        working_length = 60 * self.working
        label = "Working"
        self.change_label.emit(label)

        while working_length > 0:
            mins, seconds = divmod(working_length, 60)

            time_left = str(mins).zfill(2) + ":" + str(seconds).zfill(2)
            QThread.sleep(1)
            working_length -= 1
            self.change_time.emit(time_left)

        winsound.PlaySound(self._end_sound, winsound.SND_FILENAME)

        # Star resting timer
        rest_length = 60 * self.resting
        label = "Resting"
        self.change_label.emit(label)
        while rest_length > 0:
            mins, seconds = divmod(rest_length, 60)

            time_left = str(mins).zfill(2) + ":" + str(seconds).zfill(2)
            QThread.sleep(1)
            rest_length -= 1
            self.change_time.emit(time_left)

        winsound.PlaySound(self._end_sound, winsound.SND_FILENAME)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainPomodoro()
    main_win.show()
    sys.exit(app.exec_())
