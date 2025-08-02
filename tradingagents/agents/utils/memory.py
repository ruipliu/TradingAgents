import chromadb
from chromadb.config import Settings
from openai import OpenAI
import hashlib


class FinancialSituationMemory:
    def __init__(self, name, config):
        self.config = config
        self.use_embeddings = config["llm_provider"] == "openai"

        if self.use_embeddings:
            if config["backend_url"] == "http://localhost:11434/v1":
                self.embedding = "nomic-embed-text"
            else:
                self.embedding = "text-embedding-3-small"
            self.client = OpenAI(base_url=config["backend_url"])

        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        self.situation_collection = self.chroma_client.create_collection(name=name)

    def get_embedding(self, text):
        """Get OpenAI embedding for a text"""
        if not self.use_embeddings:
            return None

        response = self.client.embeddings.create(
            model=self.embedding, input=text
        )
        return response.data[0].embedding

    def _get_text_hash(self, text):
        """Generate a hash-based ID for text when not using embeddings"""
        return hashlib.md5(text.encode()).hexdigest()

    def add_situations(self, situations_and_advice):
        """Add financial situations and their corresponding advice. Parameter is a list of tuples (situation, rec)"""
        situations = []
        advice = []
        ids = []
        embeddings = []

        offset = self.situation_collection.count()

        for i, (situation, recommendation) in enumerate(situations_and_advice):
            situations.append(situation)
            advice.append(recommendation)
            ids.append(str(offset + i))

            if self.use_embeddings:
                embeddings.append(self.get_embedding(situation))

        if self.use_embeddings:
            self.situation_collection.add(
                documents=situations,
                metadatas=[{"recommendation": rec} for rec in advice],
                embeddings=embeddings,
                ids=ids,
            )
        else:
            self.situation_collection.add(
                documents=situations,
                metadatas=[{"recommendation": rec} for rec in advice],
                ids=ids,
            )

    def get_memories(self, current_situation, n_matches=1):
        """Find matching recommendations using embeddings or text search"""
        if self.use_embeddings:
            query_embedding = self.get_embedding(current_situation)
            results = self.situation_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_matches,
                include=["metadatas", "documents", "distances"],
            )
        else:
            # Fallback to text-based search when embeddings not available
            results = self.situation_collection.query(
                query_texts=[current_situation],
                n_results=n_matches,
                include=["metadatas", "documents", "distances"],
            )

        matched_results = []
        for i in range(len(results["documents"][0])):
            if self.use_embeddings:
                similarity_score = 1 - results["distances"][0][i]
            else:
                # For text search, distances are different - adjust accordingly
                similarity_score = max(0, 1 - results["distances"][0][i])

            matched_results.append(
                {
                    "matched_situation": results["documents"][0][i],
                    "recommendation": results["metadatas"][0][i]["recommendation"],
                    "similarity_score": similarity_score,
                }
            )

        return matched_results