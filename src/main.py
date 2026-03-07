import streamlit as st

"""
## Welcome to helium-runner App!

Heliumライブラリでページ操作する[streamlit](https://streamlit.io/)アプリです。
"""

# Herium Runner アプリへのリンク
st.page_link(
    "pages/11_helium_runner.py", label="Go to Helium Runner App", icon="🏃"
)
# YAML Extractor アプリへのリンク
st.page_link(
    "pages/12_yaml_processor.py",
    label="Go to YAML Data Processor App",
    icon="📄",
)
# ログ表示ページへのリンク
st.page_link("pages/21_logs_viewer.py", label="View Logs", icon="📄")
