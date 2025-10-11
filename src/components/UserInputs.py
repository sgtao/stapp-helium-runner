# UserInputs.py
import streamlit as st


class UserInputs:
    def __init__(self, keyname="user_inputs"):
        self.keyname = keyname
        if self.keyname not in st.session_state:
            st.session_state[self.keyname] = []
        if f"min_{self.keyname}" not in st.session_state:
            st.session_state[{"min_" + self.keyname}] = 0

    def render_inputs(self):
        # ユーザー入力フィールドの数を取得
        loaded_num = len(st.session_state[self.keyname])
        num_inputs = st.number_input(
            "Number of User Inputs",
            min_value=st.session_state[{"min_" + self.keyname}],
            max_value=10,
            value=loaded_num,
            step=1,
        )

        # ユーザー入力フィールドを動的に生成
        for i in range(num_inputs):
            # 既存の入力値を保持
            if (
                self.keyname in st.session_state
                and len(st.session_state[self.keyname]) > i
            ):
                default_value = st.session_state[self.keyname][i]["value"]
            else:
                default_value = ""

            user_input = st.text_input(
                f"Input {i}", value=default_value, key=f"{self.keyname}_{i}"
            )

            # セッションステートに保存
            if self.keyname not in st.session_state:
                st.session_state[self.keyname] = []

            # 既存の入力値を更新、または新しい入力を追加
            if len(st.session_state[self.keyname]) > i:
                st.session_state[self.keyname][i] = {"value": user_input}
            else:
                st.session_state[self.keyname].append({"value": user_input})
