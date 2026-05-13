
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, HTTPException
from app.schemas import QueryRequest, QueryResult, LoanApprovalRequest, LoanApprovalResponse, FileIngestionRequest
from app.ingestion import DataIngestion
from app.retrival import QueryRetrival
from app.db.dbconnections import QdrantDatabase
from app.config import Settings
from app.llm_router import LLMRouter


import uuid
import json

settings = Settings()
llm_router = LLMRouter()

# Move model and db init inside functions to avoid import-time failures
# model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# db = QdrantDatabase()

# TODO : write a basic fastapi code to expose the ingestion and retrival as an API. and then we can use that API in the main function to ingest and retrive the data.
app = FastAPI()

# Use schemas to define the request and response models for the API endpoints
@app.post("/ingest")
def ingest_file(data: FileIngestionRequest):
    try:
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        db = QdrantDatabase()
        ingestion = DataIngestion(data.ingest_id, model, db)
        ingestion.ingest(data.file_path)
        return {"message": "File ingested successfully", "ingest_id": data.ingest_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/query", response_model=QueryResult)
def query_file(data: QueryRequest):
    try:
        ingest_id = data.ingest_id
        question = data.question
        print(f"Received query: {question} for ingest_id: {ingest_id}")

        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        db = QdrantDatabase()
        retrival = QueryRetrival(ingest_id, model, db)
        top_K_result = retrival.retrive_data(question, data.top_k)
        print(f"Top K retrieval results: {top_K_result}")

        try:
            prompt = f"""
            You are a helpful assistant for answering questions about loan policies.
                - Use the following retrieved information to answer the question at the end.
                - if any information is missing in the retrieved information, don't make up an answer, just say you don't know.
                - And if the question is not related to LOAN policies, say you are not able to answer that question.
                
                Retrieved Information:
                    {json.dumps(top_K_result, indent=2)}
                
                Question:
                    {question}
            """
            response = llm_router.route_request(
                request_type="groq",
                prompt=prompt
            )
            print(f"LLM Response: {response}")
        except Exception as e:
            print(f"Error during LLM processing: {e}")
            raise HTTPException(status_code=500, detail="Error processing the query with LLM.")

        return {"result": response, "model_used": data.model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/loan-approval", response_model=LoanApprovalResponse)
def loan_approval(request: LoanApprovalRequest):
    try:
        ingest_id = request.ingest_id
        query = "Based on the applicant's information, should the loan be approved, denied, or pending?"

        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        db = QdrantDatabase()
        retrival = QueryRetrival(ingest_id, model, db)
        top_K_result = retrival.retrive_data(query, 5)  # Use fixed top_k or add to request

        prompt = f"""
        You are a helpful assistant for answering questions about loan approvals.
        - Based on the following applicant information, determine if the loan should be approved, denied, or pending.
        - Provide a reason for the decision and a confidence score between 0 and 1.

        Useful Information:
        {json.dumps(top_K_result, indent=2)}

        Applicant Information:
            Name: {request.applicant_name}
            Credit Score: {request.credit_score}
            Annual Income: {request.annual_income}
            Loan Amount: {request.loan_amount}
            Loan Purpose: {request.loan_purpose}
        """
        response = llm_router.route_request(
            request_type="groq",
            response_model=LoanApprovalResponse,
            prompt=prompt
        )
        # Now response is LoanApprovalResponse
        return {
            "applicant_name": request.applicant_name,
            "credit_score": request.credit_score,
            "annual_income": request.annual_income,
            "loan_amount": request.loan_amount,
            "loan_purpose": request.loan_purpose,
            "approval_status": response.approval_status,
            "reason": response.reason,
            "confidence_score": response.confidence_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="", port=8000)