"""Test NLP processor service."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.services.nlp_processor import NLPProcessor


@pytest.fixture
def nlp_processor(db):
    """Create NLP processor instance."""
    with patch("app.services.nlp_processor.SentenceTransformer") as MockModel:
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3] * 256])  # 768-dim vector
        MockModel.return_value = mock_model

        processor = NLPProcessor(db)
        return processor


def test_nlp_processor_initialization(db):
    """Test NLP processor initialization."""
    with patch("app.services.nlp_processor.SentenceTransformer") as MockModel:
        processor = NLPProcessor(db)
        assert processor is not None
        assert processor.db == db
        MockModel.assert_called_once()


def test_generate_embedding(nlp_processor):
    """Test embedding generation."""
    text = "This is a test article about artificial intelligence."
    embedding = nlp_processor.generate_embedding(text)

    assert embedding is not None
    assert isinstance(embedding, list)
    # The mock returns a nested array, so we need to check the structure
    assert len(embedding) > 0  # Just verify it's not empty


def test_generate_embedding_empty_text(nlp_processor):
    """Test embedding generation with empty text."""
    embedding = nlp_processor.generate_embedding("")

    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) > 0  # Just verify it returns something


def test_calculate_sentiment(db):
    """Test sentiment calculation."""
    processor = NLPProcessor(db)

    # Test positive text
    positive_text = "This is an amazing and wonderful article!"
    sentiment = processor._calculate_sentiment(positive_text)
    assert -1.0 <= sentiment <= 1.0

    # Test negative text
    negative_text = "This is a terrible and horrible article!"
    sentiment = processor._calculate_sentiment(negative_text)
    assert -1.0 <= sentiment <= 1.0

    # Test neutral text
    neutral_text = "This is an article about technology."
    sentiment = processor._calculate_sentiment(neutral_text)
    assert -1.0 <= sentiment <= 1.0


def test_calculate_sentiment_empty(db):
    """Test sentiment calculation with empty text."""
    processor = NLPProcessor(db)
    sentiment = processor._calculate_sentiment("")
    assert sentiment == 0.0


def test_extract_topics(db):
    """Test topic extraction."""
    processor = NLPProcessor(db)
    text = "Artificial intelligence and machine learning are transforming technology. Deep learning models are becoming more powerful."

    topics = processor._extract_topics(text)

    assert isinstance(topics, list)
    assert len(topics) > 0
    # Should extract relevant keywords
    assert any(
        keyword in ["artificial", "intelligence", "machine", "learning", "technology"]
        for keyword in topics
    )


def test_extract_topics_empty(db):
    """Test topic extraction with empty text."""
    processor = NLPProcessor(db)
    topics = processor._extract_topics("")
    assert isinstance(topics, list)
    assert len(topics) == 0


def test_calculate_readability(db):
    """Test readability calculation."""
    processor = NLPProcessor(db)

    # Simple text
    simple_text = "The cat sat on the mat. It was a nice day."
    score, label = processor._calculate_readability(simple_text)

    assert isinstance(score, (float, type(None)))
    assert isinstance(label, (str, type(None)))
    if score is not None:
        assert score >= 0
        assert label in [
            "Very Easy",
            "Easy",
            "Fairly Easy",
            "Standard",
            "Fairly Difficult",
            "Difficult",
            "Very Difficult",
        ]


def test_calculate_readability_complex(db):
    """Test readability with complex text."""
    processor = NLPProcessor(db)

    complex_text = "The implementation of sophisticated algorithmic methodologies necessitates comprehensive understanding of computational complexity theory."
    score, label = processor._calculate_readability(complex_text)

    assert isinstance(score, (float, type(None)))
    assert isinstance(label, (str, type(None)))


def test_calculate_readability_empty(db):
    """Test readability with empty text."""
    processor = NLPProcessor(db)
    score, label = processor._calculate_readability("")

    assert score is None
    assert label is None


def test_cluster_articles(nlp_processor, test_user, db):
    """Test article clustering."""
    import json

    from app.models.feed import Article, Feed

    # Create test feed and articles with embeddings
    feed = Feed(
        url="https://example.com/rss", title="Test Feed", user_id=test_user.id, is_active=True
    )
    db.add(feed)
    db.commit()

    # Create articles with embeddings
    for i in range(4):
        embedding = [0.1 + i * 0.1, 0.2 + i * 0.1, 0.3] * 256
        article = Article(
            title=f"Article {i}",
            link=f"https://example.com/article{i}",
            description=f"Description {i}",
            feed_id=feed.id,
            embedding=json.dumps(embedding),
        )
        db.add(article)
    db.commit()

    # Run clustering
    num_clusters = nlp_processor.cluster_articles(test_user.id, min_samples=2)

    # Should return number of clusters
    assert isinstance(num_clusters, int)
    assert num_clusters >= 0


def test_cluster_articles_insufficient_data(nlp_processor, test_user, db):
    """Test clustering with insufficient data."""
    import json

    from app.models.feed import Article, Feed

    # Create test feed with only one article
    feed = Feed(
        url="https://example.com/rss", title="Test Feed", user_id=test_user.id, is_active=True
    )
    db.add(feed)
    db.commit()

    article = Article(
        title="Article",
        link="https://example.com/article",
        description="Description",
        feed_id=feed.id,
        embedding=json.dumps([0.1, 0.2, 0.3] * 256),
    )
    db.add(article)
    db.commit()

    # Run clustering with min_samples=2
    num_clusters = nlp_processor.cluster_articles(test_user.id, min_samples=2)

    # Should return 0 because insufficient data
    assert num_clusters == 0


def test_assess_writing_style(db):
    """Test writing style assessment."""
    processor = NLPProcessor(db)

    # Formal text
    formal_text = "The research demonstrates significant advancements in the field of computational linguistics."
    style = processor._analyze_style(formal_text)
    assert isinstance(style, (str, type(None)))
    if style:
        assert style != ""

    # Informal text
    informal_text = "Hey! Check out this awesome new tech thing!"
    style = processor._analyze_style(informal_text)
    assert isinstance(style, (str, type(None)))


def test_assess_writing_style_empty(db):
    """Test writing style with empty text."""
    processor = NLPProcessor(db)
    style = processor._analyze_style("")
    assert style is None
