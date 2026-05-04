import json
import numpy as np

from rank_bm25 import BM25Okapi

class QueryRetrival:
    def __init__(self, ingest_id, model, db):
        self.ingest_id = ingest_id
        self.model = model
        self.db = db
        
        self.chunks = self.db.fetch_all_chunks()
        
        # Build BM25 corpus
        self.texts = [doc.payload["text"] for doc in self.chunks]
        tokenized_corpus = [text.lower().split() for text in self.texts]
        
        self.bm25 = BM25Okapi(tokenized_corpus)
        
    def _normalize(self, scores):
        if not scores:
            return scores

        min_s = min(scores)
        max_s = max(scores)

        if max_s - min_s == 0:
            return [1.0] * len(scores)

        return [(s - min_s) / (max_s - min_s) for s in scores]
    
    def _keyword_search(self, query, top_k: int= 3):
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        top_k_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for i in top_k_indices:
            results.append({
                "id": self.chunks[i].id,
                "text": self.texts[i],
                "keyword_score": scores[i]
            })

        return json.dumps(results)
        
    def _semantic_search(self, query, top_k: int):
        vector_query = self.model.encode([query], normalize=True)[0]
        hits = self.db.search(vector_query, top_k)
        # print(json.dumps(response, indent=2))
        results = []
        for hit in hits:
            results.append({
                "id": hit.id,
                "semantic_score": hit.score,
                "payload": hit.payload
            })
        
        return json.dumps(results)
    
    def retrive_data(self, query, top_k:int= 3, alpha=0.7):
        semantic = json.loads(self._semantic_search(query, top_k))
        keyword = json.loads(self._keyword_search(query, top_k))
        
        sem_scores = self._normalize([r["semantic_score"] for r in semantic])
        key_scores = self._normalize([r["keyword_score"] for r in keyword])

        for i, r in enumerate(semantic):
            r["semantic_score"] = sem_scores[i]

        for i, r in enumerate(keyword):
            r["keyword_score"] = key_scores[i]

        merged = {}
        
        # Add semantic results
        for r in semantic:
            merged[r["id"]] = {
                "id": r["id"],
                "semantic_score": r["semantic_score"],
                "payload": r["payload"],
                "keyword_score": 0.0
            }

        # Add keyword results
        for r in keyword:
            if r["id"] in merged:
                merged[r["id"]]["keyword_score"] = r["keyword_score"]
            else:
                merged[r["id"]] = {
                    "id": r["id"],
                    "text": r["text"],
                    "semantic_score": 0.0,
                    "keyword_score": r["keyword_score"]
                }

        # Final scoring
        results = []
        for item in merged.values():
            final_score = (
                alpha * item["semantic_score"] +
                (1 - alpha) * item["keyword_score"]
            )

            item["final_score"] = final_score
            results.append(item)

        # Sort and return
        results.sort(key=lambda x: x["final_score"], reverse=True)

        return results[:top_k]