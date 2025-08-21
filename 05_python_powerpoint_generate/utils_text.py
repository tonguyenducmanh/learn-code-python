
import os, mimetypes

def extract_text_any(path: str) -> str:
    mt, _ = mimetypes.guess_type(path)
    if not mt:
        mt = ""
    if mt.endswith("pdf") or path.lower().endswith(".pdf"):
        return extract_text_pdf(path)
    if path.lower().endswith(".docx"):
        return extract_text_docx(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        with open(path, "rb") as f:
            return f.read().decode("utf-8", errors="ignore")

def extract_text_pdf(path: str) -> str:
    import pymupdf
    doc = pymupdf.open(path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    doc.close()
    return text.strip()

def extract_text_docx(path: str) -> str:
    import docx
    d = docx.Document(path)
    paras = [p.text for p in d.paragraphs if p.text.strip()]
    return "\n".join(paras).strip()
