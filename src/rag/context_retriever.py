import re
from typing import List, Tuple

import numpy as np

from src.embeddings import EmbeddingManager
from .knowledge_base import KnowledgeBase
from .rule_section_finder import RuleSectionFinder

# Context retriever for ranking rule chunks based on semantic similarity, keywords, and headings. 
class ContextRetriever:
    """Rank rule chunks using semantic similarity, keywords, and headings."""

    # Initialize the context retriever with the knowledge base, embedding manager, and rule section finder. 
    def __init__(
        self,
        knowledge_base: KnowledgeBase,
        embedding_manager: EmbeddingManager,
        rule_section_finder: RuleSectionFinder,
    ):
        self.knowledge_base = knowledge_base
        self.embedding_manager = embedding_manager
        self.rule_section_finder = rule_section_finder

    # Retrieve the top matching rule chunks and their metadata based on the query. 
    def retrieve(self, query: str, top_k: int = 3) -> Tuple[List[str], List[dict]]:
        """Return the top matching rule chunks and their metadata."""
        if (
            self.knowledge_base.embeddings is None
            or len(self.knowledge_base.documents) == 0
        ):
            return [], []
        
        # Return empty lists if the knowledge base is not initialized.
        query_lower = query.lower().strip()
        query_words = {word for word in re.findall(r"[a-z0-9']+", query_lower) if word}

        # Extract the special rule section from the query if it exists.
        exact_special_rule = self.rule_section_finder.extract_special_rule_section(
            query_lower
        ) 
        # If an exact special rule section is found, return it immediately.
        if exact_special_rule is not None:
            document, metadata = exact_special_rule
            return [document], [metadata]
    
        # Extract the unit section from the query if it exists.
        exact_unit = self.rule_section_finder.extract_unit_section(query_lower)
        if exact_unit is not None:
            document, metadata = exact_unit
            return [document], [metadata]

        # Compute the semantic embedding for the query.
        query_embedding = np.array(self.embedding_manager.embed_text(query))

        # Compute the semantic similarity between the query and all documents.
        from sklearn.metrics.pairwise import cosine_similarity

        # Compute the semantic similarity scores between the query and all documents.
        semantic_scores = cosine_similarity(
            [query_embedding], self.knowledge_base.embeddings
        )[0]
        keyword_scores = np.zeros(len(self.knowledge_base.documents))
        heading_scores = np.zeros(len(self.knowledge_base.documents))

        exact_heading_pattern = re.compile(
            rf"^\s*###+\s+{re.escape(query_lower)}\s*$",
            flags=re.IGNORECASE | re.MULTILINE,
        )
        prefix_heading_pattern = re.compile(
            rf"^\s*###+\s+{re.escape(query_lower)}\b",
            flags=re.IGNORECASE | re.MULTILINE,
        )

        # Iterate over all documents to compute keyword and heading scores.
        for index, document in enumerate(self.knowledge_base.documents):
            document_lower = document.lower()
            source_name = str(self.knowledge_base.metadatas[index].get("source", ""))
            matching_words = sum(
                1
                for word in query_words
                if re.search(rf"\b{re.escape(word)}\b", document_lower)
            )

            if query_lower and exact_heading_pattern.search(document):
                heading_scores[index] += 1.0
            elif query_lower and prefix_heading_pattern.search(document):
                heading_scores[index] += 0.25

            if len(query_words) <= 3 and source_name.endswith("special_rules.md"):
                heading_scores[index] += 0.15
            keyword_scores[index] = matching_words

        if keyword_scores.max() > 0:
            keyword_scores = keyword_scores / keyword_scores.max()

        # Combine the semantic, keyword, and heading scores to rank the documents.
        combined_scores = 0.65 * semantic_scores + 0.2 * keyword_scores + heading_scores
        top_indices = np.argsort(combined_scores)[-top_k:][::-1]
        retrieved_documents = [
            self.knowledge_base.documents[index] for index in top_indices
        ]
        retrieved_metadata = [
            self.knowledge_base.metadatas[index] for index in top_indices
        ]
        return retrieved_documents, retrieved_metadata
