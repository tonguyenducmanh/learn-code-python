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
