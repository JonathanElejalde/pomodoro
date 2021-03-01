# Learning with Pomodoros and Recalls

Inspired by the wonderful Coursera course [Learning how to learn](https://www.coursera.org/learn/learning-how-to-learn).
I wanted to create an app with two concepts that I found interesting "Pomodoros and Recalls." Thus, I created this app that combines both techniques.

The app has had different versions since the beginning. I first created a console app where you can create pomodoros, and the code of this version can be found inside the `console` folder and we use the `app.py` to run it.

Then, I decided to create a UI for the app where I could also add recalls, so I learned a little bit of PyQT5 which allowed to create an app that enables the creation of pomodoros and recalls.

Finally, I wanted to see a dashboard and have the ability to search and show my recalls, therefore, I created the final version of this idea. I chose to do it using `Streamlit` because I work with data and is a tool that I already knew.

The app is not completed yet, but I feel pretty good with the current result knowing the limitations tha `Streamlit` has to build the interface.

## NOTE:

The app has been designed as a personal app, that is why we need to run it locally and maybe in the future I make it available online.

### Install
```console
git clone https://github.com/JonathanElejalde/pomodoro.git
pip install -r requirements.txt
```

### 
```console
streamlit run web_app.py
```

## Built With

- The interface was created using `Streamlit`
- The funcionality was created using python and libraries like `numpy, pandas`
- Finally, the dashboard was created using `Altair`
