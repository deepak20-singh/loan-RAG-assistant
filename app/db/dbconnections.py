from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

class InsertData:
    idx: str
    vector: str
    payload: dict

class QdrantDatabase():
    def __init__(self):
        self.client = QdrantClient(host="localhost", port=6333)
        self.collection_name = 'policy_data'
        
    def create(self):
        vector_size = 384 
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size, 
                    distance=Distance.COSINE),
            )
        return "Success"
            
    def insert(self, data: InsertData):
        try:
            for (idx, vector, payload) in data:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        PointStruct(
                            id=idx,
                            vector=vector.tolist(),
                            payload=payload
                        )
                    ]
                )
            return "Success"
        except Exception as e:
            print(f"ERROR while inserting vectors: {e}")
            return "failed"
        
    def search(self, query_vector, top_k: int= 5):
        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=top_k
        )
        return hits
    
    def fetch_all_chunks(self):
        all_points = []
        next_offset = None

        while True:
            # Use scroll to fetch a batch of points
            points, next_offset = self.client.scroll(
                collection_name=self.collection_name,
                limit=100,  # Adjust batch size based on your memory
                with_payload=True,
                with_vectors=False,  # Set to True if you need the embeddings
                offset=next_offset
            )
            
            all_points.extend(points)

            # If next_offset is None, we've reached the end
            if next_offset is None:
                break
                
        return all_points