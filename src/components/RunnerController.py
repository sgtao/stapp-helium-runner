# RunnerController.py
import helium as hl
import streamlit as st


class RunnerController:
    def buttons(self):
        st.write("##### Runner Ctrl.")
        (
            col1,
            col2,
            col3,
            col4,
            col5,
        ) = st.columns(5)
        with col1:
            if st.button(help="Reset Status", label="🔄"):
                st.session_state.hl_runner = []
                st.rerun
        with col2:
            disabled_btn = hl.get_driver() is None
            if st.button(
                help="Close Browser.", label="❌", disabled=disabled_btn
            ):
                hl.kill_browser()
        with col3:
            pass
        with col4:
            pass
        with col5:
            pass
