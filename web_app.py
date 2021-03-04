import streamlit as st
import time
import winsound
import base64
import dashboard

from queries import Pomodoro, Recall

# MAIN TO DO: Add description for the different parts of the app
# also try to explain the dashboard and what the user should focus on
# when observing it.

# Explain in words what they will see when hovering a plot
# Also try to catch some important information from the dataframes
# that we can use to give a summary in words to the user above the
# dashboards
# TO DO: Keep customizing the plots, adding useful configurations and information.


def timer(minutes=5, mode="rest"):
    """
    This functions creates a timer for work or rest
    depending on the mode.
    
    Args:
        minutes: length of the pomodoro in minutes.
    
    Returns:
        A sound that indicates the end of the timer.
    """
    if mode == "work":
        timer_length = minutes * 60
        sound_file = "end_working.wav"

    elif mode == "rest":
        timer_length = minutes * 60
        sound_file = "end_resting.wav"

    while timer_length > 0:
        # mins, seconds = divmod(timer_length, 60)

        # time_left = str(mins).zfill(2) + ":" + str(seconds).zfill(2)
        # write_time.write(f'{mode.title()}ing ' + time_left + "\r", end="")
        time.sleep(1)
        timer_length -= 1

    return winsound.PlaySound(sound_file, winsound.SND_FILENAME)


def run_pomodoro(pomodoro_queries):
    """
    Runs the complete loop of a pomodoro.
    This means 25 min for working and 5 min 
    for resting
    
    Args:
        pomodoro_queries: Pomodoro object. It controls all the 
            queries to the Pomodoro database
    """

    hour = pomodoro_queries.get_date_hour()
    # Save the value in the url for later use
    st.experimental_set_query_params(starting_hour=hour)
    timer(minutes=25, mode="work")
    timer(minutes=5, mode="rest")


def get_all_recalls(recall_queries, recall_project):
    """
    Gets the recalls of a single project and
    turns them into a single string.
    
    Args:
        recall_queries: Recall object. It controls all the queries
            to the Recall database
        recall_project: str. A project name in the Recall database
        
    returns:
        complete_recall: str.
    """
    recalls = recall_queries.get_recalls(recall_project)
    recalls = [f"**{title}**    \n{recall}" for title, recall in recalls]
    complete_recall = "\n\n".join(recalls)

    return complete_recall


def download_link(object_to_download, filename, download_link_text):
    """
    Generates a link to download the given object_to_download.
    Args:
        object_to_download: str.
        filename: str. filename and extension of file.
        download_link_text: str. Text to display for download link.

    Examples:
        download_link(our_string, 'my_file.txt', 'Click here to download your text!')

    """
    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">{download_link_text}</a>'


if __name__ == "__main__":
    import threading

    from streamlit.report_thread import add_report_ctx

    # Config the page
    st.set_page_config(layout="wide")

    # Pomodoro and Recall queries
    pomodoro_queries = Pomodoro()
    recall_queries = Recall()

    st.title("Learning app")

    pomodoro, recall = st.beta_columns((1, 2))

    ######## POMODORO BLOCK ###########
    with pomodoro:
        st.header("Pomodoro")
        categories = pomodoro_queries.get_categories()
        categories = {cat: id for cat, id in categories}

        # Check if empty
        if len(categories) == 0:
            categories["THERE ARE NOT CATEGORIES CREATED"] = 0

        # Option to add new category if necessary
        add_cat = st.beta_expander("Add new category")
        new_cat_added = False
        with add_cat:
            new_category = st.text_input("Add new category")

            if st.button("Add category"):
                pomodoro_queries.create_category(new_category)
                st.info(f"{new_category} was added")
                new_cat_added = True
                new_categories = pomodoro_queries.get_categories()
                new_categories = {cat: id for cat, id in new_categories}

        # Select category
        if new_cat_added:
            category = st.selectbox("Choose a category",
                                    list(new_categories.keys()))
            cat_id = new_categories[category]
        else:
            category = st.selectbox("Choose a category",
                                    list(categories.keys()))
            cat_id = categories[category]

        # Select project
        projects = pomodoro_queries.get_projects(cat_id)
        projects = {proj: id for proj, id in projects}

        # Option to add a new project if necessary
        add_proj = st.beta_expander("Add new project")
        new_proj_added = False
        with add_proj:
            new_project = st.text_input("Add new project")
            if st.button("Add project"):
                pomodoro_queries.create_project(new_project, cat_id)
                st.info(f"{new_project} was added")
                new_proj_added = True
                new_projects = pomodoro_queries.get_projects(cat_id)
                new_projects = {proj: id for proj, id in new_projects}

        # Select project
        if new_proj_added:
            project = st.selectbox("Choose a project",
                                   list(new_projects.keys()))
        else:
            project = st.selectbox("Choose a project", list(projects.keys()))

        # When new category, this handle the errors
        try:
            proj_id = projects[project]
        except:
            pass

        # Start pomodoro
        if st.button("Start Pomodoro"):

            # TO DO: TRY MULTIPROCESS

            thread = threading.Thread(target=run_pomodoro,
                                      args=[pomodoro_queries])
            add_report_ctx(thread)
            thread.start()

        # Retrieve the hour where the pomodoro started
        hour = st.experimental_get_query_params()

        try:
            hour = hour["starting_hour"]
            write_time = st.empty()
            write_time.info(f"Pomodoro started at: {hour[0]}")
        except:
            pass
        sel_options = st.empty()
        send_btn = st.empty()

        selections = {"Good": 1, "Bad": 2}
        selection = sel_options.selectbox("Pomodoro's satisfaction",
                                          ("Good", "Bad"))

        send_puntuation = st.empty()
        send_puntuation.error("No calification/Firts pomodoro of the session")
        if send_btn.button("Send Calification"):
            hour = st.experimental_get_query_params()
            hour = hour["starting_hour"][0]
            satisfaction = selections[selection]
            pomodoro_queries.add_pomodoro(cat_id,
                                          proj_id,
                                          hour,
                                          satisfaction=satisfaction)
            send_puntuation.success("Calification was sent")

        if st.checkbox(
                f"Enable to End/Cancel {'' if project == None else project.upper()}"
        ):
            # Cancel/End
            # End: project is actually ended
            # Cancel: project closed before the end

            end_cancel_selection = st.selectbox("Do you want to End/Cancel",
                                                ("End", "Cancel"))
            st.error(
                f"If you want to *{end_cancel_selection.upper()}* **{project}** hit the button"
            )

            if st.button("End/Cancel"):
                if end_cancel_selection == "End":
                    pomodoro_queries.end_project(proj_id)
                elif end_cancel_selection == "Cancel":
                    pomodoro_queries.cancel_project(proj_id)

    ######## RECALLS BLOCK ############
    with recall:
        st.header("Recalls")

        # Select project
        recall_projects = recall_queries.get_projects()
        clean_projects = [name[0] for name in recall_projects]
        clean_projects = sorted(clean_projects)
        recall_projects = ["ADD A NEW ONE"] + clean_projects

        # Show current projects
        current_project = st.selectbox("Current projects", recall_projects)

        recall_project = st.text_input(
            "Type a new project if not in current projects",
            f"{'' if current_project == 'ADD A NEW ONE' else current_project}",
        )
        title_input = st.empty()
        text_area = st.empty()

        recall_title = title_input.text_input("Type a recall title")
        recall_text = text_area.text_area("Type the recall")

        if st.button("Add Recall", key=1):
            recall_queries.create_recall(recall_project, recall_title,
                                         recall_text)
            # Clean text areas
            title_input.text_input("Type a recall title", value="", key=1)
            text_area.text_area("Type the recall", value="", key=1)

        # TO DO: Export all the recalls in the database as an ankidroid deck

    # Line
    st.markdown("---")

    ######## SEARCH AND DASHBOARD BLOCK ##########

    search_col, dashboard_col = st.beta_columns((1, 1))

    # Show search checkbox
    with search_col:

        st.header("Search")
        search_checkbox = st.checkbox("Enable search")

    with dashboard_col:
        st.header("Dashboard")
        dashboard_checkbox = st.checkbox("Enable Dashboard")

    # If search enable
    if search_checkbox:
        search_for_col, show_all_recalls_col = st.beta_columns((1, 1))

        # Show the search column functionality
        with search_for_col:
            search_text = st.text_input("Search for", "")
            search_text_btn = st.button("Search")

        # Show all recalls project functionality
        with show_all_recalls_col:

            project_to_show = st.selectbox("Choose a project", clean_projects)
            show_recalls_btn = st.button("Show recalls")

            # Download recalls
            download_recalls_btn = st.button("Download recalls")
            if download_recalls_btn:
                complete_recall = get_all_recalls(recall_queries,
                                                  project_to_show)
                tmp_download_link = download_link(complete_recall,
                                                  f"{project_to_show}.txt",
                                                  "Click here to download")
                st.markdown(tmp_download_link, unsafe_allow_html=True)

        # TO DO: Add a functionality or a way to clean the output
        # when we don't need it anymore

        # If search button is hit
        if search_text_btn:
            results = recall_queries.search_in_recalls(search_text)
            for search_proj, search_title, search_recall in results:
                st.subheader(search_title)
                st.markdown(search_recall)
                st.markdown("\n---\n")

        # If show projects button is hit
        if show_recalls_btn:
            complete_recall = get_all_recalls(recall_queries, project_to_show)
            st.markdown(complete_recall)

    # If dashboard enable
    if dashboard_checkbox:
        df = pomodoro_queries.create_df(pomodoro_queries.QUERY)

        if len(df) > 0:
            year, month, day = dashboard.get_current_date()

            # Set the selectboxes side-to-side
            year_col, month_col = st.beta_columns((1, 1))
            years = range(2020, year + 1)
            year_index = years.index(year)
            months = range(1, 13)
            month_index = months.index(month)
            with year_col:
                year = st.selectbox("Year", years, index=year_index)
            with month_col:
                month = st.selectbox("Month", months, index=month_index)

            monthly_chart = dashboard.monthly_chart(year, month, df)
            st.altair_chart(monthly_chart, use_container_width=True)

            # hour pomodoros
            st.subheader("Understand your bad pomodoros")
            hourly_chart = dashboard.hourly_chart(df)
            st.altair_chart(hourly_chart, use_container_width=True)

            # Project charts
            projects_df = dashboard.create_projects_df(df)

            st.subheader("Hours and days spent by project")
            proj_hours_day = dashboard.projects_hours_days(projects_df)
            st.altair_chart(proj_hours_day, use_container_width=True)

            #  TO DO, Create a better plot for singul project. One that
            # gives meaningful information

        else:
            st.write("# No pomodoros to plot")
