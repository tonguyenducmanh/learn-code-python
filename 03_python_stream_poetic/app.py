import streamlit as st
import requests
st.title("🎉 Demo Viết Thơ Lục Bát Streaming")
topic = st.text_input("Nhập chủ đề thơ:")
if st.button("Viết thơ"):
    if not topic.strip():
        st.warning("Vui lòng nhập chủ đề!")
    else:
        st.markdown("**Bài thơ lục bát đang được tạo, vui lòng chờ...**")
        response = requests.post(
            "http://localhost:8000/stream_poem", 
            json={"topic": topic}, 
            stream=True
        )
        poem_display = st.empty()
        poem_text = ""
        # Xử lý stream từng chunk và hiển thị liên tục
        for chunk in response.iter_content(chunk_size=32):
            text = chunk.decode('utf-8')
            poem_text += text
            poem_display.text(poem_text)