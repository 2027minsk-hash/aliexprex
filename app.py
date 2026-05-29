import streamlit as st
import subprocess
import os

# Автоматическая установка браузеров Playwright при первом запуске
if not os.path.exists("/home/appuser/.cache/ms-playwright"):
    st.write("Первая настройка: скачиваю браузер...")
    subprocess.run(["playwright", "install", "chromium"])
    st.experimental_rerun()

import google.generativeai as genai
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# ... (далее ваш остальной код с настройкой genai и анализом) ...

import streamlit as st
import google.generativeai as genai
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Укажите ваш ключ прямо здесь в кавычках, если не используете Secrets
api_key = "AQ.Ab8RN6I8ey6QZtk3gBWdvAaV7O0kJHb7KrWQRvx0F5C-4zq5fQ"

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

st.title("Анализатор отзывов AliExpress")
url = st.text_input("Введите ссылку на товар:")

if st.button("Анализировать"):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(5000) 
            content = page.content()
            browser.close()
            
        soup = BeautifulSoup(content, 'html.parser')
        texts = [t.text for t in soup.select('.review-content, .common-text')]
        
        if not texts:
            st.error("Отзывы не найдены. Попробуйте другую ссылку.")
        else:
            full_text = "\n".join(texts[:15])
            response = model.generate_content(f"Проанализируй отзывы и выдели конкретные жалобы: {full_text}")
            st.write(response.text)
    except Exception as e:
        st.error(f"Ошибка: {e}")
