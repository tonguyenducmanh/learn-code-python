API viết thơ lục bám (dạng streaming text)

Input: Yêu cầu về chủ đề.

Output: Bài thơ lục bát in ra dưới dạng stream trên 1 giao diện (UI) để demo

Gợi ý:

B1: dựng API stream, UI để Demo.
B2: Xây dựng Dịch vụ viết thơ:
    - Xá định luật thơ Lục bát, prompt/instructions để hướng dẫn Mô hình ngôn ngữ lớn(GPT-4.1)
    - Có thể kết hợp với Sẻach Internet để lấy thêm thông tin cho chính xác.

Yêu cầu:
tạo 1 file dùng chung là gen_poetic.py để gen thơ, tạo 1 file là api.py dùng FastAPI và 1 file là app.py dùng Streamlist

tham khảo đoạn code sau

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import OpenAI
from typing import List, Dict
from pydantic import BaseModel
import json

class MessageRequest(BaseModel):
    input: List[Dict[str, str]] = [
        {
            "role": "user",
            "content": "Viết bài thơ về Bác Hồ.",
        },
    ]

app = FastAPI()
client = OpenAI(
    api_key=""
)

def event_stream(input: list[dict]):
    stream = client.responses.create(
        model="gpt-4.1",
        input=input,
        stream=True,
    )
    for event in stream:
        if hasattr(event, "delta"):
            yield json.dumps(event.model_dump()) + "\n"

@app.post("/stream")
def stream_response(request: MessageRequest):
    return StreamingResponse(event_stream(request.input), media_type="application/json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("stream:app", host="0.0.0.0", port=8000, reload=True)

