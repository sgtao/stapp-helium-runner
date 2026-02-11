# UserInputs.py
from copy import deepcopy

import streamlit as st


class UserInputs:
    """
    st.session.stateを用いて、動的なユーザー入力フィールドを管理するクラス。

    Attributes
    ----------
    keyname : str
        セッションステートに格納するキー名（デフォルトは "user_inputs"）。

    Methods
    -------
    get_keyname():
        現在使用しているセッションステートのキー名を返す。
    get_inputs(index=None):
        すべての入力、または指定インデックスの入力を取得する。
    render_inputs():
        入力フィールドの数を指定し、動的にテキスト入力欄を生成・保持する。
    """

    def __init__(self, keyname="user_inputs"):
        """
        Parameters
        ----------
        keyname : str, optional
            セッションステートに使用するキー名（デフォルト "user_inputs"）。
        """
        self.keyname = keyname
        if self.keyname not in st.session_state:
            st.session_state[self.keyname] = []
        if f"min_{self.keyname}" not in st.session_state:
            st.session_state["min_" + self.keyname] = 0

    def get_keyname(self):
        """
        現在のセッションステートキー名を取得する。

        Returns
        -------
        str
            設定されたキー名。
        """
        return self.keyname

    def get_inputs(self, index: int = None):
        """
        セッションステートから入力内容を取得する。

        Parameters
        ----------
        index : int, optional
            取得したい入力のインデックス（Noneの場合は全件を取得）。

        Returns
        -------
        list[dict] or dict
            全入力（list形式）または指定インデックスの入力（dict形式）。

        """
        inputs = st.session_state[self.keyname]
        if index is None:
            return deepcopy(inputs)

        if len(st.session_state[self.keyname]) == 0:
            raise ValueError(f"st.session_state[{self.keyname}] has no inputs")
        if index >= len(st.session_state[self.keyname]):
            raise IndexError(
                f"index is out of range at st.session_state[{self.keyname}]"
            )

        return deepcopy(inputs[index])

    def render_inputs(self):
        """
        ユーザー入力フィールドを描画し、セッションステートに保存する。

        Notes
        -----
        - `st.number_input` により入力フィールドの数を動的に調整できる。
        - 各テキスト入力は `st.text_input` により個別に生成される。
        - 既存の入力値は保持され、数を減らした場合は末尾が削除される。
        """
        # ユーザー入力フィールドの数を取得
        loaded_num = len(st.session_state[self.keyname])
        num_inputs = st.number_input(
            "Number of User Inputs",
            min_value=st.session_state["min_" + self.keyname],
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

            # 既存の入力値を更新、または新しい入力を追加
            if len(st.session_state[self.keyname]) > i:
                st.session_state[self.keyname][i] = {"value": user_input}
            else:
                st.session_state[self.keyname].append({"value": user_input})

        # 数を減らした場合の調整
        st.session_state[self.keyname] = st.session_state[self.keyname][
            : int(num_inputs)
        ]
