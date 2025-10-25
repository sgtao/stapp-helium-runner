# run_hl_actions.py
import base64
import time

from bs4 import BeautifulSoup as bs
import helium as hl
import streamlit as st

from functions.AppLogger import AppLogger

APP_TITLE = "Helium Runner"


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


def get_target_link(web_driver, target="all"):
    """
    ページタイトル、URL、HTMLを取得する関数。
    """
    title = web_driver.title
    url = web_driver.current_url

    if target == "all":
        html = web_driver.page_source
    else:
        soup = bs(web_driver.page_source, "html.parser")
        elements = soup.select(target)
        # # aタグの場合はhref属性を取得
        # if target == "a" or target == "a[href]":
        #     html = [element.get("href") for element in elements]
        # else:
        #     html = [element.get_text() for element in elements]
        # リンク情報を辞書形式で取得
        html = [
            {"text": element.get_text(strip=True), "url": element.get("href")}
            for element in elements
        ]

    return {"type": "text", "title": title, "url": url, "html": html}


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


def run_hl_actions(config):
    app_logger = AppLogger(APP_TITLE)

    # browser設定が存在する場合のみブラウザを起動
    if "hl_start_browser" in config:
        browser_name = config["hl_start_browser"]["name"]
        start_url = config["hl_start_browser"]["start_url"]

        if browser_name == "chrome":
            # st.session_state.web_driver = hl.start_chrome(start_url)
            st.session_state.web_driver = hl.start_chrome(
                start_url, headless=True
            )
        elif browser_name == "firefox":
            st.session_state.web_driver = hl.start_firefox(start_url)
        else:
            st.error(f"Unsupported browser: {browser_name}")
            st.session_state.web_driver = None
            return

        app_logger.info_log(f"start_browser {browser_name} to {start_url}")

    actions = []
    if "actions" in config:
        actions = config["actions"]
        if st.session_state.web_driver is None:
            st.error("Browser not activate!")
            return

    for action in actions:
        if action["type"] == "hl_write":
            try:
                if ("target" not in action) or len(action["target"]) == 0:
                    hl.write(action["text"])
                else:
                    hl.write(action["text"], into=action["target"])
            except LookupError:
                st.error(
                    f"'{action['type']}': '{action['target']}' not found."
                )
                return
        elif action["type"] == "hl_write_user_key":
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
        elif action["type"] == "hl_click":
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
        elif action["type"] == "hl_press":
            value = action.get("value")
            if "key" in action:
                value = action.get("key")
            if value == "ENTER":
                hl.press(hl.ENTER)
            else:
                st.error(f"'{action['type']}': '{value}' not supported.")
                return
        elif action["type"] == "hl_wait":
            seconds = action.get("seconds")
            if "user_seconds" in action:
                seconds = get_user_input(
                    action.get("user_seconds"), action.get("user_default")
                )
                seconds = float(seconds)

            time.sleep(seconds)
        elif action["type"] == "hl_go_to":
            try:
                url = "..."
                if "url" in action:
                    url = action.get("url")
                elif "user_url" in action:
                    url = get_user_input(
                        action.get("user_url"), action.get("user_default")
                    )
                hl.go_to(url)
                app_logger.info_log(f"go to {url}")

            except Exception as e:
                # st.error(f"Error navigating to URL: {e}")
                # return
                raise f"Error navigating to URL: {e}"

        elif action["type"] == "hl_scrape_page":
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
                # st.error(f"ページ情報の取得に失敗しました: {e}")
                # return
                raise f"ページ情報の取得に失敗しました: {e}"

        elif action["type"] == "hl_scrape_links":
            target = "all"
            if "target" in action:
                target = action["target"]

            try:
                # SeleniumのWebDriverオブジェクトを取得
                driver = hl.get_driver()

                # リンク情報を取得
                page_info = get_target_link(driver, target)

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
                # st.error(f"ページ情報の取得に失敗しました: {e}")
                # return
                raise f"ページ情報の取得に失敗しました: {e}"

    if "hl_end_action" in config:
        end_action = config["hl_end_action"]
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
                # w = driver.execute_script(
                #     "return document.body.parentNode.scrollWidth"
                # )
                # h = driver.execute_script(
                #     "return document.body.parentNode.scrollHeight"
                # )
                # driver.set_window_size(w, h)
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
                # st.error(f"スクリーンショット取得失敗: {e}")
                raise f"スクリーンショット取得失敗: {e}"

        else:
            # st.error(f"Unsupported end action: {end_action}")
            raise f"Unsupported end action: {end_action}"

        # at end_action, wait for 3 seconds.
        time.sleep(3)
