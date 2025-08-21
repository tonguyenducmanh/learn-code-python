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
