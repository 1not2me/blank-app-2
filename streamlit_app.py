import os
import re
from dotenv import load_dotenv
import PyPDF2
import requests
from bs4 import BeautifulSoup
import openai

# טען את מפתח ה־API
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ניקוי טקסט
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # רווחים מרובים
    text = re.sub(r'\n+', '\n', text)  # שורות ריקות
    return text.strip()

# חילוץ טקסט מ־PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except FileNotFoundError:
        return "שגיאה: קובץ PDF לא נמצא."
    except Exception as e:
        return f"שגיאה בעיבוד PDF: {e}"
    return clean_text(text)

# חילוץ טקסט מ־URL
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = '\n'.join([p.get_text() for p in paragraphs])
        return clean_text(text)
    except requests.exceptions.RequestException as e:
        return f"שגיאה בהבאת URL: {e}"
    except Exception as e:
        return f"שגיאה בעיבוד דף אינטרנט: {e}"

# סיכום טקסט עם OpenAI
def summarize_text(text, summary_length="קצר", max_tokens=150):
    prompt = f"תמצת את הטקסט הבא בצורה {summary_length}:\n\n{text}"
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"שגיאה בשירות OpenAI: {e}"

# מענה לשאלה על פי הטקסט
def answer_question(text, question):
    prompt = f"בהתבסס על הטקסט הבא:\n{text}\n\nענה על השאלה:\n{question}\nתשובה:"
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=200,
            temperature=0.5,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"שגיאה במענה על שאלה: {e}"

# פונקציית ההפעלה הראשית
def main():
    source_type = input("הזן 'file' כדי להעלות קובץ או 'url' עבור כתובת אינטרנט: ").lower()

    text = ""
    if source_type == 'file':
        file_path = input("הזן את נתיב הקובץ (PDF או TXT): ")
        if file_path.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    text = clean_text(text)
            except Exception as e:
                text = f"שגיאה בקריאת קובץ TXT: {e}"
        else:
            print("פורמט קובץ לא נתמך.")
            return
    elif source_type == 'url':
        url = input("הזן את כתובת האתר: ")
        text = extract_text_from_url(url)
    else:
        print("קלט לא חוקי.")
        return

    if text.startswith("שגיאה"):
        print(text)
        return

    print("\n📄 חלק מהטקסט שחולץ:\n")
    print(text[:500] + "..." if len(text) > 500 else text)

    summary_length = input("\nהזן את אורך הסיכום הרצוי (קצר/בינוני/מפורט): ").lower()
    max_tokens = {"קצר": 150, "בינוני": 300, "מפורט": 500}.get(summary_length, 150)

    summary = summarize_text(text, summary_length=summary_length, max_tokens=max_tokens)
    print("\n📝 סיכום:\n")
    print(summary)

    ask = input("\nרוצה לשאול שאלה על המסמך? (y/n): ").lower()
    if ask == "y":
        question = input("הקלד את השאלה שלך: ")
        answer = answer_question(text, question)
        print("\n🤖 תשובה לשאלה:\n")
        print(answer)

if __name__ == "__main__":
    main()
