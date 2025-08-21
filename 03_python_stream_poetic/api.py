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