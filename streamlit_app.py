import os
import streamlit as st
import requests
import PyPDF2
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai

# טען משתנים מהסביבה
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# פונקציה לחילוץ טקסט מקובץ PDF
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# פונקציה לחילוץ טקסט מדף אינטרנט
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        return "\n".join([p.get_text() for p in paragraphs])
    except Exception as e:
        return f"שגיאה: {e}"

# פונקציית סיכום עם Gemini
def summarize_text_with_gemini(text, length="קצר"):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"סכם את הטקסט הבא בצורה {length}:\n\n{text}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"שגיאה בסיכום: {e}"

# ממשק Streamlit
def main():
    st.title("🧠 אפליקציה לחילוץ וסיכום מסמכים")

    source_type = st.radio("בחר מקור תוכן:", ["קובץ PDF", "כתובת URL"])
    
    text = ""
    if source_type == "קובץ PDF":
        uploaded_file = st.file_uploader("העלה קובץ PDF", type=["pdf"])
        if uploaded_file is not None:
            text = extract_text_from_pdf(uploaded_file)
    else:
        url = st.text_input("הכנס כתובת אינטרנט")
        if url:
            text = extract_text_from_url(url)
    
    if text:
        st.subheader("📄 הטקסט שחולץ:")
        st.text(text[:1000] + "..." if len(text) > 1000 else text)

        summary_style = st.selectbox("בחר סגנון סיכום:", ["קצר", "בינוני", "מפורט"])
        if st.button("📋 צור סיכום"):
            with st.spinner("יוצר סיכום..."):
                summary = summarize_text_with_gemini(text, length=summary_style)
                st.subheader("✍️ סיכום:")
                st.write(summary)

if __name__ == "__main__":
    main()
