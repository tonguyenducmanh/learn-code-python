import io
import zipfile
import streamlit as st
import requests
import json

st.set_page_config(page_title="AI Slide Generator", page_icon="📊", layout="centered")
st.title("📊 AI tạo Slide (PPTX) theo chủ đề")

with st.expander("Hướng dẫn nhanh", expanded=False):
    st.markdown(
        "- Nhập **Yêu cầu** (ví dụ: Phân tích xu hướng AI 2025 cho lãnh đạo)\n"
        "- (Tuỳ chọn) Upload **Tài liệu** PDF/TXT để làm context\n"
        "- Nhấn **Tạo slide** → Hệ thống trả về file ZIP gồm PPTX + Prompt + Outline"
    )

prompt = st.text_area("✍️ Yêu cầu slide", height=180, placeholder="Ví dụ: Giới thiệu sản phẩm X cho khách hàng doanh nghiệp...")
uploaded = st.file_uploader("📎 Tài liệu (optional)", type=["pdf", "txt", "md"])
max_slides = st.slider("Số slide nội dung tối đa", min_value=4, max_value=20, value=8)

if st.button("🚀 Tạo slide"):
    if not prompt.strip():
        st.warning("Vui lòng nhập yêu cầu.")
    else:
        with st.spinner("Đang sinh slide..."):
            url = "http://localhost:8000/generate_pptx"
            data = {"prompt": prompt, "max_slides": str(max_slides)}
            files = None
            if uploaded is not None:
                files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}

            resp = requests.post(url, data=data, files=files)
            if resp.status_code != 200:
                st.error(f"Lỗi API: {resp.status_code} - {resp.text[:300]}")
            else:
                # Lưu ZIP
                zip_bytes = resp.content
                st.download_button("⬇️ Tải ZIP (PPTX + Prompts + Outline)", data=zip_bytes, file_name="slides_bundle.zip", mime="application/zip")

                # Hiển thị nhanh outline + số slide
                try:
                    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
                    with zf.open("meta.json") as f:
                        meta = json.loads(f.read().decode("utf-8"))
                    with zf.open("outline.md") as f:
                        outline_md = f.read().decode("utf-8")
                    st.subheader(f"🧭 Outline: {meta.get('title','')}")
                    st.markdown(outline_md)

                    with zf.open("prompts.json") as f:
                        prompts = json.loads(f.read().decode("utf-8"))
                    st.subheader("🧩 Prompts cho từng slide")
                    st.json(prompts)
                except Exception as e:
                    st.info("Không thể xem nhanh nội dung ZIP. Bạn vẫn có thể tải ZIP về.")
                    st.exception(e)
