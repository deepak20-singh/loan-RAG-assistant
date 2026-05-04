
class DataIngestion():
    def __init__(self, ingest_id, model, db):
        self.ingest_id = ingest_id
        self.model = model
        self.db = db
        db.create()
    
    def _process_chunks(self, path, chunk_size=500, chunk_overlap=50):
        chunks = []
        metadata = []
        start = 0
        chunk_index = 0

        with open(path, "r", encoding="utf-8") as f:
            data = f.read()

        while start < len(data):
            end = start + chunk_size
            chunk = data[start:end]

            last_period = -1
            if end < len(data):
                last_period = chunk.rfind(".")

            if last_period > chunk_size * 0.7:
                chunk = chunk[:last_period + 1]
                end = start + last_period + 1

            chunk = chunk.strip()

            file_info = {
                "file_name": path,
                "text": chunk,
                "chunk_index": chunk_index,
                "ingest_id": str(self.ingest_id)
            }

            chunks.append(chunk)
            metadata.append(file_info)

            start = end - chunk_overlap
            chunk_index += 1

            if end <= start:  # safety
                break

        return chunks, metadata
    
    def ingest(self, path: str):
        # Chunking
        print("Initiating Ingestion | chunking content")
        chunks, metadata = self._process_chunks(path)
        print(f"Converted content to chunks. Total chunks : {len(chunks)}")
        
        # Vectorizing data
        embeddings = self.model.encode(chunks, normalize=True)
        
        # Update vectors in db
        total_data = []
        for i, (chunks, meta, embedding) in enumerate(zip(chunks, metadata, embeddings)):
            data = [i, embedding, meta]
            total_data.append(data)
         
        self.db.insert(total_data)
    
    # TODO: Process multiple files to update our vector database
    def _process_files(self, paths):
        pass

            
        # Adding embeddings to Qdrant
        # print("Initiating Ingestion | adding content to db")
        # for embedding in embeddings:
        #     res = db.insert(embedding)
        #     print(res)