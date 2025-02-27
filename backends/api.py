from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from nlp import generate_response, clean_markdown, extract_doc_content
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CDP Support Agent Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for request validation
class QueryRequest(BaseModel):
    question: str

def handle_query(service_name: str, question: str, doc_url: str = None) -> dict:
    """
    Generalized function to handle queries based on the service name.
    
    Args:
        service_name (str): The name of the service (e.g., "Segment", "mParticle").
        question (str): The user’s query.
        doc_url (str, optional): Documentation link if applicable.

    Returns:
        dict: A JSON response containing the chatbot’s reply.
    """
    prompt = f"How-to question for {service_name}: {question}"
    if doc_url:
        prompt += f"\nRefer to the {service_name} documentation: {doc_url}"

    try:
        bot_response = generate_response(prompt)
        cleaned_response = clean_markdown(bot_response)
        return {"response": cleaned_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.post("/api/general", response_model=dict)
def general_query(query: QueryRequest):
    """Endpoint for general how-to questions."""
    return handle_query("General", query.question)

@app.post("/api/segment", response_model=dict)
def segment_query(query: QueryRequest):
    """Endpoint for Segment-specific how-to questions."""
    return handle_query("Segment", query.question, "https://segment.com/docs/?ref=nav")

@app.post("/api/mparticle", response_model=dict)
def mparticle_query(query: QueryRequest):
    """Endpoint for mParticle-specific how-to questions."""
    return handle_query("mParticle", query.question, "https://docs.mparticle.com/")

@app.post("/api/lytics", response_model=dict)
def lytics_query(query: QueryRequest):
    """Endpoint for Lytics-specific how-to questions."""
    return handle_query("Lytics", query.question, "https://docs.lytics.com/")

@app.post("/api/zeotap", response_model=dict)
def zeotap_query(query: QueryRequest):
    """Endpoint for Zeotap-specific how-to questions."""
    return handle_query("Zeotap", query.question, "https://docs.zeotap.com/home/en-us/")

@app.post("/api/extract-doc", response_model=dict)
def extract_document(query: QueryRequest, doc_url: str = Query(..., description="URL of the documentation page")):
    """
    Extracts relevant content from the provided documentation URL based on the query.

    Args:
        query (QueryRequest): The user's question.
        doc_url (str): The documentation page URL.

    Returns:
        dict: A JSON response containing the extracted snippet.
    """
    try:
        snippet = extract_doc_content(doc_url, query.question)
        return {"snippet": snippet}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting document content: {str(e)}")
