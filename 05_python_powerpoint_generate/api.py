import tempfile
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import Response
from generate_pptx import generate_pptx_from_request, pack_zip_with_prompts

app = FastAPI(title="AI Slide Generator API")


@app.post("/generate_pptx")
async def generate_pptx_endpoint(
    prompt: str = Form(..., description="Nội dung yêu cầu sinh slide"),
    file: UploadFile | None = File(None, description="Tài liệu tham chiếu (optional)"),
    max_slides: int = Form(8),
):
    """
    Nhận prompt + file (optional) -> trả về ZIP gồm:
      - slides.pptx
      - outline.md
      - prompts.json
      - meta.json
    """
    temp_path = None
    if file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename[file.filename.rfind("."):]) as tmp:
            tmp.write(await file.read())
            temp_path = tmp.name

    pptx_path, outline, refined = generate_pptx_from_request(
        user_prompt=prompt,
        context_file_path=temp_path,
        max_slides=max_slides,
    )

    zip_bytes = pack_zip_with_prompts(pptx_path, outline, refined)
    headers = {
        "Content-Disposition": 'attachment; filename="slides_bundle.zip"'
    }
    return Response(content=zip_bytes, media_type="application/zip", headers=headers)


# tuỳ chọn: healthcheck
@app.get("/healthz")
def healthz():
    return {"ok": True}
