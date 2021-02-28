import sqlite3
import datetime
import os
import pandas as pd


class Pomodoro:
    """
    This class controls the functions to create, start, 
    and end pomodoros.
    An entire pomodoro is the length of the pomodoro plus
    the length of the rest time.
    """

    database_path = "data\\pomodoros.db"
    #database_path = 'pomodoro_prueba.db'

    QUERY = """
    SELECT 
    Categories.category as category, 
    Projects.name as project, 
    Projects.start as project_start,
    Projects.end as project_end,
    Projects.canceled as project_cancel,
    Pomodoros.time as pomodoro_length,
    Pomodoros.date as pomodoro_date,
    Pomodoros.hour as pomodoro_hour,
    Pomodoros.satisfaction as pomodoro_calification
    FROM Pomodoros
    INNER JOIN Projects
    ON Pomodoros.project_id = Projects.id
    INNER JOIN Categories
    ON Pomodoros.category_id = Categories.id;
    """

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
            categories: list of tuples. (category, id)
        """
        self.cursor.execute("SELECT category, id FROM Categories")
        categories = self.cursor.fetchall()

        return categories

    def get_projects(self, category_id):
        """
        Gets the projects that have not been canceled or ended
        
        Args:
            category_id: int
        Returns:
            projects: list of tuples (project_name, id)
        """
        self.cursor.execute(
            "SELECT name, id FROM Projects WHERE category_id= ? and end IS NULL and canceled = 'No'",
            (category_id, ),
        )
        projects = self.cursor.fetchall()

        return projects

    def create_category(self, category_name):
        """
        This function inserts a category in the database
        """
        self.cursor.execute("INSERT INTO Categories (category) VALUES (?)",
                            (category_name, ))
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

    def add_pomodoro(self,
                     category_id,
                     project_id,
                     hour,
                     satisfaction=0,
                     duration=25):
        """
        This function adds the pomodoro data into the database
        
        Args:           
            category_id: Pomodoro's category
            project_id: Pomodoro's project
            hour: int. Pomodoro's start hour
            satisfaction: 1 if the pomodoro was good, 2 if you 
                did not feel well while doing it.
            duration: Pomodoro duration, normally 25 min
        """
        date = self.get_date()
        self.cursor.execute(
            "INSERT INTO Pomodoros (time, date, hour, category_id, project_id, satisfaction) VALUES (?, ?, ?, ?, ?,?)",
            (
                duration,
                date,
                hour,
                category_id,
                project_id,
                satisfaction,
            ),
        )
        self.conn.commit()

    def end_project(self, project_id):
        """
        Adds the project's end date.
        We end a project when our final objective
        is accomplished.
        
        Args:
            project_id: list
        """

        date = self.get_date()
        self.cursor.execute("UPDATE Projects SET end= ? WHERE id= ?",
                            (date, project_id))
        self.conn.commit()

    def cancel_project(self, project_id):
        """
        Adds the project's cancel date. We 
        cancel a project before its ending.
            
        Args:
            project_id: int
        """
        date = self.get_date()
        self.cursor.execute("UPDATE Projects SET canceled=? WHERE id=?",
                            (date, project_id))
        self.conn.commit()

    def create_df(self, query):
        """
        Executes a query to the pomodoro dataset, then
        creates and formats the information into a 
        workable pandas dataframe
        """
        date_format = '%Y-%m-%d'
        date_columns = {
            'project_start': date_format,
            'project_end': date_format,
            'project_cancel': date_format
        }
        califications = {1: "Good", 2: "Bad"}
        df = pd.read_sql_query(query, self.conn, parse_dates=date_columns)

        # Join the pomodoro_date and pomodoro_hour
        df['pomodoro_date'] = df.pomodoro_date + " " + df.pomodoro_hour
        df["pomodoro_date"] = pd.to_datetime(df.pomodoro_date,
                                             format="%Y-%m-%d %H:%M:%S")
        df.drop('pomodoro_hour', axis=1, inplace=True)

        # Replace the values in the calification to better understanding
        df.replace({"pomodoro_calification": califications}, inplace=True)

        # pomodoro_date as index is easier to filter when creating the dashboard
        df.set_index('pomodoro_date', inplace=True, drop=False)

        return df

    def get_all_projects(self):
        """
        Gets all the project names no matter their state.
        """
        self.cursor.execute("SELECT name FROM Projects")
        projects = self.cursor.fetchall()
        projects = [project[0] for project in projects]

        return projects

    def create_database(self):
        if not os.path.exists(self.database_path):
            # Make some fresh tables using executescript()
            print("Creating pomodoros database ...")
            conn = sqlite3.connect(self.database_path)
            cur = conn.cursor()
            cur.executescript("""
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
            """)
            conn.commit()


class Recall:
    """
    This class handles the different queries
    that we can make to the Recalls database
    """
    database_path = "data\\recalls.db"

    #database_path = 'recalls_prueba.db'

    def __init__(self):
        # create database if need
        self.create_database()
        self.conn, self.cursor = self.get_conn_cursor()

    def get_conn_cursor(self):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        return conn, cursor

    def get_projects(self):
        """
        Retrieves the unique project names from the
        recalls database
        
        returns:
            projects: list of tuples. (project_name, )
        """
        self.cursor.execute("SELECT DISTINCT project_name FROM Recalls")
        projects = self.cursor.fetchall()

        return projects

    def create_recall(self, project_name, title, recall):
        """
        Inserts a recall 
        Args:
            project_name: str
            title: str
            recall: str
        """

        query = (
            "INSERT INTO Recalls (recall, title, project_name) VALUES (?, ?, ?)"
        )
        self.cursor.execute(query, (recall, title, project_name))

        self.conn.commit()

    def get_recalls(self, project_name):
        """
        Gets the recalls from an specific project
        
        Args:
            project_name: str.
        returns:
            recalls: list of tuples. (title, recall)
        """
        query = ("SELECT title, recall FROM Recalls WHERE project_name = ?")
        self.cursor.execute(query, (project_name, ))

        recalls = self.cursor.fetchall()

        return recalls

    def search_in_recalls(self, text):
        """
        Search for the text inside all the recalls
        
        Args:
            text: str. The string that we are going to search for
        returns:
            results: list of tuples. (project_name, title, recall)
        """
        query = (
            f'SELECT project_name, title, recall FROM Recalls WHERE recall LIKE ?'
        )
        self.cursor.execute(query, (f'%{text}%', ))

        results = self.cursor.fetchall()

        return results

    def create_database(self):
        # Create database if it does not exist
        if not os.path.exists(self.database_path):
            print("Creating recalls database ...")
            conn = sqlite3.connect(self.database_path)
            cur = conn.cursor()
            cur.executescript("""
                CREATE TABLE IF NOT EXISTS Recalls(
                    recall TEXT NOT NULL,
                    title TEXT NOT NULL,
                    project_name TEXT NOT NULL
                );
                """)
            conn.commit()


if __name__ == "__main__":
    pom_queries = Pomodoro()

    projects = pom_queries.get_all_projects()
    for pro in projects:
        print(pro)