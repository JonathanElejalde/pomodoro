import time
import sqlite3
import os

from PyQt5 import QtCore, QtGui, QtWidgets


class Recalls(object):

    database_path = "data\\recalls.db"

    def setupUi(self, recall_form):
        # Track the recals
        self.recall_count = 0
        self._create_database()
        self.conn, self.cursor = self._get_conn_cursor()

        recall_form.setObjectName("recall_form")
        recall_form.resize(268, 380)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(recall_form)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_3 = QtWidgets.QLabel(recall_form)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_4.addWidget(self.label_3)
        self.proj_line_edit = QtWidgets.QLineEdit(recall_form)
        self.proj_line_edit.setObjectName("proj_line_edit")
        self.verticalLayout_4.addWidget(self.proj_line_edit)
        self.verticalLayout_3.addLayout(self.verticalLayout_4)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(recall_form)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.recall_title = QtWidgets.QLineEdit(recall_form)
        self.recall_title.setObjectName("recall_title")
        self.verticalLayout.addWidget(self.recall_title)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(recall_form)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.recall_text = QtWidgets.QTextEdit(recall_form)
        self.recall_text.setObjectName("recall_text")
        self.verticalLayout_2.addWidget(self.recall_text)
        self.save_recall = QtWidgets.QPushButton(recall_form)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.save_recall.setFont(font)
        self.save_recall.setObjectName("save_recall")
        self.verticalLayout_2.addWidget(self.save_recall)
        self.recall_saved_label = QtWidgets.QLabel(recall_form)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.recall_saved_label.setFont(font)
        self.recall_saved_label.setText("")
        self.recall_saved_label.setAlignment(QtCore.Qt.AlignCenter)
        self.recall_saved_label.setObjectName("recall_saved_label")
        self.verticalLayout_2.addWidget(self.recall_saved_label)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        # Buttons
        self.save_recall.clicked.connect(self.add_recall)

        self.retranslateUi(recall_form)
        QtCore.QMetaObject.connectSlotsByName(recall_form)

    def add_recall(self):
        # Add one to the recall count
        self.recall_count += 1

        # Get project, title and recall
        project_name = self.proj_line_edit.text()
        title = self.recall_title.text()
        text = self.recall_text.toPlainText()

        self._create_recall(project_name, title, text)
        self.conn.commit()

        # Clean title and recall
        self.recall_title.setText("")
        self.recall_text.clear()

        # Confirm recall saved
        self.recall_saved_label.setText(f"The recall {self.recall_count} was saved")

    def _create_recall(self, project_name, title, recall):
        recall_query = (
            f"INSERT INTO Recalls (recall, title, project_name) VALUES (?, ?, ?)"
        )
        self.cursor.execute(recall_query, (recall, title, project_name))

    def _get_conn_cursor(self):

        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        return conn, cursor

    def _create_database(self):

        # Create database if it does not exist
        if not os.path.exists(self.database_path):
            print("Creating recalls database ...")
            conn = sqlite3.connect(self.database_path)
            cur = conn.cursor()
            cur.executescript(
                """
                CREATE TABLE IF NOT EXISTS Recalls(
                    recall TEXT NOT NULL,
                    title TEXT NOT NULL,
                    project_name TEXT NOT NULL,
                    FOREIGN KEY (project_name) REFERENCES Project (project_name)
                );
                """
            )
            conn.commit()

    def retranslateUi(self, recall_form):
        _translate = QtCore.QCoreApplication.translate
        recall_form.setWindowTitle(_translate("recall_form", "Recall"))
        self.label_3.setText(_translate("recall_form", "Project:"))
        self.label.setText(_translate("recall_form", "Recall title: "))
        self.label_2.setText(_translate("recall_form", "Recall:"))
        self.save_recall.setText(_translate("recall_form", "Save recall"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    recall_form = QtWidgets.QWidget()
    ui = Recalls()
    ui.setupUi(recall_form)
    recall_form.show()
    sys.exit(app.exec_())
