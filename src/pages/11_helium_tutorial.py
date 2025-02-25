# 11_helium_tutorial.py
import os

from helium import start_chrome, write, press, ENTER, kill_browser
import streamlit as st

# ChromeDriverのパスを設定（必要に応じて変更）
os.environ["PATH"] += os.pathsep + "/chrome-driver"

# from functions.calculations import calculate_spiral
# from components.spiral_chart import spiral_chart

# # メインページに移動
# st.page_link("main.py", label="Go to Main", icon="🏠")

st.title("helium_tutorial")

"""
trial helium:
https://github.com/mherrmann/helium/blob/master/docs/cheatsheet.md#interacting-with-a-web-site
```py
from helium import *
start_chrome('google.com')
write('helium selenium github')
press(ENTER)
kill_browser()
```
"""

if st.button("Start Helium"):
    try:
        # Chromeを起動
        start_chrome("google.com")
        # Heliumを使って操作
        write("helium selenium github")
        press(ENTER)
        kill_browser()

    except Exception as e:
        st.error(f"An error occurred: {e}")
