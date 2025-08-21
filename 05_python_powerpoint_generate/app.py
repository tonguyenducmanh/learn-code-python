
import streamlit as st
import requests
import base64
import json

st.set_page_config(page_title="AI Slide Designer", page_icon="🧠", layout="centered")

st.title("🧠🎨 AI Slide Designer")
st.caption("Mỗi slide một phong cách — AI tự hiểu prompt và thiết kế bố cục, màu sắc, ảnh minh hoạ.")

with st.expander("⚙️ Tuỳ chọn"):
    api_url = st.text_input("API URL", value="http://localhost:8000/generate_slides", help="Đặt URL API FastAPI của bạn")

user_prompt = st.text_area("Nhập yêu cầu tạo slide (tiếng Việt hoặc tiếng Anh):", height=220, placeholder="Ví dụ: Tạo slide trình bày chiến lược Go-To-Market cho sản phẩm SaaS B2B, có số liệu, biểu đồ, case study, lộ trình...")
uploaded_file = st.file_uploader("Tài liệu tham chiếu (tùy chọn):", type=["pdf", "txt", "docx"])

col1, col2 = st.columns([1,1])
with col1:
    seed = st.number_input("Random seed (tuỳ chọn, để -1 nếu muốn ngẫu nhiên mỗi lần)", value=-1, step=1)
with col2:
    max_slides = st.slider("Số slide tối đa mà AI có thể tạo", min_value=3, max_value=30, value=12)

if st.button("🚀 Tạo Slide"):
    if not user_prompt.strip():
        st.warning("Vui lòng nhập yêu cầu.")
    else:
        with st.spinner("AI đang thiết kế slide..."):
            data = {"user_prompt": user_prompt, "max_slides": str(max_slides), "seed": str(seed)}
            files = {}
            if uploaded_file is not None:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            try:
                resp = requests.post(api_url, data=data, files=files, timeout=120)
                if resp.status_code != 200:
                    st.error(f"Lỗi API ({resp.status_code}): {resp.text}")
                else:
                    payload = resp.json()
                    spec = payload.get("spec", {})
                    pptx_b64 = payload.get("pptx_base64", "")
                    if not pptx_b64:
                        st.error("Không nhận được file PPTX từ API.")
                    else:
                        st.success("Đã tạo slide!")
                        st.subheader("📋 Cấu trúc & phong cách từng slide")
                        st.json(spec)

                        pptx_bytes = base64.b64decode(pptx_b64)
                        st.download_button(
                            label="⬇️ Tải file PPTX",
                            data=pptx_bytes,
                            file_name=payload.get("filename", "slides.ai.pptx"),
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
            except Exception as e:
                st.exception(e)
