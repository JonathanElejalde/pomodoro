import datetime
import winsound
import time


class Pomodoro:
    """
    This class controls the functions to create, start, 
    and end pomodoros.
    An entire pomodoro is the length of the pomodoro plus
    the length of the rest time.
    """

    _end_sound = "countdown.wav"

    def __init__(self, cursor):
        self.cursor = cursor

    def _get_date(self):
        date = datetime.date.today()
        return date

    def _get_date_hour(self):
        date_hour = datetime.datetime.now()
        date_hour = date_hour.strftime("%H:%M:%S")

        return date_hour

    def timer(self, minutes=5, mode="pomodoro"):
        """
        This functions creates a timer for the pomodoro or rest
        depending on the mode.
        
        Args:
            minutes: length of the pomodoro in minutes.
        
        Returns:
            A sound that indicates the end of the timer.
        """
        if mode == "pomodoro":
            if isinstance(minutes, str):
                timer_length = int(minutes) * 60
            else:
                timer_length = minutes * 60

        elif mode == "rest":
            timer_length = minutes * 60

        print("---Timer---")
        while timer_length > 0:
            mins, seconds = divmod(timer_length, 60)

            time_left = str(mins).zfill(2) + ":" + str(seconds).zfill(2)
            print(time_left + "\r", end="")
            time.sleep(1)
            timer_length -= 1

        return winsound.PlaySound(self._end_sound, winsound.SND_FILENAME)

    def next_decision(self):
        """
        This function asks for the next decision after a pomodoro
        
        Returns:
            The number with the decision
        """
        while True:
            print("1- Create a pomodoro")
            print("2- End the project")
            print("3- Cancel the project")
            print("4- Exit the program")

            decision = input("Type your option's number: ")
            try:
                decision = int(decision)
            except:
                print("Entry a number")
                continue
            if decision in [1, 2, 3, 4]:
                return decision
            else:
                print("Your entry is not between the options")
                continue

    def show_categories(self):
        """
        This function search for the current categories in
        the database. It can also create new ones
        
        Returns:
            The new category id or an existing category
        """
        self.cursor.execute("SELECT id, category FROM Categories")
        categories = self.cursor.fetchall()
        # If there are not categories in the database
        if categories == None:
            category_id = self._create_category()
            return category_id
        else:
            for category in categories:
                print(str(category[0]) + "- " + category[1])

        category_id = input('Type the category id or type "new" to create a new one: ')
        try:
            if category_id == "new":
                category_id = self._create_category()
            else:
                category_id = int(category_id)
        except Exception as e:
            print('Try using the project id or type "new" to create a new one')
            print(e)

        return category_id

    def show_projects(self, category_id):
        """
        This function shows the projects that haven't been ended or canceled
        Returns:
            The new project id or an existing project
        """
        self.cursor.execute(
            "SELECT id, name FROM Projects WHERE category_id= ? and end IS NULL and canceled = 'No'",
            (category_id,),
        )
        projects = self.cursor.fetchall()
        # If there are not projects in the category
        if projects == None:
            project_id = self._create_project(category_id)
            return project_id

        for project in projects:
            print(str(project[0]) + "- " + project[1])

        project_id = input('Type the project id or type "new" to create a new one: ')
        try:
            if project_id == "new":
                project_id = self._create_project(category_id)
            else:
                project_id = int(project_id)
        except Exception as e:
            print('Try using the project id or type "new" to create a new one')
            print(e)

        return project_id

    def _create_category(self):
        """
        This function inserts a category in the dabase
        
        Returns:
            The category id as int
        """
        print("Creating a new category...")
        category_name = input("Add the category name: ")
        self.cursor.execute(
            "INSERT INTO Categories (category) VALUES (?)", (category_name,)
        )
        self.cursor.execute(
            "SELECT id FROM Categories WHERE category= ?", (category_name,)
        )
        new_category_id = self.cursor.fetchone()[0]

        return new_category_id

    def _create_project(self, category_id):
        """
        This function inserts a project in the dabase
        
        Returns:
            The project id as int
        """
        print("Creating a new project...")
        project_name = input("Add the project name: ")
        date = self._get_date()
        self.cursor.execute(
            "INSERT INTO Projects (name, start, category_id) VALUES (?, ?, ?)",
            (project_name, date, category_id),
        )
        self.cursor.execute(
            "SELECT id FROM Projects WHERE name= ? and category_id= ?",
            (project_name, category_id),
        )
        new_project_id = self.cursor.fetchone()[0]

        return new_project_id

    def add_pomodoro(self, duration, category_id, project_id, satisfaction):
        """
        This function adds the pomodoro data into the database
        
        Args:
            duration: Pomodoro duration, normally 25 min
            satisfaction: 1 if the pomodoro was good, 2 if you 
                did not feel well while doing it.
            category_id: Pomodoro's category
            project_id: Pomodoro's project
        """
        date = self._get_date()
        hour = self._get_date_hour()
        self.cursor.execute(
            "INSERT INTO Pomodoros (time, date, hour, category_id, project_id, satisfaction) VALUES (?, ?, ?, ?, ?,?)",
            (duration, date, hour, category_id, project_id, satisfaction,),
        )

    def end_project(self, project_id):
        """
        This functions adds the date where the project
        finished.
        
        Args:
            project_id: int
        """
        date = self._get_date()
        self.cursor.execute(
            "UPDATE Projects SET end= ? WHERE id= ?", (date, project_id)
        )

    def cancel_project(self, project_id):
        """
        Adds the date when we decide to cancel a project
        
        Args:
            project_id: int
        """
        date = self._get_date()
        self.cursor.execute(
            "UPDATE Projects SET canceled=? WHERE id=?", (date, project_id)
        )

