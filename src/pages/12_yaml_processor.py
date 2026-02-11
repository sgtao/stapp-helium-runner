# yaml_processor.py
import streamlit as st
import pandas as pd
from logic.yaml_handler import YamlParser
from logic.processor import DataProcessingUseCase


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
            processor = DataProcessingUseCase()
            page_data = processor.execute(raw_data)

            # --- 4.2 プレビュー表示 (F-31) ---
            st.header(f"📊 Summary: {page_data.title}")
            col1, col2 = st.columns(2)
            col1.metric("Base URL", page_data.base_url)
            col2.metric("Unique Links", page_data.unique_links_count)

            # データフレームで詳細表示
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
            st.subheader("Link Analysis")
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
                "Download Markdown (.md)", md_content, file_name="export.md"
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
