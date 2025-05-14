import os
import streamlit as st
import PyPDF2
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai

# טען את מפתח ה־API מקובץ הסביבה
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# הגדרת המודל של Gemini
model = genai.GenerativeModel('gemini-pro')

# חילוץ טקסט מ־PDF
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# חילוץ טקסט מקישור
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        return "\n".join([p.get_text() for p in paragraphs])
    except Exception as e:
        return f"שגיאה: {e}"

# סיכום טקסט בעזרת Gemini
def summarize_text_with_gemini(text, length="קצר"):
    prompt = f"תמצת את הטקסט הבא בצורה {length}:\n\n{text}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"שגיאה בסיכום: {e}"

# ממשק המשתמש
def main():
    st.title("📄 מסכם טקסטים מבוסס Gemini")
    st.markdown("בחר מקור קלט (PDF, TXT, או URL):")

    source = st.radio("מקור הטקסט:", ["קובץ", "קישור"])

    text = ""
    if source == "קובץ":
        uploaded_file = st.file_uploader("העלה קובץ PDF או TXT", type=["pdf", "txt"])
        if uploaded_file:
            if uploaded_file.name.endswith(".pdf"):
                text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.name.endswith(".txt"):
                text = uploaded_file.read().decode("utf-8")
            else:
                st.error("פורמט קובץ לא נתמך.")

    elif source == "קישור":
        url = st.text_input("הכנס כתובת אתר:")
        if url:
            text = extract_text_from_url(url)

    if text:
        st.subheader("📘 טקסט שחולץ (תצוגה מקדימה):")
        st.text_area("תוכן", value=text[:1000], height=200)

        summary_length = st.selectbox("בחר אורך סיכום:", ["קצר", "בינוני", "מפורט"])
        if st.button("✏️ צור סיכום"):
            summary = summarize_text_with_gemini(text, length=summary_length)
            st.subheader("📌 סיכום:")
            st.write(summary)

if __name__ == "__main__":
    main()
