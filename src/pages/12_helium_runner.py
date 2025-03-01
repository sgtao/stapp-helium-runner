# 12_helium_runner.py
import time

import helium as hl
import streamlit as st
import yaml


@st.dialog("Pause for next action")
def confirm_user(message):
    # Only Close Browser
    st.write(message)
    col1, col2 = st.columns(2)
    if col1.button("OK"):
        hl.kill_browser()
        st.rerun()
    if col2.button("Cancel"):
        st.rerun()


def get_page_info(web_driver):
    """
    ページタイトル、URL、HTMLを取得する関数。
    """
    title = web_driver.title
    url = web_driver.current_url
    # html = hl.get_page_source()
    html = "foo-bar"
    return {"title": title, "url": url, "html": html}


def run_browser_actions(config):
    browser_name = config["browser"]["name"]
    start_url = config["browser"]["start_url"]
    actions = config["actions"]
    end_action = config["end_action"]
    if "hl_runner" not in st.session_state:
        st.session_state["hl_runner"] = {}

    if browser_name == "chrome":
        hl.start_chrome(start_url)
    elif browser_name == "firefox":
        hl.start_firefox(start_url)
    else:
        st.error(f"Unsupported browser: {browser_name}")
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

        elif action["type"] == "press":
            hl.press(hl.ENTER)
        elif action["type"] == "wait":
            # wait(action["seconds"])
            # confirm_user("Waiting Run...")
            time.sleep(action["seconds"])
        elif action["type"] == "go_to":
            try:
                hl.go_to(action["url"])
            except Exception as e:
                st.error(f"Error navigating to URL: {e}")
                return

        elif action["type"] == "scrape_page":
            try:
                # SeleniumのWebDriverオブジェクトを取得
                driver = hl.get_driver()

                # ページ情報を取得
                page_info = get_page_info(driver)

                # 変数名を取得
                variable = action.get("variable", "page_info")

                # Streamlitのセッションステートに格納
                st.session_state.hl_runner[variable] = page_info
                st.info(f"ページ情報を変数 [{variable}] に保存しました。")
                st.write(st.session_state.hl_runner[variable])
            except Exception as e:
                st.error(f"ページ情報の取得に失敗しました: {e}")
                return

    if end_action == "kill_browser":
        hl.kill_browser()
    elif end_action == "stop_run":
        st.info("Finish run!")
        confirm_user("Close Browser?")
    else:
        st.error(f"Unsupported end action: {end_action}")


def init_st_session_state():
    if "write_message" not in st.session_state:
        st.session_state.write_message = ""


def sidebar():
    with st.sidebar:
        default_message = "foo bar"
        if st.session_state.write_message == "":
            default_message = st.session_state.write_message
        st.session_state.write_message = st.text_input(
            "Enter message to write", value=default_message
        )


def main():
    st.title("Helium Runner")

    uploaded_file = st.file_uploader("Choose a YAML config file", type="yaml")

    if uploaded_file is not None:
        try:
            config = yaml.safe_load(uploaded_file)
            with st.expander("Show Config File:", expanded=False):
                st.write(config)
            # st.markdown(config)
            if st.button("Run Config", type="primary"):
                run_browser_actions(config)
        except yaml.YAMLError as e:
            st.error(f"Error loading YAML file: {e}")


if __name__ == "__main__":
    init_st_session_state()
    sidebar()
    main()
