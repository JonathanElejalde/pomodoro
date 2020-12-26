def create_database(cursor):
    # Make some fresh tables using executescript()
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


if __name__ == "__main__":

    import sqlite3

    # --CREATING THE DATABASE--
    conn = sqlite3.connect("pomodoroTimer.db")
    cursor = conn.cursor()

    # This will run if the database is not created already
    create_database(cursor)
