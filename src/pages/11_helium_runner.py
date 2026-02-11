# helium_runner.py
import re
import yaml

import streamlit as st

from ui.ConfigFiles import ConfigFiles
from ui.MainViewer import MainViewer
from ui.RunnerController import RunnerController
from ui.UserKeys import UserKeys
from ui.UserInputs import UserInputs
from logic.AppLogger import AppLogger

APP_TITLE = "Helium Runner"


def init_st_session_state():
    if "web_driver" not in st.session_state:
        st.session_state.web_driver = None
    if "config" not in st.session_state:
        st.session_state.config = None
    if "hl_runner" not in st.session_state:
        st.session_state.hl_runner = []
    if "hl_running" not in st.session_state:
        st.session_state.hl_running = False


def sidebar():
    with st.sidebar:
        user_keys = UserKeys()
        user_keys.input_key()

        user_inputs = UserInputs()
        user_inputs.render_inputs()

        with st.expander("session_state", expanded=False):
            st.write(st.session_state)

        runner_ctrl = RunnerController()
        runner_ctrl.buttons()


def _initialize_user_inputs(config):
    """ユーザー入力の初期化処理"""
    if "actions" not in config:
        return

    app_logger = AppLogger(APP_TITLE)

    # user_input_Nの検出用正規表現
    pattern = re.compile(r"user_input_(\d+)")

    # print("loaded_action")
    app_logger.debug_log("loaded_action")
    min_user_inputs = 0
    for action in config.get("actions", []):
        for key, value in action.items():
            # print(f"key:{key} = {value}")
            app_logger.debug_log(f"key:{key} = {value}")

            # 文字列型の値のみ処理
            if not isinstance(value, str):
                continue

            # 正規表現でuser_input_Nを検出
            match = pattern.match(value)
            if match:
                index = int(match.group(1))
                default_value = action.get("user_default", "")
                # print(f"- index: {index} (default= {default_value})")
                app_logger.debug_log(
                    f"- index: {index} (default= {default_value})"
                )

                # 配列の拡張
                while len(st.session_state.user_inputs) <= index:
                    st.session_state.user_inputs.append(
                        {"value": default_value}
                    )
                    min_user_inputs += 1

                # デフォルト値の設定（上書き防止）
                current_value = st.session_state.user_inputs[index].get(
                    "value"
                )
                if not current_value:
                    st.session_state.user_inputs[index][
                        "value"
                    ] = default_value

    # コンフィグで必要なユーザーインプット数
    return min_user_inputs


def load_config(uploaded_yaml):
    """
    YAMLファイルを読み込み、ユーザー入力を初期化する

    Args:
        uploaded_file: Streamlitのfile_uploaderから受け取るファイルオブジェクト

    Returns:
        Dict[str, Any]: 処理済みの設定データ
    """
    try:
        config = yaml.safe_load(uploaded_yaml)
        st.session_state.user_inputs = []
        st.session_state.min_user_inputs = _initialize_user_inputs(config)
        return config
    except yaml.YAMLError as e:
        st.error(f"YAML解析エラー: {str(e)}")
        return {}
    except Exception as e:
        st.error(f"設定ファイルの処理に失敗しました: {str(e)}")
        return {}


def on_file_upload():
    st.session_state.config = None


def main():
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()

    config_files = ConfigFiles()

    st.title("🏃 Helium Runner")
    main_viewer = MainViewer()

    # selected_config_file = st.selectbox("Select a config file", config_files)
    selected_config_file = config_files.render_config_selector()

    # 選択されたコンフィグファイルを読み込む
    if selected_config_file:
        config = config_files.load_config_from_yaml(selected_config_file)
        config_files.render_config_viewer(selected_config_file, config)
        if st.button("Load config", icon="⬆"):
            app_logger.info_log(f"loaded_config: {selected_config_file}")
            st.session_state.config = config
            st.rerun()

    uploaded_file = st.file_uploader(
        "Choose a YAML config file", type="yaml", on_change=on_file_upload
    )

    if uploaded_file is not None and st.session_state.config is None:
        try:
            config = load_config(uploaded_file)
            if config:
                if "title" in config:
                    config_title = config["title"]
                    app_logger.info_log(f"loaded_config: {config_title}")
                else:
                    app_logger.info_log("loaded_config w.o. title")
                st.session_state.config = config
                # main_viewer.config_viewer(st.session_state.config)
                st.rerun()
        except yaml.YAMLError as e:
            st.error(f"Error loading YAML file: {e}")

    # 設定情報が存在する場合、表示する
    if st.session_state.config:
        main_viewer.config_viewer(st.session_state.config)

    # st.session_state.hl_runner の内容を表示
    main_viewer.hl_runner_viewer()


if __name__ == "__main__":
    init_st_session_state()

    sidebar()
    main()
