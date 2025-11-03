"""Prompt template library for LLM processing."""

from sqlalchemy.orm import Session

from app.models.rule import PromptTemplate


class PromptLibrary:
    """Manage prompt templates."""

    def __init__(self, db: Session):
        """Initialize prompt library."""
        self.db = db

    def create_default_prompts(self) -> list[PromptTemplate]:
        """Create default prompt templates."""
        prompts = [
            self._summarize_prompt(),
            self._extract_key_points_prompt(),
            self._sentiment_analysis_prompt(),
            self._fact_check_prompt(),
            self._eli5_prompt(),
            self._technical_depth_prompt(),
            self._bias_detection_prompt(),
            self._topic_classification_prompt(),
        ]

        for prompt in prompts:
            existing = (
                self.db.query(PromptTemplate).filter(PromptTemplate.name == prompt.name).first()
            )
            if not existing:
                self.db.add(prompt)

        self.db.commit()
        return prompts

    def _summarize_prompt(self) -> PromptTemplate:
        """Summarization prompt."""
        return PromptTemplate(
            name="Summarize Article",
            description="Generate a concise summary of the article",
            category="summarization",
            prompt_text="""Summarize the following article in 2-3 sentences. Focus on the main points and key takeaways.

Title: {title}

Content: {content}

Provide a clear, concise summary:""",
            variables=["title", "content"],
            output_format="text",
            is_public=True,
        )

    def _extract_key_points_prompt(self) -> PromptTemplate:
        """Key points extraction prompt."""
        return PromptTemplate(
            name="Extract Key Points",
            description="Extract main points as bullet list",
            category="extraction",
            prompt_text="""Extract the key points from this article as a bullet list. Focus on actionable insights and important information.

Title: {title}

Content: {content}

Key Points:
-""",
            variables=["title", "content"],
            output_format="text",
            is_public=True,
        )

    def _sentiment_analysis_prompt(self) -> PromptTemplate:
        """Sentiment analysis prompt."""
        return PromptTemplate(
            name="Analyze Sentiment",
            description="Determine the sentiment and tone of the article",
            category="analysis",
            prompt_text="""Analyze the sentiment and tone of this article.

Title: {title}

Content: {content}

Provide:
1. Overall sentiment (positive/negative/neutral)
2. Tone (formal/informal/technical/conversational/etc.)
3. Key emotions present
4. Brief explanation (1-2 sentences)

Format as JSON:""",
            variables=["title", "content"],
            output_format="json",
            is_public=True,
        )

    def _fact_check_prompt(self) -> PromptTemplate:
        """Fact checking prompt."""
        return PromptTemplate(
            name="Fact Check Claims",
            description="Identify and verify factual claims",
            category="analysis",
            prompt_text="""Identify the main factual claims in this article and assess their verifiability.

Title: {title}

Content: {content}

For each claim:
1. State the claim
2. Assess if it's verifiable (yes/no/unclear)
3. Note any red flags or concerns

Format as JSON array:""",
            variables=["title", "content"],
            output_format="json",
            is_public=True,
        )

    def _eli5_prompt(self) -> PromptTemplate:
        """ELI5 (Explain Like I'm 5) prompt."""
        return PromptTemplate(
            name="ELI5 Explanation",
            description="Explain complex topics in simple terms",
            category="summarization",
            prompt_text="""Explain this article in simple terms that a non-technical person can understand. Avoid jargon and use analogies where helpful.

Title: {title}

Content: {content}

Simple explanation:""",
            variables=["title", "content"],
            output_format="text",
            is_public=True,
        )

    def _technical_depth_prompt(self) -> PromptTemplate:
        """Technical depth analysis prompt."""
        return PromptTemplate(
            name="Technical Depth Analysis",
            description="Assess technical complexity and depth",
            category="analysis",
            prompt_text="""Analyze the technical depth of this article.

Title: {title}

Content: {content}

Provide:
1. Technical level (beginner/intermediate/advanced/expert)
2. Main technologies/concepts discussed
3. Prerequisites needed to understand
4. Target audience

Format as JSON:""",
            variables=["title", "content"],
            output_format="json",
            is_public=True,
        )

    def _bias_detection_prompt(self) -> PromptTemplate:
        """Bias detection prompt."""
        return PromptTemplate(
            name="Detect Bias",
            description="Identify potential bias in the article",
            category="analysis",
            prompt_text="""Analyze this article for potential bias or one-sided perspectives.

Title: {title}

Content: {content}
Author: {author}

Identify:
1. Any clear biases or agenda
2. Missing perspectives
3. Loaded language or framing
4. Overall objectivity score (1-10)

Format as JSON:""",
            variables=["title", "content", "author"],
            output_format="json",
            is_public=True,
        )

    def _topic_classification_prompt(self) -> PromptTemplate:
        """Topic classification prompt."""
        return PromptTemplate(
            name="Classify Topics",
            description="Classify article into relevant topics/categories",
            category="extraction",
            prompt_text="""Classify this article into relevant topics and categories.

Title: {title}

Content: {content}

Provide:
1. Primary category (e.g., Technology, Business, Science, etc.)
2. 3-5 specific topics/tags
3. Industry/field if applicable
4. Confidence level for each (1-10)

Format as JSON:""",
            variables=["title", "content"],
            output_format="json",
            is_public=True,
        )
