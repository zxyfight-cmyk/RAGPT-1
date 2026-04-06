import os
from docx import Document
from PyPDF2 import PdfReader

def load_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def load_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join([page.extract_text() for page in reader.pages])

def load_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def load_all_documents(folder_path):
    docs = {}
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith(".docx"):
            docs[file_path] = load_docx(file_path)
        elif filename.endswith(".pdf"):
            docs[file_path] = load_pdf(file_path)
        elif filename.endswith(".txt") or filename.endswith(".md"):
            docs[file_path] = load_txt(file_path)
    return docs