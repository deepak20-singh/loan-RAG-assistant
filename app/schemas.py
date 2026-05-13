from pydantic import BaseModel, Field
from typing import Literal

class FileIngestionRequest(BaseModel):
    file_path: str = Field(..., description="The path to the file to be ingested.")
    ingest_id: str = Field(..., description="The unique identifier for the file to be ingested.")

class QueryRequest(BaseModel):
    question: str = Field(..., description="The user's question to be answered based on the ingested data.")
    ingest_id: str = Field("", description="The unique identifier for the ingested data to query against.")
    model: str = Field("groq", description="The LLM model to use for answering the question.")
    top_k: int = Field(5, description="The number of top results to retrieve from the database for answering the question.")

class QueryAnswer(BaseModel):
    question: str = Field(..., description="The user's question to be answered based on the ingested data.")
    answer: str = Field(None, description="The answer to the user's question.")
    confidence_score: float = Field(..., ge=0, le=1, description="A score indicating the confidence in the answer.")
    content: str = Field(None, description="The content used to answer the question.")

class QueryResult(BaseModel):
    result: QueryAnswer = Field(..., description="The result of the query, including the answer and confidence score.")
    model_used: str = Field(..., description="The LLM model used to generate the answer.")

class LLMRequest(BaseModel):
    request_type: Literal["groq", "whisper", "deepface"] = Field(..., description="The type of LLM request to route.")
    prompt: str = Field(..., description="The prompt or input for the LLM to process.")

class LoanApprovalRequest(BaseModel):
    applicant_name: str = Field(..., description="Name of the loan applicant.")
    credit_score: int = Field(..., description="Credit score of the applicant.")
    annual_income: float = Field(..., description="Annual income of the applicant.")
    loan_amount: float = Field(..., description="Amount of loan requested.")
    loan_purpose: str = Field(..., description="Purpose of the loan.")
    ingest_id: str = Field("", description="The unique identifier for the ingested data to query against.")

class LoanApprovalResponse(BaseModel):
    applicant_name: str = Field(..., description="Name of the loan applicant.")
    credit_score: int = Field(..., description="Credit score of the applicant.")
    annual_income: float = Field(..., description="Annual income of the applicant.")
    loan_amount: float = Field(..., description="Amount of loan requested.")
    loan_purpose: str = Field(..., description="Purpose of the loan.")
    approval_status: Literal["approved", "denied", "pending"] = Field(None, description="Status of the loan approval.")
    reason: str = Field(None, description="Reason for loan approval or denial.")
    confidence_score: float = Field(None, ge=0, le=1, description="Confidence score for the loan approval decision.")