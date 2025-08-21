Tạo API đánh giá độ phù hợp CV với tin tuyển dụng
Input: FILE CV(PDF)
System: Nội dung tin tuyển dụng
Output: Đánh giá độ phù hợp của CV với tin tuyển dụng

Gợi ý:
B1: Dựng API nhận vào là 1 file CV.
B2: Chuyển đổi PDF sang Text (Thư viện đọc PDF của python)
B3: Phân tích các chỉ tiêu chính từ JD, trọng số cho từng chỉ tiêu
B4: Gửi nội dung CV, kèm các chỉ tiêu từ JD lên cho LLM
B5: Nhận kết quả, hiển thị độ phù hợp

Yêu cầu:
tạo 1 file dùng chung là review_cv.py để đánh giá cv, tạo 1 file là api.py dùng FastAPI và 1 file là app.py dùng Streamlist

trong api thì cung cấp 2 tham số là nội dung file, prompt system là tin tuyển dụng muốn review

tham khảo tương tự đoạn code dưới

gen_poetic.py

```
from openai import OpenAI

client = OpenAI(api_key="...")  # API key của bạn

def generate_luc_bat_poem_stream(topic: str):
    prompt = f"""
Bạn là một nhà thơ hiện đại, hãy viết một bài thơ lục bát về chủ đề sau:
'{topic}'
Luật thơ lục bát:
- Câu 1: 6 chữ; câu 2: 8 chữ
- Vần cuối câu 1 và câu 2 phải bằng nhau
- Câu 3: 6 chữ; câu 4: 8 chữ; câu 4 vần cuối bằng câu 2
- Và tiếp tục theo thể lục bát truyền thống

Viết từng câu thơ, giữ đúng luật thơ lục bát, thể hiện cảm xúc sâu sắc.
Bắt đầu ngay bài thơ.
Hãy trả lời theo dạng streaming text.
"""

    # Streaming response
    with client.responses.stream(
        model="gpt-4.1",
        input=[{"role": "user", "content": prompt}],
    ) as stream:
        for event in stream:
            if event.type == "response.output_text.delta":
                yield event.delta
            elif event.type == "response.error":
                yield f"[ERROR]: {event.error}"
```

api.py

```
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from gen_poetic import generate_luc_bat_poem_stream
class TopicRequest(BaseModel):
    topic: str
app = FastAPI()
@app.post("/stream_poem")
def stream_poem(request: TopicRequest):
    def event_generator():
        for chunk in generate_luc_bat_poem_stream(request.topic):
            yield chunk
    return StreamingResponse(event_generator(), media_type="text/plain")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
```

app.py

```
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
```
