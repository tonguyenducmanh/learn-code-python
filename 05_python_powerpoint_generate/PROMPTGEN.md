Triển khai dịch vụ AI API

API tạo slie (PPTX) theo chủ đề yêu cầu

Input: Yêu cầu + Tài liệu (nếu có)

Output: File PPTX phân tích dựa trên Yêu cầu và Tài liệu

Gợi ý:

B1: Dựng API nhận vào là yêu cầu của người sử dụng và Tài liệu
B2: Chuyển đổi tài liệu thành Text, để làm Context mô tả cho LLM (Nếu có file upload tài liệu)
B3: Viết prompt để phân tích chủ đề, đưa ra outline và cho phép người dùng sửa.
B4: Từ outline, sinh ra Slide
Gợi ý thư viện PHTHON-PPTX.
Nếu tích hợp API sinh ảnh là điểm cộng.


Yêu cầu:
tạo 1 file dùng chung là generate_pptx.py để tạo file powerpoint, tạo 1 file là api.py dùng FastAPI và 1 file là app.py dùng Streamlist

trong api thì cung cấp 2 tham số là nội dung file (optional) và nội dung prompt mong muốn sinh slide

kết quả trả về phải có cả file slide và nội dung prompt để sinh từng file slide riêng

tham khảo đoạn code đã gen được theo yêu cầu review cv bên dưới

review_cv.py
```
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

```

api.py

```
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
import tempfile
from review_cv import extract_text_from_pdf, analyze_cv

app = FastAPI()

@app.post("/review_cv")
async def review_cv_endpoint(file: UploadFile, job_description: str = Form(...)):
    """
    API nhận CV (PDF) và tin tuyển dụng, trả về đánh giá
    """
    # Lưu file tạm
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Trích xuất text từ CV
    cv_text = extract_text_from_pdf(tmp_path)

    # Gọi hàm phân tích
    result = analyze_cv(cv_text, job_description)

    return JSONResponse({"result": result})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
```

app.py
```
import streamlit as st
import requests

st.title("📄 Đánh giá độ phù hợp CV với tin tuyển dụng")

job_description = st.text_area("Nhập nội dung tin tuyển dụng:", height=200)
uploaded_file = st.file_uploader("Tải lên CV (PDF):", type=["pdf"])

if st.button("Đánh giá CV"):
    if not job_description.strip():
        st.warning("Vui lòng nhập nội dung tin tuyển dụng!")
    elif not uploaded_file:
        st.warning("Vui lòng tải lên CV!")
    else:
        with st.spinner("Đang phân tích CV..."):
            files = {"file": uploaded_file}
            data = {"job_description": job_description}
            response = requests.post("http://localhost:8000/review_cv", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json().get("result", "")
                st.subheader("🔍 Kết quả đánh giá:")
                st.markdown(result)
            else:
                st.error("Đã xảy ra lỗi khi phân tích CV.")
```