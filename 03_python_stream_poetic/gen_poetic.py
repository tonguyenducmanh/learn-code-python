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
