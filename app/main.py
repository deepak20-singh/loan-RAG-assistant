from ingestion import DataIngestion
from retrival import QueryRetrival
from sentence_transformers import SentenceTransformer
from db.dbconnections import QdrantDatabase

import uuid
import json

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
db = QdrantDatabase()



def file_ingestion(ingest_id, path="data/policy.md"): 
    try:
        ingestion = DataIngestion(ingest_id, model, db)
        ingestion.ingest(path)
    except Exception as e:
        print(f"Error: {e}")
        
def file_retrival():
    pass
        
def main():
    file_path = "data/policy.md"  # change this to your file
    ingest_id = uuid.uuid4()
    
    # file_ingestion(ingest_id)
    
    top_K_result = QueryRetrival(ingest_id, model, db).retrive_data("What credit score do I need?")
    for r in top_K_result:
        print(json.dumps(r, indent=2))

if __name__ == "__main__":
    main()