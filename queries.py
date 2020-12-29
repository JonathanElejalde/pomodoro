import sqlite3
import datetime
import os
import time


class Pomodoro:
    """
    This class controls the functions to create, start, 
    and end pomodoros.
    An entire pomodoro is the length of the pomodoro plus
    the length of the rest time.
    """

    database_path = "data\pomodoros.db"

    def __init__(self):
        # create database if need
        self.create_database()
        self.conn, self.cursor = self.get_conn_cursor()

    def get_date(self):
        date = datetime.date.today()
        return date

    def get_date_hour(self):
        date_hour = datetime.datetime.now()
        date_hour = date_hour.strftime("%H:%M:%S")

        return date_hour

    def get_conn_cursor(self):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        return conn, cursor

    def get_categories(self):
        """
        Gets the current categories in the database.
    
        Returns:
            categories: list of tuples (id, category)
        """
        self.cursor.execute("SELECT id, category FROM Categories")
        categories = self.cursor.fetchall()

        return categories

    def get_projects(self, category_id):
        """
        Gets the projects that have not been canceled or ended
        
        Args:
            category_id: int
        Returns:
            projects: list of tuples (id, project name)
        """
        self.cursor.execute(
            "SELECT id, name FROM Projects WHERE category_id= ? and end IS NULL and canceled = 'No'",
            (category_id,),
        )
        projects = self.cursor.fetchall()

        return projects

    def create_category(self, category_name):
        """
        This function inserts a category in the database
        """
        self.cursor.execute(
            "INSERT INTO Categories (category) VALUES (?)", (category_name,)
        )
        self.conn.commit()

    def create_project(self, project_name, category_id):
        """
        This function inserts a project in the database
        """
        date = self.get_date()
        self.cursor.execute(
            "INSERT INTO Projects (name, start, category_id) VALUES (?, ?, ?)",
            (project_name, date, category_id),
        )
        self.conn.commit()

    def add_pomodoro(self, category_id, project_id, satisfaction, duration=25):
        """
        This function adds the pomodoro data into the database
        
        Args:           
            category_id: Pomodoro's category
            project_id: Pomodoro's project
            satisfaction: 1 if the pomodoro was good, 2 if you 
                did not feel well while doing it.
            duration: Pomodoro duration, normally 25 min
        """
        date = self.get_date()
        hour = self.get_date_hour()
        self.cursor.execute(
            "INSERT INTO Pomodoros (time, date, hour, category_id, project_id, satisfaction) VALUES (?, ?, ?, ?, ?,?)",
            (duration, date, hour, category_id, project_id, satisfaction,),
        )
        self.conn.commit()

    def end_project(self, project_id):
        """
        Adds the project's end date
        
        Args:
            project_id: list
        """

        date = self.get_date()
        self.cursor.execute(
            "UPDATE Projects SET end= ? WHERE id= ?", (date, project_id)
        )
        self.conn.commit()

    def cancel_project(self, project_id):
        """
        Adds the project's cancel date    
        Args:
            project_id: int
        """
        date = self.get_date()
        self.cursor.execute(
            "UPDATE Projects SET canceled=? WHERE id=?", (date, project_id)
        )
        self.conn.commit()

    def create_database(self):
        if not os.path.exists(self.database_path):
            # Make some fresh tables using executescript()
            print("Creating pomodoros database ...")
            conn = sqlite3.connect(self.database_path)
            cur = conn.cursor()
            cursor.executescript(
                """
            CREATE TABLE IF NOT EXISTS Pomodoros (
                id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                time INTEGER NOT NULL,
                date TEXT,
                hour TEXT,
                category_id INTEGER,
                project_id INTEGER,
                satisfaction INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Projects (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                name TEXT,
                start TEXT,
                end TEXT,
                category_id,
                canceled TEXT DEFAULT "No"        
            );

            CREATE TABLE IF NOT EXISTS Categories (
                id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                category TEXT
            );
            """
            )
            conn.commit()


if __name__ == "__main__":
    pass
