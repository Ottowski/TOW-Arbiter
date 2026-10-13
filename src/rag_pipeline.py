from pathlib import Path
from typing import List, Tuple

from src.document_loader import DocumentLoader
from src.embeddings import EmbeddingManager
from src.rag.answer_generator import AnswerGenerator
from src.rag.context_retriever import ContextRetriever
from src.rag.knowledge_base import KnowledgeBase
from src.rag.rule_section_finder import RuleSectionFinder


class RAGPipeline:
    """Coordinate rule indexing, retrieval, and answer generation."""

    # Initialize the RAG pipeline with the necessary components.
    def __init__(
        self,
        rules_directory: str = "./rules",
        vector_store_path: str = "./data/vector_store",
    ):
        # Set up the embedding manager, document loader, and knowledge base.
        self.embedding_manager = EmbeddingManager()
        self.document_loader = DocumentLoader(rules_directory=rules_directory)
        self.rules_directory = rules_directory
        self.vector_store_path = Path(vector_store_path)

        # Initialize the knowledge base, rule section finder, context retriever, and answer generator.
        self.knowledge_base = KnowledgeBase(
            rules_directory=rules_directory,
            vector_store_path=self.vector_store_path,
            document_loader=self.document_loader,
            embedding_manager=self.embedding_manager,
        )
        # Initialize the rule section finder.
        self.rule_section_finder = RuleSectionFinder(rules_directory)
        self.context_retriever = ContextRetriever(
            knowledge_base=self.knowledge_base,
            embedding_manager=self.embedding_manager,
            rule_section_finder=self.rule_section_finder,
        )
        # Initialize the answer generator.
        self.answer_generator = AnswerGenerator()
        
    @property
    def documents(self):
        return self.knowledge_base.documents

    @documents.setter
    def documents(self, value):
        self.knowledge_base.documents = value

    @property
    def embeddings(self):
        return self.knowledge_base.embeddings

    @embeddings.setter
    def embeddings(self, value):
        self.knowledge_base.embeddings = value

    @property
    def metadatas(self):
        return self.knowledge_base.metadatas

    @metadatas.setter
    def metadatas(self, value):
        self.knowledge_base.metadatas = value

        # Compute a hash of the current rules for change detection.
    def _rules_hash(self) -> str:
        return self.knowledge_base._rules_hash()
    
    # Extract a special rule section from the rules.
    def _extract_special_rule_section(self, rule_name: str) -> tuple[str, dict] | None:
        return self.rule_section_finder.extract_special_rule_section(rule_name)

    # Extract a unit section from the rules.
    def _extract_unit_section(self, unit_name: str) -> tuple[str, dict] | None:
        return self.rule_section_finder.extract_unit_section(unit_name)
    
    # Initialize the knowledge base.
    def initialize_knowledge_base(self, force_rebuild: bool = False):
        self.knowledge_base.initialize(force_rebuild=force_rebuild)

    # Retrieve context documents relevant to a query.
    def retrieve_context(self, query: str, top_k: int = 3) -> Tuple[List[str], List[dict]]:
        return self.context_retriever.retrieve(query, top_k=top_k)

    # Generate an answer using the LLM based on the retrieved context.
    def generate_answer(self, query: str, context_documents: List[str]) -> str:
        return self.answer_generator.generate_prompt(query, context_documents)

    # Answer a question using either the LLM or a simple aggregation of context documents.
    def answer_question(self, query: str, use_llm: bool = False) -> dict:
        relevant_docs, metadatas = self.retrieve_context(query, top_k=5)
        if use_llm:
            answer = self.generate_answer(query, relevant_docs)
        else:
            answer = self._simple_answer(relevant_docs)

        return {
            "query": query,
            "answer": answer,
            "sources": metadatas,
            "context_chunks": relevant_docs,
        }

    # Generate a simple answer by combining the top matched context documents.
    def _simple_answer(self, documents: List[str]) -> str:
        return self.answer_generator.simple_answer(documents)

    # Normalize markdown text for better readability before displaying it.
    def _normalize_markdown_for_display(self, text: str) -> str:
        return self.answer_generator.normalize_markdown(text)
