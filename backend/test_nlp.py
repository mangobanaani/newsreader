#!/usr/bin/env python3
"""Test NLP processing."""

import os
os.environ['DATABASE_URL'] = 'sqlite:///./dev.db'
os.environ['SECRET_KEY'] = 'test-key'

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Test VADER sentiment
analyzer = SentimentIntensityAnalyzer()
text = "OpenAI and Amazon ink $38B cloud computing deal"
scores = analyzer.polarity_scores(text)
print(f"Text: {text}")
print(f"Sentiment scores: {scores}")
print(f"Compound score: {scores['compound']}")
