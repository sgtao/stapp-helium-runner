# UserInputs.py
import streamlit as st


class UserInputs:
    def render_inputs(self, keyname="user_inputs"):
        # ユーザー入力フィールドの数を取得
        loaded_num = len(st.session_state.user_inputs)
        num_inputs = st.number_input(
            "Number of User Inputs",
            min_value=st.session_state.min_user_inputs,
            max_value=10,
            value=loaded_num,
            step=1,
        )

        # ユーザー入力フィールドを動的に生成
        for i in range(num_inputs):
            # 既存の入力値を保持
            if (
                keyname in st.session_state
                and len(st.session_state[keyname]) > i
            ):
                default_value = st.session_state[keyname][i]["value"]
            else:
                default_value = ""

            user_input = st.text_input(
                f"Input {i}", value=default_value, key=f"user_input_{i}"
            )

            # セッションステートに保存
            if keyname not in st.session_state:
                st.session_state[keyname] = []

            # 既存の入力値を更新、または新しい入力を追加
            if len(st.session_state[keyname]) > i:
                st.session_state[keyname][i] = {"value": user_input}
            else:
                st.session_state[keyname].append({"value": user_input})
