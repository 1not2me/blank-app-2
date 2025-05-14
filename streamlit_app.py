import os
import openai
import PyPDF2
import requests
from bs4 import BeautifulSoup
import streamlit as st
from dotenv import load_dotenv

# טען משתני סביבה
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# חילוץ טקסט מקובץ PDF
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# חילוץ טקסט מקישור URL
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        return "\n".join([p.get_text() for p in paragraphs])
    except Exception as e:
        return f"שגיאה: {e}"

# סיכום טקסט באמצעות OpenAI
def summarize_text(text, summary_length="קצר", max_tokens=150):
    prompt = f"תמצת את הטקסט הבא בצורה {summary_length}:\n\n{text}"
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"שגיאה בסיכום הטקסט: {e}"

# ממשק ראשי עם Streamlit
def main():
    st.title("מערכת לסיכום מסמכים ושאלות")
    st.markdown("העלה קובץ PDF / טקסט או הזן כתובת URL לחילוץ וסיכום תוכן")

    source_option = st.radio("בחר מקור קלט:", ("קובץ", "URL"))

    text = ""
    if source_option == "קובץ":
        uploaded_file = st.file_uploader("העלה קובץ PDF או TXT", type=["pdf", "txt"])
        if uploaded_file:
            if uploaded_file.name.endswith(".pdf"):
                text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.name.endswith(".txt"):
                text = uploaded_file.read().decode("utf-8")
            else:
                st.error("פורמט קובץ לא נתמך.")
    else:
        url = st.text_input("הזן קישור URL")
        if url:
            text = extract_text_from_url(url)

    if text:
        with st.expander("הצג טקסט מלא"):
            st.text_area("טקסט שחולץ", text, height=300)

        summary_length = st.selectbox("בחר אורך סיכום", ["קצר", "בינוני", "מפורט"])
        if st.button("צור סיכום"):
            if summary_length == "קצר":
                tokens = 150
            elif summary_length == "בינוני":
                tokens = 300
            else:
                tokens = 500
            summary = summarize_text(text, summary_length=summary_length, max_tokens=tokens)
            st.subheader("🔎 סיכום המסמך:")
            st.write(summary)

if __name__ == "__main__":
    main()
