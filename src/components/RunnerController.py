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
            if st.button(help="Force Rerun", label="🔄"):
                st.rerun()
        with col2:
            if st.button(help="Reset Status", label="🧹"):
                st.session_state.user_inputs = []
                st.session_state.hl_runner = []
                st.rerun()
        with col3:
            disabled_btn = hl.get_driver() is None
            if st.button(
                help="Close Browser.", label="❌", disabled=disabled_btn
            ):
                hl.kill_browser()
                st.rerun()
        with col4:
            pass
        with col5:
            pass
