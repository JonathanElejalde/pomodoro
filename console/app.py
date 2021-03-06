import sqlite3
import os

from pomodoro import Pomodoro

os.chdir("..")  # Go up one directory from working directory

# Create database if it does not exist
database_path = "data\pomodoros.db"
if not os.path.exists(database_path):
    print("Creating database ...")
    os.system("database.py")

conn = sqlite3.connect("data\pomodoros.db")
cursor = conn.cursor()

pomodoro = Pomodoro(cursor)

### Main loop
while True:
    # Show the categories available
    category_id = pomodoro.show_categories()
    project_id = pomodoro.show_projects(category_id)
    pomodoro_time = input("Add the length of the pomodoro in minutes: ")

    # call for the timer
    pomodoro.timer(minutes=pomodoro_time)

    # Rest timer
    pomodoro.timer(mode="rest")

    # Ask for satisfaction
    satisfaction = input("Type how well was your pomodoro. 1=Good - 2=Bad: ")

    # Add the pomodoro to the database
    pomodoro.add_pomodoro(pomodoro_time, category_id, project_id, satisfaction)
    conn.commit()

    # Next step
    decision = pomodoro.next_decision()
    if decision == 1:
        continue
    elif decision == 2:
        pomodoro.end_project(project_id)
        conn.commit()
    elif decision == 3:
        pomodoro.cancel_project(project_id)
        conn.commit()
    else:
        break

conn.commit()
conn.close()
print("---ENDING PROGRAM---")

