# UserInputs.py
import streamlit as st


class UserInputs:
    def __init__(self):
        self.user_inputs = []

        # item0：テキスト入力
        text_preset = {
            "type": "text",
            "value": "",
        }
        self.user_inputs.append(text_preset)
        st.session_state.user_inputs = self.user_inputs

    def input_expander(self):
        with st.expander("User Inputs", expanded=False):
            # item 0
            st.session_state.user_inputs[0]["value"] = st.text_input(
                "User Input 0 (Text)",
                key="user_input0",
                type="default",
                placeholder="UserInput 0",
                value=st.session_state.user_inputs[0]["value"],
            )
