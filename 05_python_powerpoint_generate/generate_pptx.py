import os
import io
import json
import tempfile
from typing import List, Dict, Optional, Tuple

import pymupdf  # PyMuPDF
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

from openai import OpenAI


# ========== LLM CLIENT ==========
def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY env var")
    return OpenAI(api_key=api_key)


# ========== FILE ➜ TEXT ==========
def extract_text_from_pdf(file_path: str) -> str:
    text = []
    doc = pymupdf.open(file_path)
    try:
        for page in doc:
            text.append(page.get_text("plain"))
    finally:
        doc.close()
    return "\n".join(text).strip()


def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()


def extract_text_from_file(file_path: str) -> str:
    """
    Hỗ trợ nhanh: PDF / TXT. (Có thể mở rộng DOCX sau)
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    if ext in (".txt", ".md"):
        return extract_text_from_txt(file_path)
    # fallback: chưa hỗ trợ -> trả rỗng
    return ""


# ========== PROMPTING ==========
OUTLINE_SYSTEM = (
    "Bạn là chuyên gia trình bày và soạn slide. "
    "Hãy tạo dàn ý slide súc tích, logic, dễ trình bày."
)

OUTLINE_USER_TMPL = """
Yêu cầu người dùng:
{user_prompt}

Ngữ cảnh/tài liệu (nếu có):
{context}

Yêu cầu đầu ra (JSON hợp lệ):
{{
  "title": "Tiêu đề tổng",
  "slides": [
    {{
      "title": "Tiêu đề slide",
      "bullets": ["gạch đầu dòng 1", "gạch đầu dòng 2", "..."],
      "image_prompt": "mô tả ảnh minh họa (tuỳ chọn, có thể để trống)"
    }}
  ],
  "notes": "ghi chú thuyết trình tổng quát (optional)"
}}

Ràng buộc:
- Tối đa {max_slides} slide nội dung (không tính trang bìa nếu bạn muốn thêm).
- Ngắn gọn, thực tiễn, ưu tiên bullet thay vì văn dài.
- Luôn trả về JSON hợp lệ, KHÔNG kèm giải thích.
"""

def llm_generate_outline(user_prompt: str, context: str, max_slides: int = 10, model: str = "gpt-4.1") -> Dict:
    client = get_openai_client()
    user = OUTLINE_USER_TMPL.format(user_prompt=user_prompt, context=context or "(Không có)", max_slides=max_slides)
    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": OUTLINE_SYSTEM},
            {"role": "user", "content": user}
        ],
        temperature=0.4,
    )
    text = resp.output_text
    # Thử parse JSON
    try:
        data = json.loads(text)
    except Exception:
        # Nếu model trả kèm text khác, tìm khối JSON
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            data = json.loads(text[start:end+1])
        else:
            raise ValueError("LLM không trả về JSON hợp lệ:\n" + text)
    return data


SLIDE_PROMPT_SYSTEM = (
    "Bạn là trợ lý tạo nội dung slide. "
    "Với mỗi slide, hãy tối ưu tiêu đề và bullets ngắn gọn, súc tích."
)

SLIDE_PROMPT_USER_TMPL = """
Dựa trên dàn ý và ngữ cảnh sau, hãy tinh chỉnh nội dung CHO TỪNG SLIDE.

Dàn ý đầu vào (JSON):
{outline_json}

Ràng buộc:
- Trả về JSON với mảng `slides`, mỗi phần tử:
  {{
    "title": "...",
    "bullets": ["...", "...", "..."],
    "speaker_notes": "ghi chú thuyết trình ngắn (optional)",
    "image_prompt": "mô tả ảnh minh hoạ (optional)"
  }}
- Giữ cấu trúc slide tương đương đầu vào nhưng tối ưu câu chữ, ưu tiên tính hành động, số liệu (nếu có).
- KHÔNG trả lời gì khác ngoài JSON hợp lệ.
"""

def llm_refine_slides(outline: Dict, model: str = "gpt-4.1-mini") -> Dict:
    client = get_openai_client()
    user = SLIDE_PROMPT_USER_TMPL.format(outline_json=json.dumps(outline, ensure_ascii=False))
    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SLIDE_PROMPT_SYSTEM},
            {"role": "user", "content": user}
        ],
        temperature=0.3,
    )
    text = resp.output_text
    try:
        data = json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            data = json.loads(text[start:end+1])
        else:
            raise ValueError("LLM không trả về JSON hợp lệ (refine):\n" + text)
    return data


# ========== OPTIONAL IMAGE GEN (stub) ==========
def generate_image(image_prompt: str) -> Optional[str]:
    """
    TODO: tích hợp API sinh ảnh nếu muốn.
    Trả về đường dẫn file ảnh tạm hoặc None. Hiện để None.
    """
    return None


# ========== RENDER PPTX ==========
def _add_title_slide(prs: Presentation, title: str, subtitle: Optional[str] = None):
    layout = prs.slide_layouts[0]  # Title Slide
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = title or "Presentation"
    if subtitle is not None:
        slide.placeholders[1].text = subtitle
    return slide

def _add_content_slide(prs: Presentation, title: str, bullets: List[str], image_path: Optional[str] = None):
    layout = prs.slide_layouts[1]  # Title and Content
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = title or ""
    tf = slide.shapes.placeholders[1].text_frame
    tf.clear()
    for i, b in enumerate(bullets or []):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = b
        p.level = 0

    # Nếu có ảnh, chèn ảnh dưới khối content
    if image_path and os.path.exists(image_path):
        # chèn ảnh với width = 5.5 inch, căn giữa
        left = Inches(1.0)
        top = Inches(4.0)
        width = Inches(8.0)
        slide.shapes.add_picture(image_path, left, top, width=width)

    return slide


def render_pptx(preset_title: str, slides_spec: List[Dict], output_path: str) -> None:
    prs = Presentation()
    # Trang bìa
    _add_title_slide(prs, title=preset_title, subtitle=None)

    for s in slides_spec:
        title = s.get("title", "")
        bullets = s.get("bullets", [])
        image_prompt = s.get("image_prompt") or ""
        image_path = None
        if image_prompt:
            image_path = generate_image(image_prompt)

        _add_content_slide(prs, title=title, bullets=bullets, image_path=image_path)

    # Tuỳ chỉnh font size nhẹ cho Title (tuỳ chọn)
    for slide in prs.slides:
        if slide.shapes.title and slide.shapes.title.has_text_frame:
            for p in slide.shapes.title.text_frame.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(36)
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(30, 30, 30)

    prs.save(output_path)


# ========== PUBLIC FACADE ==========
def generate_pptx_from_request(
    user_prompt: str,
    context_file_path: Optional[str] = None,
    max_slides: int = 8,
    outline_only: bool = False,
    model_outline: str = "gpt-4.1",
    model_refine: str = "gpt-4.1-mini",
) -> Tuple[str, Dict, Dict]:
    """
    Trả về:
      - pptx_path: đường dẫn file PPTX đã sinh
      - outline: JSON outline thô từ LLM
      - refined: JSON slides đã tinh chỉnh (dùng để render + prompts cho từng slide)
    """
    context_text = ""
    if context_file_path:
        context_text = extract_text_from_file(context_file_path)

    outline = llm_generate_outline(user_prompt, context_text, max_slides=max_slides, model=model_outline)

    if outline_only:
        refined = {"slides": outline.get("slides", [])}
    else:
        refined = llm_refine_slides(outline, model=model_refine)

    # Render pptx
    tmp_pptx = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx")
    tmp_pptx.close()
    title = outline.get("title") or "Generated Presentation"
    render_pptx(title, refined.get("slides", []), tmp_pptx.name)

    return tmp_pptx.name, outline, refined


def pack_zip_with_prompts(pptx_path: str, outline: Dict, refined: Dict) -> bytes:
    """
    Đóng gói ZIP gồm:
      - slides.pptx
      - outline.md
      - prompts.json  (danh sách prompt cho từng slide / image_prompt)
      - meta.json     (tiêu đề, số slide, ...)
    """
    import zipfile

    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as z:
        # PPTX
        z.write(pptx_path, arcname="slides.pptx")

        # Outline markdown đơn giản
        title = outline.get("title", "Presentation")
        md_lines = [f"# {title}", ""]
        for i, s in enumerate(outline.get("slides", []), 1):
            md_lines.append(f"## {i}. {s.get('title','')}")
            for b in s.get("bullets", []):
                md_lines.append(f"- {b}")
            md_lines.append("")
        z.writestr("outline.md", "\n".join(md_lines))

        # Prompts cho từng slide (đầu vào để tái sinh)
        # Ở đây mình coi 'refined' chính là đặc tả từng slide sau tinh chỉnh
        z.writestr("prompts.json", json.dumps(refined, ensure_ascii=False, indent=2))

        # Meta
        meta = {
            "title": title,
            "num_slides": len(refined.get("slides", [])),
        }
        z.writestr("meta.json", json.dumps(meta, ensure_ascii=False, indent=2))

    bio.seek(0)
    return bio.read()
