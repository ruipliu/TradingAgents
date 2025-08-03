import chromadb
from chromadb.config import Settings
from openai import OpenAI
import hashlib
import os
from pathlib import Path


class FinancialSituationMemory:
    def __init__(self, name, config):
        self.config = config
        self.use_embeddings = config["llm_provider"] == "openai"

        if self.use_embeddings:
            if config["backend_url"] == "http://localhost:11434/v1":
                self.embedding = "nomic-embed-text"
                self.expected_dimension = 384  # nomic-embed-text dimension
            else:
                self.embedding = "text-embedding-3-small"
                self.expected_dimension = 1536  # text-embedding-3-small dimension
            self.client = OpenAI(base_url=config["backend_url"])
        else:
            self.expected_dimension = None

        # Create persistent storage directory
        memory_dir = Path("./memory_storage") / name
        memory_dir.mkdir(parents=True, exist_ok=True)

        # Use persistent client instead of in-memory client
        self.chroma_client = chromadb.PersistentClient(path=str(memory_dir))

        # Get or create collection with dimension validation
        self.situation_collection = self._get_or_create_collection(name)

    def _get_or_create_collection(self, name):
        """Get existing collection or create new one, handling dimension mismatches."""
        try:
            # Try to get existing collection
            collection = self.chroma_client.get_collection(name=name)

            # Check if collection has existing data
            if collection.count() > 0:
                # If we're switching from embeddings to no embeddings or vice versa,
                # or if there's a dimension mismatch, recreate the collection
                if self.use_embeddings:
                    # Test with a small embedding to check dimension compatibility
                    try:
                        test_embedding = [0.0] * self.expected_dimension
                        collection.query(
                            query_embeddings=[test_embedding],
                            n_results=1,
                            include=["documents"]
                        )
                        print(f"✓ Using existing memory collection with {self.expected_dimension}D embeddings")
                        return collection
                    except Exception as e:
                        if "dimension" in str(e).lower():
                            print(f"⚠️  Dimension mismatch detected in existing collection")
                            print(f"   Expected: {self.expected_dimension}D, but collection has different dimensions")
                            print(f"   Recreating collection to match current embedding model...")

                            # Delete the old collection and create a new one
                            self.chroma_client.delete_collection(name=name)
                            collection = self.chroma_client.create_collection(name=name)
                            print(f"✓ Created new memory collection with {self.expected_dimension}D embeddings")
                            return collection
                        else:
                            # Re-raise if it's not a dimension error
                            raise e
                else:
                    # We're not using embeddings, but collection might have been created with embeddings
                    # Try a text-based query to see if it works
                    try:
                        collection.query(
                            query_texts=["test"],
                            n_results=1,
                            include=["documents"]
                        )
                        print(f"✓ Using existing memory collection without embeddings")
                        return collection
                    except Exception as e:
                        print(f"⚠️  Existing collection incompatible with text-only queries")
                        print(f"   Recreating collection for text-based search...")

                        # Delete the old collection and create a new one
                        self.chroma_client.delete_collection(name=name)
                        collection = self.chroma_client.create_collection(name=name)
                        print(f"✓ Created new memory collection for text-based search")
                        return collection
            else:
                # Empty collection, use as-is
                print(f"✓ Using existing empty memory collection")
                return collection

        except Exception as e:
            # Collection doesn't exist or other error, create new one
            print(f"Creating new memory collection: {name}")
            return self.chroma_client.create_collection(name=name)

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