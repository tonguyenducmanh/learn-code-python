import pymupdf  # Thay cho fitz
from openai import OpenAI

# Khởi tạo OpenAI Client
client = OpenAI(api_key="...")  # Thay bằng API key thực tế


def extract_text_from_pdf(file_path: str) -> str:
    """Đọc file PDF và trả về nội dung text"""
    text = ""
    # Mở file PDF
    pdf_document = pymupdf.open(file_path)
    for page in pdf_document:
        text += page.get_text("text")  # Lấy text ở chế độ "text"
    pdf_document.close()
    return text.strip()

def analyze_cv(cv_text: str, job_description: str) -> str:
    """
    Gửi CV và tin tuyển dụng đến LLM để đánh giá độ phù hợp
    """
    prompt = f"""
Bạn là chuyên gia tuyển dụng.
Hãy đánh giá mức độ phù hợp của ứng viên dựa trên CV dưới đây so với tin tuyển dụng.

Tin tuyển dụng:
{job_description}

CV Ứng viên:
{cv_text}

Hãy trả về:
- Đánh giá tổng quan (1-100 điểm)
- Điểm mạnh của ứng viên
- Điểm cần cải thiện
- Tóm tắt ngắn gọn

Trả lời chi tiết bằng tiếng Việt.
"""
    response = client.responses.create(
        model="gpt-4.1",
        input=[{"role": "system", "content": "Bạn là chuyên gia phân tích CV và tuyển dụng."},
               {"role": "user", "content": prompt}]
    )

    return response.output_text
