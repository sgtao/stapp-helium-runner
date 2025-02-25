# 12_run_helium_config.py
from helium import (
    ENTER,
)
import helium as hl
import streamlit as st
import yaml


@st.dialog("Pause for next action")
def confirm_user(message):
    st.write(message)
    if st.button("OK"):
        st.rerun()


def run_browser_actions(config):
    browser_name = config["browser"]["name"]
    start_url = config["browser"]["start_url"]
    actions = config["actions"]
    end_action = config["end_action"]

    if browser_name == "chrome":
        hl.start_chrome(start_url)
    elif browser_name == "firefox":
        hl.start_firefox(start_url)
    else:
        st.error(f"Unsupported browser: {browser_name}")
        return

    for action in actions:
        if action["type"] == "write_message":
            hl.write(st.session_state.write_message)
        elif action["type"] == "write":
            hl.write(action["text"])
        elif action["type"] == "press":
            hl.press(ENTER)
        elif action["type"] == "wait":
            # wait(action["seconds"])
            confirm_user("Waiting Run...")

    if end_action == "kill_browser":
        hl.kill_browser()
    elif end_action == "stop_run":
        st.info("Finish run!")
    else:
        st.error(f"Unsupported end action: {end_action}")


def init_st_session_state():
    if "write_message" not in st.session_state:
        st.session_state.write_message = ""


def sidebar():
    with st.sidebar:
        default_message = "foo bar"
        if st.session_state.write_message == "":
            default_message = st.session_state.write_message
        st.session_state.write_message = st.text_input(
            "Enter message to write", value=default_message
        )


def main():
    st.title("Helium YAML Config")

    uploaded_file = st.file_uploader("Choose a YAML config file", type="yaml")

    if uploaded_file is not None:
        try:
            config = yaml.safe_load(uploaded_file)
            # st.markdown(config)
            st.write(config)
            if st.button("Start Config"):
                run_browser_actions(config)
        except yaml.YAMLError as e:
            st.error(f"Error loading YAML file: {e}")


if __name__ == "__main__":
    init_st_session_state()
    sidebar()
    main()
