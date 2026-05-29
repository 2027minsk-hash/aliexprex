import streamlit as st
import google.generativeai as genai
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Используем секреты, если они есть, или вставьте ключ сюда в кавычках
api_key = st.secrets.get("GOOGLE_API_KEY", "ВАШ_API_КЛЮЧ_ОТ_GOOGLE_AI_STUDIO")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
genai.configure(api_key="AQ.Ab8RN6I8ey6QZtk3gBWdvAaV7O0kJHb7KrWQRvx0F5C-4zq5fQ")
st.title("Анализатор отзывов AliExpress")
url = st.text_input("Введите ссылку на товар AliExpress:")

def fetch_reviews(url):
    try:
        with sync_playwright() as p:
            # Запускаем браузер с имитацией реального пользователя
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
            page = context.new_page()
            
            page.goto(url, wait_until="networkidle")
            
            # Прокрутка до блока отзывов
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(5000) # Ждем, пока JS подгрузит контент
            
            content = page.content()
            browser.close()
            
            soup = BeautifulSoup(content, 'html.parser')
            # Ищем текст отзывов (класс может меняться, пробую универсальный поиск)
            # Обычно на Ali это элементы внутри списка отзывов
            reviews = [t.get_text() for t in soup.find_all(class_=['review-content', 'common-text'])]
            return reviews
    except Exception as e:
        return str(e)

if st.button("Анализировать"):
    if not url:
        st.warning("Введите ссылку!")
    else:
        with st.spinner('Анализирую отзывы (это может занять до 15 сек)...'):
            reviews = fetch_reviews(url)
            
            if not reviews:
                st.error("Отзывы не найдены. Попробуйте другой товар (на некоторых товарах отзывы скрыты).")
            else:
                full_text = "\n".join(reviews[:20])
                prompt = f"Проанализируй отзывы: {full_text}. Выдели конкретные жалобы (боли) клиентов, например: 'швы расходятся через неделю'."
                
                try:
                    response = model.generate_content(prompt)
                    st.write("### Результат:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Ошибка ИИ: {e}")
