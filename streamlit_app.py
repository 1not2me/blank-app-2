import os
import openai
import PyPDF2
import requests
from bs4 import BeautifulSoup
import streamlit as st
from dotenv import load_dotenv

# טעינת מפתח API מקובץ .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# חילוץ טקסט מקובץ PDF
def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"שגיאה בקריאת PDF: {e}"

# חילוץ טקסט מ-URL
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        return "\n".join([p.get_text() for p in paragraphs])
    except Exception as e:
        return f"שגיאה בטעינת דף האינטרנט: {e}"

# סיכום טקסט עם OpenAI ChatCompletion
def summarize_text(text, summary_length="קצר", max_tokens=150):
    prompt = f"תמצת את הטקסט הבא בצורה {summary_length}:\n\n{text}"
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "אתה עוזר חכם שמסכם טקסטים בעברית"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"שגיאה בסיכום הטקסט: {e}"

# ממשק Streamlit
def main():
    st.title("📄 מערכת לסיכום מסמכים")
    st.markdown("בחר מקור קלט: העלאת קובץ או הזנת כתובת אינטרנט")

    source_option = st.radio("בחר מקור:", ("קובץ", "URL"))

    text = ""
    if source_option == "קובץ":
        uploaded_file = st.file_uploader("העלה קובץ PDF או TXT", type=["pdf", "txt"])
        if uploaded_file:
            if uploaded_file.name.endswith(".pdf"):
                text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.name.endswith(".txt"):
                text = uploaded_file.read().decode("utf-8")
            else:
                st.error("פורמט לא נתמך. נא לבחור PDF או TXT.")
    else:
        url = st.text_input("הזן URL:")
        if url:
            text = extract_text_from_url(url)

    if text:
        with st.expander("📘 טקסט שחולץ"):
            st.text_area("תוכן:", text, height=300)

        summary_length = st.selectbox("בחר אורך סיכום:", ["קצר", "בינוני", "מפורט"])
        if st.button("✏️ צור סיכום"):
            tokens = {"קצר": 500, "בינוני": 1500, "מפורט": 5000}.get(summary_length, 150)
            summary = summarize_text(text, summary_length=summary_length, max_tokens=tokens)
            st.subheader("📌 סיכום:")
            st.write(summary)

if __name__ == "__main__":
    main()
