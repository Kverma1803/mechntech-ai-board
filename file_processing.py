import base64
import fitz
import docx
import pandas as pd
import io

def process_uploaded_files(uploaded_files):
    text_content = ""
    images_base64 = []

    for file in uploaded_files:
        ext = file.name.split('.')[-1].lower()
        if ext == 'pdf':
            try:
                doc = fitz.open(stream=file.read(), filetype="pdf")
                text_content += f"\n--- PDF: {file.name} ---\n"
                for page in doc:
                    text_content += page.get_text() + "\n"
            except Exception as e:
                text_content += f"\n[Error reading PDF {file.name}: {e}]\n"
        elif ext in ['docx', 'doc']:
            try:
                doc = docx.Document(io.BytesIO(file.read()))
                text_content += f"\n--- DOCX: {file.name} ---\n"
                for p in doc.paragraphs:
                    text_content += p.text + "\n"
            except:
                pass
        elif ext in ['csv']:
            try:
                df = pd.read_csv(file)
                text_content += f"\n--- CSV: {file.name} ---\n"
                text_content += df.to_string() + "\n"
            except:
                pass
        elif ext in ['xlsx', 'xls']:
            try:
                df = pd.read_excel(file)
                text_content += f"\n--- EXCEL: {file.name} ---\n"
                text_content += df.to_string() + "\n"
            except:
                pass
        elif ext in ['png', 'jpg', 'jpeg']:
            try:
                b64 = base64.b64encode(file.read()).decode('utf-8')
                images_base64.append(b64)
            except:
                pass
        elif ext == 'txt':
            try:
                text_content += f"\n--- TXT: {file.name} ---\n"
                text_content += file.read().decode('utf-8') + "\n"
            except:
                pass
    return text_content, images_base64
