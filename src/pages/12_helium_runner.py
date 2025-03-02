# 12_helium_runner.py
import time

from bs4 import BeautifulSoup as bs
import helium as hl
import streamlit as st
import yaml
from selenium.webdriver.remote.webdriver import WebDriver

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


def get_page_info(web_driver: WebDriver, target="all"):
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

    return {"title": title, "url": url, "html": html}


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

        elif action["type"] == "pressENTER":
            hl.press(hl.ENTER)
        elif action["type"] == "wait":
            # wait(action["seconds"])
            # confirm_user("Waiting Run...")
            time.sleep(action["seconds"])
        elif action["type"] == "go_to":
            try:
                url = "..."
                if "url" in action:
                    url = action.get("url")
                if "user_default" in action:
                    url = action.get("user_default")
                if "user_url" in action:
                    url = get_state_user_inputs(action.get("user_url"))
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
        else:
            st.error(f"Unsupported end action: {end_action}")


def init_st_session_state():
    if "write_message" not in st.session_state:
        st.session_state.write_message = ""
    if "hl_runner" not in st.session_state:
        st.session_state.hl_runner = []
    if "web_driver" not in st.session_state:
        st.session_state.web_driver = None
    if "user_inputs" not in st.session_state:
        st.session_state.user_inputs = []


def get_state_user_inputs(key):
    if key == "user_input_0":
        return st.session_state.user_inputs[0]["value"]


def sidebar():
    with st.sidebar:
        user_keys = UserKeys()
        user_keys.input_key()

        user_inputs = UserInputs()
        user_inputs.input_expander()

        with st.expander("session_state", expanded=False):
            st.write(st.session_state)


def config_viewer(config):
    with st.expander("Show Config File:", expanded=False):
        st.write(config)
    # st.markdown(config)
    if st.button("Run Config", type="primary"):
        run_browser_actions(config)


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
            st.write(page_info)

            # チェックボックスを追加
            delete_checkbox = st.checkbox(
                f"削除: {variable_name}", key=f"delete_{i}"
            )
            if delete_checkbox:
                items_to_delete.append(i)

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
            config_viewer(config)
        except yaml.YAMLError as e:
            st.error(f"Error loading YAML file: {e}")

    # st.session_state.hl_runner の内容を表示
    hl_runner_viewer()


if __name__ == "__main__":
    init_st_session_state()
    sidebar()
    main()
