import streamlit as st
import google.generativeai as genai
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

# Настройка Gemini API
genai.configure(api_key="ВАШ_API_КЛЮЧ_ОТ_GOOGLE_AI_STUDIO")
model = genai.GenerativeModel('gemini-1.5-flash')
genai.configure(api_key="AQ.Ab8RN6I8ey6QZtk3gBWdvAaV7O0kJHb7KrWQRvx0F5C-4zq5fQ")
st.title("Анализатор отзывов AliExpress")
url = st.text_input("Введите ссылку на товар AliExpress:")

def fetch_reviews_with_playwright(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            
            # Ждем прогрузки отзывов (прокрутка вниз может потребоваться)
            page.mouse.wheel(0, 5000)
            time.sleep(5) 
            
            content = page.content()
            browser.close()
            
            soup = BeautifulSoup(content, 'html.parser')
            # Класс 'review-text' может отличаться, это пример для структуры Ali
            reviews = [tag.text for tag in soup.select('.review-text')]
            return reviews
    except Exception as e:
        return f"Ошибка при загрузке: {e}"

if st.button("Анализировать"):
    if not url:
        st.error("Пожалуйста, введите ссылку!")
    else:
        with st.spinner('Загружаю отзывы и анализирую...'):
            reviews = fetch_reviews_with_playwright(url)
            
            if not reviews or isinstance(reviews, str):
                st.error("Не удалось найти отзывы. Попробуйте другую ссылку.")
            else:
                full_text = "\n".join(reviews[:30]) # Берем первые 30 отзывов для экономии токенов
                
                prompt = f"""
                Проанализируй отзывы о товаре с AliExpress.
                Твоя задача: найти конкретные "боли" клиентов.
                Пример плохого ответа: "плохое качество".
                Пример хорошего ответа: "молния сломалась через 3 недели", "размер маломерит на 2 размера".
                
                Отзывы для анализа:
                {full_text}
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.success("Анализ завершен:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Ошибка при обращении к ИИ: {e}")
