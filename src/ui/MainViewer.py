# MainViewer.py
import time

import streamlit as st

from logic.run_hl_actions import run_hl_actions


class MainViewer:
    def config_viewer(self, config):
        with st.expander("Show Config File:", expanded=False):
            st.write(config)

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
                    run_hl_actions(config)
                except Exception as e:
                    st.error(f"実行エラー: {str(e)}")
                    time.sleep(3)
                finally:
                    st.session_state.hl_running = False
                    time.sleep(1)
                    st.rerun()

    def hl_runner_viewer(self):
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
