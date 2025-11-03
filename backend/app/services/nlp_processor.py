"""NLP processing service for article clustering and semantic analysis."""

import math
import re
from collections import Counter

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from spacy.lang.en import English
from sqlalchemy.orm import Session
from textstat import textstat
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.core.config import settings
from app.models.feed import Article


class NLPProcessor:
    """NLP processing service."""

    def __init__(self, db: Session) -> None:
        """Initialize NLP processor."""
        self.db = db
        self.model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.nlp = English()
        if "sentencizer" not in self.nlp.pipe_names:
            self.nlp.add_pipe("sentencizer")

    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for text."""
        embedding = self.model.encode(text)
        return embedding.tolist()

    def process_article(self, article: Article) -> None:
        """Process single article for NLP features."""
        import json

        # Combine title and description for embedding
        text = f"{article.title}. {article.description or ''}"

        # Generate embedding (store as JSON string for SQLite compatibility)
        embedding = self.generate_embedding(text)
        article.embedding = json.dumps(embedding)

        # Extract topics and categories (model auto-converts to JSON)
        topics = self._extract_topics(text)
        article.topics = topics  # JSONEncodedList will handle conversion

        # Calculate sentiment using VADER
        article.sentiment_score = self._calculate_sentiment(text)
        readability_score, readability_label = self._calculate_readability(text)
        article.readability_score = readability_score
        article.readability_label = readability_label
        article.writing_style = self._analyze_style(text)

        self.db.commit()

    def process_all_articles(self, user_id: int) -> dict[str, int]:
        """Process all articles for a user with NLP features."""
        import json

        # Get all articles without embeddings for this user
        articles = (
            self.db.query(Article)
            .join(Article.feed)
            .filter(
                Article.feed.has(user_id=user_id),
                (
                    Article.embedding.is_(None)
                    | Article.readability_score.is_(None)
                    | Article.writing_style.is_(None)
                ),
            )
            .all()
        )

        processed = 0
        for article in articles:
            try:
                # Combine title and description for embedding
                text = f"{article.title}. {article.description or ''}"

                # Generate embedding (store as JSON string for SQLite compatibility)
                embedding = self.generate_embedding(text)
                article.embedding = json.dumps(embedding)

                # Extract topics and categories (model auto-converts to JSON)
                topics = self._extract_topics(text)
                article.topics = topics  # JSONEncodedList will handle conversion

                # Calculate sentiment using VADER
                article.sentiment_score = self._calculate_sentiment(text)
                readability_score, readability_label = self._calculate_readability(text)
                article.readability_score = readability_score
                article.readability_label = readability_label
                article.writing_style = self._analyze_style(text)

                processed += 1

                # Commit in batches of 10 to avoid memory issues
                if processed % 10 == 0:
                    self.db.commit()

            except Exception as e:
                print(f"Error processing article {article.id}: {e}")
                continue

        # Final commit
        self.db.commit()

        return {
            "processed": processed,
            "total": len(articles),
            "message": f"Successfully processed {processed} out of {len(articles)} articles",
        }

    def cluster_articles(self, user_id: int, min_samples: int | None = None) -> int:
        """Cluster articles using DBSCAN on embeddings."""
        import json

        if min_samples is None:
            min_samples = settings.CLUSTERING_MIN_SAMPLES

        # Get articles with embeddings
        articles = (
            self.db.query(Article)
            .join(Article.feed)
            .filter(
                Article.embedding.isnot(None),
                Article.feed.has(user_id=user_id),
            )
            .all()
        )

        if len(articles) < min_samples:
            return 0

        # Extract embeddings (parse JSON strings)
        embeddings = []
        for article in articles:
            if isinstance(article.embedding, str):
                embeddings.append(json.loads(article.embedding))
            else:
                embeddings.append(article.embedding)

        embeddings = np.array(embeddings)

        # Perform clustering
        clustering = DBSCAN(eps=0.5, min_samples=min_samples, metric="cosine")
        labels = clustering.fit_predict(embeddings)

        # Update cluster IDs
        for article, label in zip(articles, labels):
            article.cluster_id = int(label) if label != -1 else None

        self.db.commit()
        return len(set(labels) - {-1})  # Return number of clusters (excluding noise)

    def find_similar_articles(
        self, article: Article, limit: int = 10, threshold: float = 0.7
    ) -> list[tuple[Article, float]]:
        """Find similar articles based on embedding similarity."""
        import json

        if not article.embedding:
            return []

        # Get other articles with embeddings
        articles = (
            self.db.query(Article)
            .filter(
                Article.id != article.id,
                Article.embedding.isnot(None),
                Article.feed.has(user_id=article.feed.user_id),
            )
            .all()
        )

        # Parse article embedding
        if isinstance(article.embedding, str):
            article_embedding = np.array(json.loads(article.embedding))
        else:
            article_embedding = np.array(article.embedding)

        similarities: list[tuple[Article, float]] = []

        for other in articles:
            # Parse other embedding
            if isinstance(other.embedding, str):
                other_embedding = np.array(json.loads(other.embedding))
            else:
                other_embedding = np.array(other.embedding)

            similarity = float(
                np.dot(article_embedding, other_embedding)
                / (np.linalg.norm(article_embedding) * np.linalg.norm(other_embedding))
            )

            if similarity >= threshold:
                similarities.append((other, similarity))

        # Sort by similarity and return top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]

    def _calculate_readability(self, text: str) -> tuple[float | None, str | None]:
        """Calculate readability score and label using textstat."""
        cleaned = text.strip()
        if not cleaned:
            return None, None

        try:
            score = float(textstat.flesch_reading_ease(cleaned))
        except Exception:
            return None, None

        if math.isnan(score):
            return None, None

        if score >= 90:
            label = "Very Easy"
        elif score >= 80:
            label = "Easy"
        elif score >= 70:
            label = "Fairly Easy"
        elif score >= 60:
            label = "Standard"
        elif score >= 50:
            label = "Fairly Difficult"
        elif score >= 30:
            label = "Difficult"
        else:
            label = "Very Difficult"

        return round(score, 2), label

    def _analyze_style(self, text: str) -> str | None:
        """Analyze writing style using sentence length and lexical variety."""
        cleaned = text.strip()
        if not cleaned:
            return None

        doc = self.nlp(cleaned)
        sentences = list(doc.sents)
        tokens = [token.text for token in doc if token.is_alpha]

        if not sentences or not tokens:
            return None

        avg_sentence_length = sum(len(sent.text.split()) for sent in sentences) / len(sentences)
        lexical_diversity = len(set(token.lower() for token in tokens)) / len(tokens)

        if avg_sentence_length <= 14:
            base_style = "Brief & Accessible"
        elif avg_sentence_length <= 22:
            base_style = "Balanced Narrative"
        else:
            base_style = "In-depth Analysis"

        if lexical_diversity >= 0.65:
            descriptor = " • Rich Vocabulary"
        elif lexical_diversity <= 0.4:
            descriptor = " • Straightforward Language"
        else:
            descriptor = ""

        return f"{base_style}{descriptor}" if descriptor else base_style

    def _extract_topics(self, text: str) -> list[str]:
        """Extract topics from text using TF-IDF and keyword extraction."""
        # Common technical terms and protocols to filter out
        blacklist_terms = {
            "http",
            "https",
            "www",
            "com",
            "org",
            "net",
            "html",
            "xml",
            "json",
            "api",
            "url",
            "link",
            "href",
            "src",
            "img",
            "div",
            "span",
            "class",
            "read",
            "more",
            "click",
            "here",
            "article",
            "post",
            "page",
            "site",
            "website",
            "blog",
            "news",
            "today",
            "said",
            "says",
            "according",
            "report",
            "reports",
            "reported",
            "story",
            "stories",
            "comment",
            "comments",
            "share",
            "tweet",
            "follow",
            "subscribe",
            "newsletter",
            "theguardian",
            "nytimes",
            "bbc",
            "cnn",
            "reuters",
            "bloomberg",  # News sources
            "jpeg",
            "jpg",
            "png",
            "gif",
            "pdf",
            "svg",  # File formats
        }

        # Use TF-IDF for better keyword extraction
        try:
            # Create TF-IDF vectorizer with custom parameters
            vectorizer = TfidfVectorizer(
                max_features=20,
                stop_words="english",
                ngram_range=(1, 2),  # Include both unigrams and bigrams
                min_df=1,
                lowercase=True,
                token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z]+\b",  # Only words, no numbers
            )

            # Fit and transform the text
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()

            # Get TF-IDF scores
            tfidf_scores = tfidf_matrix.toarray()[0]

            # Get top keywords by TF-IDF score, filter blacklist
            top_indices = tfidf_scores.argsort()[-15:][::-1]
            tfidf_topics = [
                feature_names[i]
                for i in top_indices
                if tfidf_scores[i] > 0 and feature_names[i] not in blacklist_terms
            ][:10]

        except Exception:
            # Fallback to simple frequency-based extraction
            tfidf_topics = self._extract_topics_fallback(text)

        # Add some basic categorization based on keywords
        categories = self._categorize_text(text)

        # Combine TF-IDF topics and categories, remove duplicates and blacklisted
        all_topics = [
            topic
            for topic in list(set(tfidf_topics + categories))
            if topic not in blacklist_terms
            and not any(char in topic for char in ["/", ".", "@", "#"])  # Filter URL/email patterns
            and not any(
                word in topic.lower() for word in ["http", "https", "www", "url", "link"]
            )  # Filter URL-related terms
            and len(topic) > 2  # Filter very short terms
            and not topic.replace(" ", "").isdigit()  # Filter pure numbers
        ]

        return all_topics[:15]  # Return top 15 topics

    def _extract_topics_fallback(self, text: str) -> list[str]:
        """Fallback topic extraction using word frequency."""
        # Common stop words to filter out
        stop_words = {
            "the",
            "be",
            "to",
            "of",
            "and",
            "a",
            "in",
            "that",
            "have",
            "i",
            "it",
            "for",
            "not",
            "on",
            "with",
            "he",
            "as",
            "you",
            "do",
            "at",
            "this",
            "but",
            "his",
            "by",
            "from",
            "they",
            "we",
            "say",
            "her",
            "she",
            "or",
            "an",
            "will",
            "my",
            "one",
            "all",
            "would",
            "there",
            "their",
            "what",
            "so",
            "up",
            "out",
            "if",
            "about",
            "who",
            "get",
            "which",
            "go",
            "me",
            "when",
            "make",
            "can",
            "like",
            "time",
            "no",
            "just",
            "him",
            "know",
            "take",
            "people",
            "into",
            "year",
            "your",
            "good",
            "some",
            "could",
            "them",
            "see",
            "other",
            "than",
            "then",
            "now",
            "look",
            "only",
            "come",
            "its",
            "over",
            "think",
            "also",
            "back",
            "after",
            "use",
            "two",
            "how",
            "our",
            "work",
            "first",
            "well",
            "way",
            "even",
            "new",
            "want",
            "because",
            "any",
            "these",
            "give",
            "day",
            "most",
            "us",
            "is",
            "was",
            "are",
            "been",
            "has",
            "had",
            "were",
            "said",
            "did",
            "having",
            "may",
            "such",
            "being",
            "here",
            "should",
            # Technical terms
            "http",
            "https",
            "www",
            "com",
            "org",
            "net",
            "html",
            "xml",
            "json",
            "read",
            "more",
            "click",
            "here",
            "article",
            "post",
            "page",
            "site",
            "website",
            "blog",
            "news",
            "today",
            "according",
            "report",
            "story",
        }

        # Remove punctuation and convert to lowercase
        text = re.sub(r"[^\w\s]", " ", text.lower())

        # Split into words and filter
        words = text.split()

        # Filter words: remove stop words, short words, numbers
        filtered_words = [
            word
            for word in words
            if word not in stop_words and len(word) > 3 and not word.isdigit()
        ]

        # Get most common words as topics
        word_counts = Counter(filtered_words)
        return [word for word, _ in word_counts.most_common(10)]

    def _categorize_text(self, text: str) -> list[str]:
        """Categorize text based on keywords."""
        categories = []

        # Define category keywords
        category_keywords = {
            "technology": [
                "tech",
                "software",
                "hardware",
                "computer",
                "digital",
                "internet",
                "online",
                "cyber",
                "data",
                "cloud",
                "app",
                "smartphone",
                "device",
            ],
            "ai": [
                "artificial intelligence",
                "machine learning",
                "neural",
                "deep learning",
                "chatgpt",
                "openai",
                "anthropic",
                "claude",
                "gpt",
                "model",
                "llm",
                "transformer",
            ],
            "business": [
                "business",
                "company",
                "corporate",
                "market",
                "stock",
                "investment",
                "finance",
                "economy",
                "trade",
                "industry",
                "startup",
                "enterprise",
            ],
            "politics": [
                "politics",
                "government",
                "election",
                "president",
                "congress",
                "senate",
                "policy",
                "legislation",
                "political",
                "democrat",
                "republican",
                "vote",
            ],
            "science": [
                "science",
                "research",
                "study",
                "scientist",
                "discovery",
                "experiment",
                "university",
                "journal",
                "academic",
                "laboratory",
            ],
            "health": [
                "health",
                "medical",
                "disease",
                "patient",
                "doctor",
                "hospital",
                "medicine",
                "treatment",
                "vaccine",
                "virus",
                "healthcare",
                "wellness",
            ],
            "sports": [
                "sports",
                "game",
                "player",
                "team",
                "coach",
                "league",
                "championship",
                "football",
                "basketball",
                "baseball",
                "soccer",
                "tennis",
            ],
            "entertainment": [
                "movie",
                "film",
                "music",
                "actor",
                "celebrity",
                "entertainment",
                "hollywood",
                "concert",
                "album",
                "show",
                "series",
                "netflix",
            ],
            "security": [
                "security",
                "cybersecurity",
                "breach",
                "hack",
                "vulnerability",
                "attack",
                "malware",
                "ransomware",
                "encryption",
                "privacy",
                "password",
            ],
        }

        text_lower = text.lower()

        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)

        return categories

    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score using VADER."""
        # VADER returns a dictionary with neg, neu, pos, and compound scores
        # compound score is a normalized score between -1 (most negative) and 1 (most positive)
        scores = self.sentiment_analyzer.polarity_scores(text)
        return scores["compound"]
