# helium_runner.py
import base64
import time

from bs4 import BeautifulSoup as bs
import helium as hl
import streamlit as st
import yaml

from components.UserKeys import UserKeys
from components.UserInputs import UserInputs


@st.dialog("Pause for next action")
def confirm_user(message):
    # Only Close Browser
    st.write(message)
    col1, col2 = st.columns(2)
    if col1.button("OK"):
        hl.kill_browser()
        st.session_state.web_driver = None
        st.rerun()
    if col2.button("Cancel"):
        st.rerun()


def get_page_info(web_driver, target="all"):
    """
    ページタイトル、URL、HTMLを取得する関数。
    """
    title = web_driver.title
    url = web_driver.current_url

    if target == "all":
        html = web_driver.page_source
    else:
        # html = web_driver.find_element_by_name(target).text
        # Beautiful SoupでHTMLを解析
        soup = bs(web_driver.page_source, "html.parser")
        # 指定されたセレクタに一致するすべての要素を検索
        elements = soup.select(target)
        # 各要素のテキストコンテンツを抽出
        html = [element.get_text() for element in elements]

    return {"type": "text", "title": title, "url": url, "html": html}


def run_browser_actions(config):
    # browser設定が存在する場合のみブラウザを起動
    if "browser" in config:
        browser_name = config["browser"]["name"]
        start_url = config["browser"]["start_url"]

        if browser_name == "chrome":
            st.session_state.web_driver = hl.start_chrome(start_url)
        elif browser_name == "firefox":
            st.session_state.web_driver = hl.start_firefox(start_url)
        else:
            st.error(f"Unsupported browser: {browser_name}")
            st.session_state.web_driver = None
            return

    actions = []
    if "actions" in config:
        actions = config["actions"]
        if st.session_state.web_driver is None:
            st.error("Browser not activate!")
            return

    for action in actions:
        if action["type"] == "write_message":
            hl.write(st.session_state.write_message)
        # elif action["type"] == "write":
        #     hl.write(action["text"])
        elif action["type"] == "write":
            try:
                hl.write(action["text"], into=action["target"])
            except LookupError:
                st.error(
                    f"'{action['type']}': '{action['target']}' not found."
                )
                return
        elif action["type"] == "write_user_key":
            try:
                keyname = action.get("key")
                if keyname not in st.session_state:
                    st.error(
                        f"{action['type']}'Key({keyname}) Not Found in state!"
                    )
                    return
                value = st.session_state[keyname]
                hl.write(value, into=action["target"])
            except LookupError:
                st.error(
                    f"'{action['type']}': '{action['target']}' not found."
                )
                return
        elif action["type"] == "click":
            try:
                target_name = action["target"]
                if "user_target" in action:
                    target_name = get_user_input(
                        action.get("user_target"), action.get("user_default")
                    )
                if action["target"].startswith("Button:"):
                    # action["target"] が "Button:" で始まる場合は Button として扱う
                    len_ommit = len("Button:")
                    target_name = action["target"][len_ommit:]
                    hl.wait_until(hl.Button(target_name).exists)
                elif action["target"].startswith("Link:"):
                    # action["target"] が "Link:" で始まる場合は Link として扱う
                    len_ommit = len("Link:")
                    target_name = action["target"][len_ommit:]
                    hl.wait_until(hl.Link(target_name).exists)
                elif action["target"].startswith("Text:"):
                    # action["target"] が "Text:" で始まる場合は 直接指定する
                    len_ommit = len("Text:")
                    target_name = action["target"][len_ommit:]
                    hl.wait_until(hl.Text(target_name).exists)
                else:
                    # それ以外の場合は、要素名を直接指定して待機する
                    hl.wait_until(hl.Text(target_name).exists)
                # Click Target
                hl.click(target_name)
            except LookupError:
                st.error(
                    f"'{action['type']}': '{action['target']}' not found."
                )
                return
        elif action["type"] == "press":
            value = action.get("value")
            if value == "ENTER":
                hl.press(hl.ENTER)
            else:
                st.error(f"'{action['type']}': '{value}' not supported.")
                return
        elif action["type"] == "wait":
            seconds = action.get("seconds")
            if "user_seconds" in action:
                seconds = get_user_input(
                    action.get("user_seconds"), action.get("user_default")
                )
                seconds = float(seconds)

            # wait(action["seconds"])
            # confirm_user("Waiting Run...")
            time.sleep(seconds)
        elif action["type"] == "go_to":
            try:
                url = "..."
                if "url" in action:
                    url = action.get("url")
                elif "user_url" in action:
                    url = get_user_input(
                        action.get("user_url"), action.get("user_default")
                    )
                hl.go_to(url)
            except Exception as e:
                st.error(f"Error navigating to URL: {e}")
                return

        elif action["type"] == "scrape_page":
            target = "all"
            if "target" in action:
                target = action["target"]

            try:
                # SeleniumのWebDriverオブジェクトを取得
                driver = hl.get_driver()

                # ページ情報を取得
                page_info = get_page_info(driver, target)

                # 変数名を取得
                variable = action.get("variable")

                # Streamlitのセッションステートに格納
                # st.session_state.hl_runner[variable] = page_info
                st.session_state.hl_runner.append(
                    {
                        "key": variable,
                        "value": page_info,
                    }
                )

                if page_info:
                    st.info(f"ページ情報を変数 [{variable}] に保存しました。")
                else:
                    st.warning("ページ情報がありません。")

            except Exception as e:
                st.error(f"ページ情報の取得に失敗しました: {e}")
                return

    if "end_action" in config:
        end_action = config["end_action"]
        if end_action == "kill_browser":
            hl.kill_browser()
            st.session_state.web_driver = None
            return
        elif end_action == "stop_run":
            st.info("Finish run!")
            confirm_user("Close Browser?")
        elif end_action == "get_screen":
            try:
                # メモリ上でスクリーンショットを処理
                driver = hl.get_driver()
                screenshot_png = driver.get_screenshot_as_png()

                # BASE64エンコード
                encoded_image = base64.b64encode(screenshot_png).decode(
                    "utf-8"
                )

                # セッションステートに保存
                st.session_state.hl_runner.append(
                    {
                        "key": "screenshot",
                        "value": {
                            "type": "image",
                            "data": f"data:image/png;base64,{encoded_image}",
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        },
                    }
                )

                st.success("スクリーンショットを保存しました")

            except Exception as e:
                st.error(f"スクリーンショット取得失敗: {e}")

        else:
            st.error(f"Unsupported end action: {end_action}")


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


def get_state_user_inputs(key):
    if key == "user_input_0":
        return st.session_state.user_inputs[0]["value"]


def sidebar():
    user_inputs_key = "user_inputs"
    with st.sidebar:
        user_keys = UserKeys()
        user_keys.input_key()

        user_inputs = UserInputs()
        user_inputs.input_expander(user_inputs_key)

        with st.expander("session_state", expanded=False):
            st.write(st.session_state)


def config_viewer(config):
    with st.expander("Show Config File:", expanded=False):
        st.write(config)

    # 初回表示時または状態リセット時
    if not st.session_state.get("hl_running"):
        # ボタンの状態をセッションステートと連動
        if st.button(
            "Run Config",
            type="primary",
            key="run_config_main",
            # disabled=True,
            disabled=st.session_state.hl_running,
        ):
            st.session_state.hl_running = True
            # button_container.empty()  # ボタンを即時非表示
            st.rerun()

    # 実行状態の場合
    if st.session_state.get("hl_running"):
        with st.spinner("処理を実行中です..."):
            time.sleep(1)  # デモ用の遅延
            try:
                run_browser_actions(config)
            except Exception as e:
                st.error(f"実行エラー: {str(e)}")
            finally:
                st.session_state.hl_running = False
                st.rerun()


def hl_runner_viewer():

    # st.session_state.hl_runner の内容を表示
    if len(st.session_state.hl_runner) == 0:
        st.info("ページ情報がありません。")
        return

    st.info("取得したページ情報:")

    # 削除対象のアイテムを格納するリスト
    items_to_delete = []

    for i, item in enumerate(st.session_state.hl_runner):
        variable_name = item["key"]
        page_info = item["value"]

        with st.expander(f"変数名: {variable_name}:", expanded=False):
            # チェックボックスを追加
            delete_checkbox = st.checkbox(
                f"削除: {variable_name}", key=f"delete_{i}"
            )
            if delete_checkbox:
                items_to_delete.append(i)

            # 画像データの表示
            if (
                isinstance(page_info, dict)
                and page_info.get("type") == "image"
            ):
                st.image(
                    page_info["data"],
                    caption=f"Screenshot ({page_info['timestamp']})",
                    # use_column_width=True,
                )
            else:
                st.write(page_info)

    # 削除ボタンを追加
    if st.button("選択したアイテムを削除"):
        # 削除対象のアイテムをセッションステートから削除 (逆順に削除)
        for i in sorted(items_to_delete, reverse=True):
            del st.session_state.hl_runner[i]

        st.success("選択したアイテムを削除しました。")
        st.rerun()  # アプリを再実行して表示を更新


def main():
    st.title("Helium Runner")

    uploaded_file = st.file_uploader("Choose a YAML config file", type="yaml")

    if uploaded_file is not None:
        try:
            config = yaml.safe_load(uploaded_file)
            # st.session_state.hl_running = False
            #
            config_viewer(config)
        except yaml.YAMLError as e:
            st.error(f"Error loading YAML file: {e}")

    # st.session_state.hl_runner の内容を表示
    hl_runner_viewer()


def get_user_input(key, default_value):
    """
    ユーザー入力を取得する関数。
    """
    if key.startswith("user_input_"):
        # index = int(key[{len("user_input_")} :])
        index = int(key[11:])
        if (
            "user_inputs" in st.session_state
            and len(st.session_state.user_inputs) > index
        ):
            return st.session_state.user_inputs[index]["value"]
        else:
            return default_value
    return default_value


if __name__ == "__main__":
    init_st_session_state()
    sidebar()
    main()
