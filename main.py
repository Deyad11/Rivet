from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
class AnalyzeRequest(BaseModel):
    session_text:str
@app.post("/analyze")
def analyze(request:AnalyzeRequest):
    return{
         "status":"received",
         "length":len(request.session_text)
    }