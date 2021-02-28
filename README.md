# Pomodoros and recalls for learning

Inspired by the wonderful Coursera course [Learning how to learn](https://www.coursera.org/learn/learning-how-to-learn).
I wanted a programmatical way to apply some of the amazing things learned. Thus, I created this app that combines the 
pomodoro and recall techniques. I used qt-designer to create a simple UI that let you create a 25 min pomodoro
allowing us to add a category, a project name and finally add recalls or information that you may want to retrieve later.


- [Explanation about pomodoros](https://en.wikipedia.org/wiki/Pomodoro_Technique)

### Install
```console
git clone https://github.com/JonathanElejalde/pomodoro.git
```

### Run
```console
python app.py
```

## Built With

- Pyqt5 for the UI design. It is something simple
- sqlite3 to store the pomodoros and recalls
- Finally, regular python to create the functionality on top of the UI
