# helium_runner.py
import streamlit as st
import yaml

from components.MainViewer import MainViewer
from components.RunnerController import RunnerController
from components.UserKeys import UserKeys
from components.UserInputs import UserInputs


def init_st_session_state():
    if "write_message" not in st.session_state:
        st.session_state.write_message = ""
    if "hl_runner" not in st.session_state:
        st.session_state.hl_runner = []
    if "hl_running" not in st.session_state:
        st.session_state.hl_running = False
    if "web_driver" not in st.session_state:
        st.session_state.web_driver = None
    if "user_inputs" not in st.session_state:
        st.session_state.user_inputs = []


def sidebar():
    user_inputs_key = "user_inputs"
    with st.sidebar:
        user_keys = UserKeys()
        user_keys.input_key()

        user_inputs = UserInputs()
        user_inputs.input_expander(user_inputs_key)

        with st.expander("session_state", expanded=False):
            st.write(st.session_state)

        runner_ctrl = RunnerController()
        runner_ctrl.buttons()


def main():
    st.title("Helium Runner")
    main_viewer = MainViewer()

    uploaded_file = st.file_uploader("Choose a YAML config file", type="yaml")

    if uploaded_file is not None:
        try:
            config = yaml.safe_load(uploaded_file)
            # st.session_state.hl_running = False
            #
            main_viewer.config_viewer(config)
        except yaml.YAMLError as e:
            st.error(f"Error loading YAML file: {e}")

    # st.session_state.hl_runner の内容を表示
    main_viewer.hl_runner_viewer()


if __name__ == "__main__":
    init_st_session_state()
    sidebar()
    main()
