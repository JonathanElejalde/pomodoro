from altair.vegalite.v4 import schema
from altair.vegalite.v4.schema.channels import Tooltip
import pandas as pd
import altair as alt
import numpy as np

from queries import Pomodoro

THEME = 'magma'


def get_current_date():
    """
    Gets the current date to perform default 
    charts.
    
    returns:
        date: tuple. (year, month, day)
    """
    date = pd.to_datetime('now')

    year = date.year
    month = date.month
    day = date.day

    return (year, month, day)


# POMODORO CHARTS
def monthly_chart(year, month, df):
    """
    
    """
    # Filter
    df_copy = df.copy()
    filtered = df_copy.loc[f'{year}/{month}']

    month_name = filtered.pomodoro_date.dt.month_name()
    month_name = month_name.iloc[0]

    base = alt.Chart(
        filtered, title=f'Productivity in {month_name}').mark_circle().encode(
            x=alt.X('monthdate(pomodoro_date):O',
                    title='Days',
                    axis=alt.Axis(labelAngle=-90)),
            y=alt.Y('hoursminutes(pomodoro_date)', title='Daily hours'),
        ).properties(width=400, height=200)

    stack = base.mark_bar().encode(y=alt.Y('count()', title='Daily pomodoros'),
                                   color=alt.Color('project',
                                                   title='Project names'),
                                   tooltip=[
                                       alt.Tooltip('category',
                                                   title='Category'),
                                       alt.Tooltip('project',
                                                   title='Project name'),
                                       alt.Tooltip('count()',
                                                   title='Pomodoros'),
                                       alt.Tooltip(
                                           'sum(pomodoro_length)',
                                           title='Minutes invested this day')
                                   ])

    scatter = base.encode(color=alt.Color('project', title='Project names'),
                          tooltip=[
                              alt.Tooltip('category', title='Category'),
                              alt.Tooltip('project', title='Project name'),
                              alt.Tooltip('yearmonthdate(pomodoro_date)',
                                          title='Date'),
                              alt.Tooltip('pomodoro_calification',
                                          title='Satisfaction'),
                              alt.Tooltip('hoursminutes(pomodoro_date)',
                                          title='Start')
                          ],
                          size=alt.Size('pomodoro_calification',
                                        sort='descending',
                                        title='Calification'))

    chart = alt.hconcat(stack, scatter)

    return chart


def hourly_chart(df):
    """
    """
    df_copy = df.copy()
    # Get only the bad pomodoros
    bad_condition = df_copy.pomodoro_calification == 'Bad'
    bad_df = df_copy[bad_condition]

    # Filtered pomodoros without calification
    condition = df_copy.pomodoro_calification != 0
    new_df = df_copy[condition]

    grouped_chart = alt.Chart(new_df).mark_bar().encode(
        alt.X('pomodoro_calification:N', title="", axis=None),
        alt.Y('count():Q', title='Pomodoro count'),
        alt.Column('hours(pomodoro_date):O',
                   title='Good and Bad pomodoros by hour'),
        alt.Color('pomodoro_calification:N', title='Calification'),
        tooltip=[alt.Tooltip('hours(pomodoro_date)'),
                 alt.Tooltip('count()')]).properties(width=20, height=200)

    heatmap = alt.Chart(
        bad_df, title='Bad pomodoros by day and hour').mark_rect().encode(
            alt.X('hours(pomodoro_date)',
                  title='Hours',
                  axis=alt.Axis(labelAngle=-90)),
            alt.Y('day(pomodoro_date):O', title='Day of the week'),
            alt.Color('count():Q',
                      title='Pomodoro count',
                      scale=alt.Scale(domain=(10, 1), scheme=THEME)),
            tooltip=[
                alt.Tooltip('count()', title='Bad pomodoros'),
                alt.Tooltip('sum(pomodoro_length)', title='Minutes wasted'),
                alt.Tooltip('hours(pomodoro_date)', title='Hour')
            ]).properties(width=400, height=200)

    return grouped_chart & heatmap


## PROJECT CHARTS
def create_projects_df(df):
    """
    """

    df_copy = df.copy()
    date_format = '%Y-%m-%d'
    tmp_projects = df_copy.groupby('project').agg({
        'category':
        'first',
        'project_start':
        'first',
        'project_end':
        'first',
        'project_cancel':
        'first',
        'pomodoro_length':
        'sum',
        'pomodoro_calification':
        'count'
    })

    # Rename the columns resulting from the groupby
    project_columns = {
        'project_start': 'start',
        'project_end': 'end',
        'project_cancel': 'cancel',
        'pomodoro_length': 'minutes',
        'pomodoro_calification': 'total_pomodoros'
    }
    tmp_projects.rename(columns=project_columns, inplace=True)

    # Create separete columns for the pomodoro califications
    tmp_projects_2 = df_copy.groupby(
        'project')['pomodoro_calification'].value_counts().unstack().fillna(0)

    # Merge the two resulting groupby dataframes
    projects = pd.merge(tmp_projects,
                        tmp_projects_2,
                        left_index=True,
                        right_index=True)

    # Create the project status column.
    conditions = [projects.end.notnull(), projects.cancel.notnull()]
    choices = ['Ended', 'Canceled']
    projects['status'] = np.select(conditions, choices, default='On')

    # Create the days column. It counts the amount of days since its
    # start until its end/cancel date or current day if still on.
    today = pd.to_datetime("today", format=date_format)
    end_mask = (projects.status == "Ended")
    cancel_mask = (projects.status == 'Canceled')
    on_mask = (projects.status == 'On')
    projects['days'] = 0
    projects.loc[end_mask, 'days'] = (projects.end - projects.start).dt.days
    projects.loc[cancel_mask,
                 'days'] = (projects.cancel - projects.start).dt.days
    projects.loc[on_mask, 'days'] = (today - projects.start).dt.days

    # Convert the minutes count into hours
    projects['hours'] = pd.to_datetime(projects.minutes,
                                       unit='m').dt.strftime('%H:%M')

    # Convert the minutes column to amount of pomodoros
    projects['pomodoros'] = projects.minutes / 25

    projects.reset_index(inplace=True)

    return projects


def projects_hours_days(df):
    """
    """
    df_copy = df.copy()
    single = alt.selection_single()

    chart = alt.Chart(
        df_copy, title='Projects').mark_point(filled=True).encode(
            alt.X('yearmonthdate(start)', title="Project start date"),
            alt.Y('days', title='Days since the start'),
            color=alt.Color(
                'status:N',
                title='Project current status',
                sort='descending',
            ),
            size=alt.Size('hours',
                          title='Total hours invested in the project'),
            tooltip=[
                alt.Tooltip('category'),
                alt.Tooltip('project'),
                alt.Tooltip('start', title='Project start date'),
                alt.Tooltip('status'),
                alt.Tooltip('days', title='Days since the start'),
                alt.Tooltip('hours', title='Total hours invested'),
                alt.Tooltip('pomodoros', title='Amount of pomodoros made')
            ]).add_selection(single).properties(width=800).interactive()

    return chart


# Make possible to show various plojects
def plot_project(project, df):
    """
    """
    df_copy = df.copy()

    # Filterer the project
    filtered = df_copy[df_copy.project == project]

    # Get start and end dates
    row = filtered.iloc[0]
    start = row.project_start
    end = row.project_end
    cancel = row.project_cancel

    start = start.date()
    if end:
        last = end.date()
    elif cancel:
        last = cancel.date()
    else:
        today = pd.to_datetime("today")
        last = today.date()

    line = alt.Chart(filtered).mark_bar().encode(
        alt.X(
            'yearmonthdate(pomodoro_date):O',
            # scale=alt.Scale(
            #     domain=[start.isoformat(), last.isoformat()]),
            axis=alt.Axis(labelAngle=-90)),
        alt.Y('count()')).configure_range(category={'scheme': 'dark2'})

    return line


def my_theme():
    return {
        'config': {
            'view': {
                'continuousHeight': 300,
                'continuousWidth': 400
            },  # from the default theme
            'range': {
                'category': {
                    'scheme': THEME
                }
            }
        }
    }


# Altair theme
alt.themes.register('my_theme', my_theme)
alt.themes.enable('my_theme')

if __name__ == "__main__":

    pomodoro = Pomodoro()
    df = pomodoro.create_df(pomodoro.QUERY)
    project = 'El asesinato de Roger Ackroyd - Agatha Christie'
    filtered = plot_project(project, df)
