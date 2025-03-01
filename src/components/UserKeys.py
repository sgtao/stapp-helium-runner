# UserKeys.py
import os
import streamlit as st


class UserKeys:
    def __init__(self):
        self.runner_username = ""
        self.runner_password = ""
        # プリセット確認
        if "runner_username" in st.session_state:
            self.runner_username = st.session_state.runner_username
        elif os.getenv("RUNNER_USERNAME"):
            st.session_state.runner_username = os.getenv("RUNNER_USERNAME")
            self.runner_username = st.session_state.runner_username
        else:
            self.runner_username = ""

        if "runner_password" in st.session_state:
            self.runner_password = st.session_state.runner_password
        elif os.getenv("RUNNER_PASSWORD"):
            st.session_state.runner_password = os.getenv("RUNNER_PASSWORD")
            self.runner_password = st.session_state.runner_password
        else:
            self.runner_password = ""

    def input_key(self):
        # ユーザー名の設定
        st.session_state.runner_username = st.text_input(
            "Runner UserName",
            key="username",
            type="default",
            placeholder="Your ID(i.e. Email)",
            value=self.runner_username,
        )
        # パスワードの設定
        st.session_state.runner_password = st.text_input(
            "Runner Password",
            key="password",
            type="password",
            placeholder="(Your Password)",
            value=self.runner_password,
        )
