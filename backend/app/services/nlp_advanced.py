"""Advanced NLP tooling for article analysis."""

import re

from sqlalchemy.orm import Session

from app.models.feed import Article
from app.models.rule import ArticleMetadata


class AdvancedNLPProcessor:
    """Advanced NLP processing for articles."""

    def __init__(self, db: Session):
        """Initialize NLP processor."""
        self.db = db

    def extract_entities(self, text: str) -> dict[str, list[str]]:
        """Extract named entities from text.

        This is a simplified implementation. In production, use spaCy or similar.
        """
        entities: dict[str, list[str]] = {
            "people": [],
            "organizations": [],
            "locations": [],
            "technologies": [],
            "products": [],
        }

        # Common tech keywords
        tech_keywords = [
            "AI",
            "ML",
            "Python",
            "JavaScript",
            "React",
            "Docker",
            "Kubernetes",
            "AWS",
            "Azure",
            "GCP",
            "TensorFlow",
            "PyTorch",
            "OpenAI",
            "Claude",
            "GPT",
            "LLM",
            "API",
            "REST",
            "GraphQL",
            "SQL",
            "NoSQL",
            "Redis",
            "PostgreSQL",
            "MongoDB",
            "FastAPI",
            "Django",
            "Flask",
            "Node.js",
        ]

        # Simple pattern matching for demonstration
        for tech in tech_keywords:
            if re.search(rf"\b{re.escape(tech)}\b", text, re.IGNORECASE):
                if tech not in entities["technologies"]:
                    entities["technologies"].append(tech)

        # Extract capitalized phrases as potential entities
        # This is very basic - use NER model in production
        words = text.split()
        for i, word in enumerate(words):
            if word and word[0].isupper() and len(word) > 2:
                # Simple heuristic: 2-3 capitalized words in a row
                phrase_parts = [word]
                for j in range(i + 1, min(i + 3, len(words))):
                    if words[j] and words[j][0].isupper():
                        phrase_parts.append(words[j])
                    else:
                        break

                if len(phrase_parts) >= 2:
                    phrase = " ".join(phrase_parts)
                    # Guess entity type based on keywords
                    if any(kw in phrase for kw in ["Inc", "Corp", "Company", "Ltd", "LLC"]):
                        if phrase not in entities["organizations"]:
                            entities["organizations"].append(phrase)
                    else:
                        if phrase not in entities["people"]:
                            entities["people"].append(phrase)

        return entities

    def extract_keywords(self, text: str, max_keywords: int = 10) -> list[str]:
        """Extract keywords from text using TF-IDF-like approach."""
        # Remove common stop words
        stop_words = set(
            [
                "the",
                "a",
                "an",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
                "by",
                "from",
                "as",
                "is",
                "was",
                "are",
                "were",
                "been",
                "be",
                "have",
                "has",
                "had",
                "do",
                "does",
                "did",
                "will",
                "would",
                "could",
                "should",
                "may",
                "might",
                "must",
                "can",
                "this",
                "that",
                "these",
                "those",
                "i",
                "you",
                "he",
                "she",
                "it",
                "we",
                "they",
            ]
        )

        # Tokenize and filter
        words = re.findall(r"\b\w+\b", text.lower())
        filtered_words = [w for w in words if len(w) > 3 and w not in stop_words]

        # Count frequency
        word_freq: dict[str, int] = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and return top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:max_keywords]]

    def generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """Generate extractive summary from text."""
        if not text:
            return ""

        # Split into sentences
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        if len(sentences) <= max_sentences:
            return " ".join(sentences) + "."

        # Score sentences based on position and keyword density
        keywords = set(self.extract_keywords(text, 15))
        scored_sentences = []

        for idx, sentence in enumerate(sentences):
            # Position score (earlier sentences are more important)
            position_score = 1.0 - (idx / len(sentences)) * 0.5

            # Keyword score
            sentence_words = set(re.findall(r"\b\w+\b", sentence.lower()))
            keyword_score = (
                len(sentence_words & keywords) / len(sentence_words) if sentence_words else 0
            )

            total_score = position_score + keyword_score
            scored_sentences.append((total_score, sentence))

        # Sort by score and take top N
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        summary_sentences = [s for _, s in scored_sentences[:max_sentences]]

        # Reorder by original position
        summary_sentences_ordered = [s for s in sentences if s in summary_sentences]

        return " ".join(summary_sentences_ordered) + "."

    def clean_content(self, html_content: str) -> str:
        """Remove HTML tags and clean content."""
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", html_content)

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove common ad phrases
        ad_phrases = [
            "advertisement",
            "sponsored content",
            "click here",
            "subscribe now",
            "sign up",
        ]
        for phrase in ad_phrases:
            text = re.sub(phrase, "", text, flags=re.IGNORECASE)

        return text.strip()

    def process_article(self, article: Article) -> ArticleMetadata:
        """Process article with all NLP tools."""
        # Get or create metadata
        metadata = (
            self.db.query(ArticleMetadata).filter(ArticleMetadata.article_id == article.id).first()
        )

        if not metadata:
            metadata = ArticleMetadata(article_id=article.id)
            self.db.add(metadata)

        # Combine title and content for analysis
        text = f"{article.title}. {article.content or article.description or ''}"

        try:
            metadata.processing_status = "processing"

            # Extract entities
            metadata.entities = self.extract_entities(text)

            # Extract keywords
            metadata.keywords = self.extract_keywords(text)

            # Generate summary
            if article.content:
                metadata.summary = self.generate_summary(article.content)

            # Clean content
            if article.content:
                metadata.main_content = self.clean_content(article.content)

            metadata.processing_status = "completed"
            metadata.processed_at = None  # Set via datetime.utcnow in model

        except Exception as e:
            metadata.processing_status = "failed"
            if metadata.processing_errors is None:
                metadata.processing_errors = []
            metadata.processing_errors.append(str(e))

        self.db.commit()
        return metadata
