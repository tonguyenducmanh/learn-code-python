
import io
import json
import os
import tempfile
import base64
from typing import Optional, Dict, Any

from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI

from generate_pptx import create_presentation_from_spec
from utils_text import extract_text_any

app = FastAPI(title="AI Slide Designer API", version="1.0.0")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
client = OpenAI()

def build_spec_prompt(user_prompt: str, context_text: str, max_slides: int, seed: Optional[int]) -> str:
    seed_hint = "" if seed is None else f"(Ưu tiên tính ngẫu nhiên có kiểm soát với seed={seed})."
    return f"""
Bạn là chuyên gia thiết kế thuyết trình và narration cho slide PowerPoint.
Nhiệm vụ: từ yêu cầu của người dùng và (nếu có) tài liệu tham chiếu, hãy tạo **JSON** mô tả *toàn bộ* deck với **mỗi slide có layout & style khác nhau** (không dùng 1 theme cố định).

Yêu cầu bắt buộc:
- Mỗi slide phải chỉ rõ: title, bullets/nội dung có cấu trúc, speaker_notes (ghi chú thuyết trình), và style riêng.
- Style bao gồm: background_color (hex), title_color (hex), text_color (hex), font_family (gợi ý phổ biến: Arial/Calibri/Roboto/Georgia/Helvetica), layout (một trong: "title_only", "title_content", "image_left_text_right", "text_left_image_right", "quote", "two_columns", "comparison", "timeline", "big_number", "chart_focus").
- Nếu phù hợp, đề xuất: has_image (true/false) + image_keyword (từ khoá ảnh minh hoạ), hoặc has_chart/has_table (true/false) cùng data/suggested_chart.
- Mỗi slide nên có style khác nhau (màu, layout, hoặc font) để tạo cảm giác đa dạng nhưng vẫn chuyên nghiệp.
- Tổng số slide tối đa: {max_slides}. {seed_hint}

Ngữ cảnh tài liệu (nếu có, tóm tắt gọn): 
\"\"\"
{context_text[:4000]}
\"\"\"

Yêu cầu người dùng:
\"\"\"
{user_prompt}
\"\"\"

Trả về **JSON hợp lệ** đúng định dạng sau, không kèm văn bản nào khác ngoài JSON:
{{
  "title": "Tiêu đề deck",
  "slides": [
    {{
      "title": "Tiêu đề slide",
      "bullets": ["gạch đầu dòng 1", "gạch đầu dòng 2"],
      "speaker_notes": "ghi chú trình bày ngắn gọn",
      "style": {{
        "layout": "image_left_text_right",
        "background_color": "#F0F8FF",
        "title_color": "#003366",
        "text_color": "#1A1A1A",
        "font_family": "Calibri",
        "has_image": true,
        "image_keyword": "teamwork",
        "has_chart": false,
        "has_table": false
      }}
    }}
  ]
}}
    """.strip()

@app.post("/generate_slides")
async def generate_slides(
    user_prompt: str = Form(...),
    max_slides: int = Form(12),
    seed: int = Form(-1),
    file: UploadFile | None = None
):
    # 1) Extract context text if file uploaded
    context_text = ""
    if file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        try:
            context_text = extract_text_any(tmp_path)
        except Exception as e:
            context_text = f"(Không đọc được file: {e})"

    # 2) Build prompt
    seed_val = None if seed == -1 else seed
    prompt = build_spec_prompt(user_prompt, context_text, int(max_slides), seed_val)

    # 3) Call LLM to get JSON spec
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": "Bạn là chuyên gia thiết kế slide và PowerPoint, trả lời CHỈ BẰNG JSON hợp lệ."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9 if seed_val is None else 0.7,
    )
    output_text = response.output_text

    # Try to parse JSON
    try:
        spec = json.loads(output_text)
    except Exception:
        # Try to recover JSON block
        import re
        m = re.search(r"\{.*\}", output_text, re.DOTALL)
        if not m:
            return JSONResponse({"error": "LLM không trả về JSON hợp lệ", "raw": output_text}, status_code=500)
        try:
            spec = json.loads(m.group(0))
        except Exception as e:
            return JSONResponse({"error": f"Lỗi parse JSON: {e}", "raw": output_text}, status_code=500)

    # 4) Create PPTX from spec
    try:
        pptx_bytes, filename = create_presentation_from_spec(spec, seed=seed_val)
        pptx_b64 = base64.b64encode(pptx_bytes).decode("utf-8")
    except Exception as e:
        return JSONResponse({"error": f"Lỗi tạo PPTX: {e}"}, status_code=500)

    return JSONResponse({
        "filename": filename,
        "spec": spec,
        "pptx_base64": pptx_b64
    })
