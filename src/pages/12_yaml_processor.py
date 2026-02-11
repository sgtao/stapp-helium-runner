# yaml_processor.py
import streamlit as st
import pandas as pd
import yaml

import jmespath

from logic.yaml_handler import YamlParser
from logic.processor import DataProcessingUseCase


def extract_top_props_keys(raw_data: dict, top_props: str = ".") -> list[str]:
    return [
        f"{top_props}.{item["key"]}"
        for item in raw_data.get(top_props, [])
        if "key" in item
    ]


def build_property_options(raw_data: dict):
    options = {
        "Whole": ".",
        "hl_runner(Whole)": "hl_runner",
    }

    if "hl_runner" in raw_data:
        for item in raw_data["hl_runner"]:
            key = item.get("key")
            if key:
                options[f"hl_runner.{key}"] = (
                    f"hl_runner[?key=='{key}'].value | [0]"
                )
    return options


def extract_property_from_data(raw_data: dict, property_path: str):
    if property_path == ".":
        return raw_data
    # ".hl_runner.body" → "hl_runner[?key=='body'].value | [0]"
    query = property_path.lstrip(".")
    return jmespath.search(query, raw_data)


def main():
    st.set_page_config(page_title="YAML Data Extractor", layout="wide")
    st.title("📄 YAML Data Extractor & Processor")

    uploaded_file = st.file_uploader(
        "YAMLファイルをアップロードしてください", type=["yaml", "yml"]
    )

    if uploaded_file:
        try:
            # Infrastructure & UseCase の実行
            raw_data = YamlParser.parse(uploaded_file)

            # keys = [".", "hl_runner"]
            # keys += extract_top_props_keys(raw_data, "hl_runner")
            options = build_property_options(raw_data)

            # selected_key = st.selectbox(
            label = st.selectbox("🔍 抽出対象を選択してください", options)
            query = options[label]

            raw_data = extract_property_from_data(raw_data, query)

            # --- YAML全体表示 ---
            with st.expander("📂 Uploaded YAML (raw view)", expanded=False):
                st.code(
                    yaml.dump(raw_data, allow_unicode=True), language="yaml"
                )

            processor = DataProcessingUseCase()
            page_data = processor.execute(raw_data)

            # --- 4.2 プレビュー表示 (F-31) ---
            st.subheader(f"📊 Title: {page_data.title}")
            col1, col2 = st.columns(2)
            col1.metric("Base URL", page_data.base_url)
            col2.metric("Unique Links", page_data.unique_links_count)

            # --- Tabs ---
            tab_contents, tab_links = st.tabs(
                ["📄 Contents", "🔗 Link Analysis"]
            )
            df_links = pd.DataFrame(
                [
                    {
                        "Text": link.text,
                        "Original": link.original_url,
                        "Absolute": link.absolute_url,
                    }
                    for link in page_data.links
                ]
            )

            with tab_contents:
                st.subheader("📄 Contents")

                content = page_data.content

                if not content:
                    st.info("No content available.")
                else:
                    # list / dict / str を安全に文字列化
                    if isinstance(content, (list, dict)):
                        content_text = yaml.dump(
                            content,
                            allow_unicode=True,
                            default_flow_style=False,
                        )
                    else:
                        content_text = str(content)

                    # エスケープ文字を実体化
                    content_text = (
                        content_text.replace("\\r\\n", "\n")
                        .replace("\\n", "\n")
                        .replace("\\t", "\t")
                    )

                    st.code(content_text, language="html")

            with tab_links:
                # データフレームで詳細表示
                st.subheader("🔗 Link Analysis")

                if df_links.empty:
                    st.info("No links detected.")
                else:
                    st.dataframe(df_links, width="content")

                # --- 4.2 出力機能 (F-20, F-21) ---
                st.divider()
                c1, c2 = st.columns(2)

                # Markdown生成
                md_content = f"""
                # {page_data.title}\n\n
                - **Base URL:** {page_data.base_url}\n\n
                ## Links\n"""
                md_content += "\n".join(
                    [
                        f"- [{link.text}]({link.absolute_url})"
                        for link in page_data.links
                    ]
                )

                c1.download_button(
                    "Download Markdown (.md)",
                    md_content,
                    file_name="export.md",
                )

                # URLリスト生成
                url_list = "\n".join(
                    [
                        link.absolute_url
                        for link in page_data.links
                        if link.absolute_url
                    ]
                )
                c2.download_button(
                    "Download URL List (.txt)", url_list, file_name="urls.txt"
                )

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
