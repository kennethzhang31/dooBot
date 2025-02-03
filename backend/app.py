from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import rag_chain

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],  
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def query_chatbot(request: QueryRequest):
    try:
        print(f"Received query: {request.query}")  # ✅ Log input query
        response = rag_chain.invoke(request.query)
        print(f"Generated response: {response}")  # ✅ Log generated response
        return {"response": response}
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))