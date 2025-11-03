"""Feed template library with ready-made presets."""

from sqlalchemy.orm import Session

from app.models.rule import FeedTemplate


class TemplateLibrary:
    """Manage feed templates."""

    def __init__(self, db: Session):
        """Initialize template library."""
        self.db = db

    def create_default_templates(self) -> list[FeedTemplate]:
        """Create default feed templates."""
        templates = [
            self._tech_news_template(),
            self._ai_ml_research_template(),
            self._startup_news_template(),
            self._security_news_template(),
            self._dev_blogs_template(),
            self._product_hunt_template(),
            self._hacker_news_template(),
            self._reddit_programming_template(),
        ]

        for template in templates:
            existing = (
                self.db.query(FeedTemplate).filter(FeedTemplate.name == template.name).first()
            )
            if not existing:
                self.db.add(template)

        self.db.commit()
        return templates

    def _tech_news_template(self) -> FeedTemplate:
        """Tech news template."""
        return FeedTemplate(
            name="Tech News Essentials",
            description="Curated tech news from top sources with AI filtering",
            category="Technology",
            icon="💻",
            suggested_feeds=[
                "https://techcrunch.com/feed/",
                "https://www.theverge.com/rss/index.xml",
                "https://arstechnica.com/feed/",
                "https://www.wired.com/feed/rss",
            ],
            rules=[
                {
                    "name": "Hide clickbait",
                    "rule_type": "filter",
                    "conditions": [
                        {
                            "field": "title",
                            "operator": "matches_regex",
                            "value": r"(You won't believe|This one trick|Shocking)",
                        }
                    ],
                    "actions": [{"type": "hide"}],
                },
                {
                    "name": "Star breaking news",
                    "rule_type": "priority",
                    "conditions": [
                        {
                            "field": "title",
                            "operator": "contains",
                            "value": "breaking",
                        }
                    ],
                    "actions": [{"type": "star"}, {"type": "set_priority", "value": 10}],
                },
                {
                    "name": "Tag AI articles",
                    "rule_type": "category",
                    "conditions": [
                        {
                            "field": "title",
                            "operator": "matches_regex",
                            "value": r"\b(AI|artificial intelligence|machine learning|GPT|LLM)\b",
                        }
                    ],
                    "actions": [{"type": "add_tag", "value": "AI"}],
                },
            ],
            preferences={
                "enable_recommendations": True,
                "min_relevance_score": 0.6,
                "preferred_topics": ["AI", "startups", "programming"],
            },
            is_public=True,
        )

    def _ai_ml_research_template(self) -> FeedTemplate:
        """AI/ML research template."""
        return FeedTemplate(
            name="AI/ML Research",
            description="Academic papers and research in AI/ML",
            category="Research",
            icon="🧠",
            suggested_feeds=[
                "http://export.arxiv.org/rss/cs.AI",
                "http://export.arxiv.org/rss/cs.LG",
                "http://export.arxiv.org/rss/cs.CL",
                "https://distill.pub/rss.xml",
            ],
            rules=[
                {
                    "name": "Extract paper entities",
                    "rule_type": "extract",
                    "conditions": [],
                    "actions": [{"type": "extract_entities"}],
                },
                {
                    "name": "Summarize abstracts",
                    "rule_type": "summarize",
                    "conditions": [],
                    "actions": [{"type": "summarize"}],
                },
                {
                    "name": "Tag by subfield",
                    "rule_type": "category",
                    "conditions": [
                        {
                            "field": "content",
                            "operator": "contains",
                            "value": "transformer",
                        }
                    ],
                    "actions": [{"type": "add_tag", "value": "transformers"}],
                },
            ],
            preferences={
                "enable_recommendations": True,
                "preferred_topics": [
                    "transformers",
                    "reinforcement learning",
                    "computer vision",
                ],
            },
            is_public=True,
        )

    def _startup_news_template(self) -> FeedTemplate:
        """Startup news template."""
        return FeedTemplate(
            name="Startup Ecosystem",
            description="Funding, acquisitions, and startup news",
            category="Business",
            icon="🚀",
            suggested_feeds=[
                "https://techcrunch.com/startups/feed/",
                "https://news.crunchbase.com/feed/",
            ],
            rules=[
                {
                    "name": "Star funding announcements",
                    "rule_type": "priority",
                    "conditions": [
                        {
                            "field": "title",
                            "operator": "matches_regex",
                            "value": r"(raises|funding|Series [A-D]|million|billion)",
                        }
                    ],
                    "actions": [
                        {"type": "star"},
                        {"type": "add_tag", "value": "funding"},
                    ],
                },
                {
                    "name": "Tag by stage",
                    "rule_type": "category",
                    "conditions": [
                        {
                            "field": "content",
                            "operator": "contains",
                            "value": "Series A",
                        }
                    ],
                    "actions": [{"type": "add_tag", "value": "Series-A"}],
                },
            ],
            preferences={
                "preferred_topics": ["funding", "YC", "acquisitions"],
            },
            is_public=True,
        )

    def _security_news_template(self) -> FeedTemplate:
        """Security news template."""
        return FeedTemplate(
            name="Cybersecurity News",
            description="Security vulnerabilities, threats, and updates",
            category="Security",
            icon="🔐",
            suggested_feeds=[
                "https://feeds.feedburner.com/TheHackersNews",
                "https://krebsonsecurity.com/feed/",
                "https://www.schneier.com/feed/atom/",
            ],
            rules=[
                {
                    "name": "Star critical vulnerabilities",
                    "rule_type": "priority",
                    "conditions": [
                        {
                            "field": "title",
                            "operator": "matches_regex",
                            "value": r"(critical|zero-day|CVE-|vulnerability)",
                        }
                    ],
                    "actions": [{"type": "star"}, {"type": "add_tag", "value": "critical"}],
                },
                {
                    "name": "Tag by threat type",
                    "rule_type": "category",
                    "conditions": [
                        {
                            "field": "content",
                            "operator": "contains",
                            "value": "ransomware",
                        }
                    ],
                    "actions": [{"type": "add_tag", "value": "ransomware"}],
                },
            ],
            preferences={
                "preferred_topics": ["vulnerabilities", "exploits", "patches"],
            },
            is_public=True,
        )

    def _dev_blogs_template(self) -> FeedTemplate:
        """Developer blogs template."""
        return FeedTemplate(
            name="Developer Blogs",
            description="Engineering blogs from top tech companies",
            category="Engineering",
            icon="👨‍💻",
            suggested_feeds=[
                "https://engineering.fb.com/feed/",
                "https://netflixtechblog.com/feed",
                "https://aws.amazon.com/blogs/aws/feed/",
                "https://blog.cloudflare.com/rss/",
            ],
            rules=[
                {
                    "name": "Tag by technology",
                    "rule_type": "category",
                    "conditions": [
                        {
                            "field": "content",
                            "operator": "contains",
                            "value": "kubernetes",
                        }
                    ],
                    "actions": [{"type": "add_tag", "value": "kubernetes"}],
                },
                {
                    "name": "Extract code examples",
                    "rule_type": "extract",
                    "conditions": [],
                    "actions": [{"type": "extract_entities"}],
                },
            ],
            preferences={
                "preferred_topics": ["architecture", "scalability", "infrastructure"],
            },
            is_public=True,
        )

    def _product_hunt_template(self) -> FeedTemplate:
        """Product Hunt template."""
        return FeedTemplate(
            name="Product Hunt Daily",
            description="New product launches and trending products",
            category="Products",
            icon="🎯",
            suggested_feeds=[],
            rules=[
                {
                    "name": "Star top products",
                    "rule_type": "priority",
                    "conditions": [
                        {
                            "field": "title",
                            "operator": "contains",
                            "value": "Product of the Day",
                        }
                    ],
                    "actions": [{"type": "star"}],
                },
            ],
            preferences={
                "preferred_topics": ["SaaS", "productivity", "AI tools"],
            },
            is_public=True,
        )

    def _hacker_news_template(self) -> FeedTemplate:
        """Hacker News template."""
        return FeedTemplate(
            name="Hacker News Curated",
            description="Top stories from Hacker News with smart filtering",
            category="Community",
            icon="🔶",
            suggested_feeds=[
                "https://hnrss.org/frontpage",
                "https://hnrss.org/best",
            ],
            rules=[
                {
                    "name": "Hide meta discussions",
                    "rule_type": "filter",
                    "conditions": [
                        {
                            "field": "title",
                            "operator": "matches_regex",
                            "value": r"(Ask HN|Show HN|Tell HN)",
                        }
                    ],
                    "actions": [{"type": "mark_read"}],
                },
                {
                    "name": "Star high engagement",
                    "rule_type": "priority",
                    "conditions": [
                        {
                            "field": "title",
                            "operator": "matches_regex",
                            "value": r"\d{3,}",  # 100+ points
                        }
                    ],
                    "actions": [{"type": "star"}],
                },
            ],
            preferences={
                "preferred_topics": ["programming", "startups", "science"],
            },
            is_public=True,
        )

    def _reddit_programming_template(self) -> FeedTemplate:
        """Reddit programming template."""
        return FeedTemplate(
            name="Reddit r/programming",
            description="Top programming discussions from Reddit",
            category="Community",
            icon="🤖",
            suggested_feeds=[
                "https://www.reddit.com/r/programming/.rss",
                "https://www.reddit.com/r/python/.rss",
                "https://www.reddit.com/r/javascript/.rss",
            ],
            rules=[
                {
                    "name": "Hide memes",
                    "rule_type": "filter",
                    "conditions": [
                        {
                            "field": "title",
                            "operator": "matches_regex",
                            "value": r"(meme|funny|humor)",
                        }
                    ],
                    "actions": [{"type": "hide"}],
                },
                {
                    "name": "Star tutorials",
                    "rule_type": "priority",
                    "conditions": [
                        {
                            "field": "title",
                            "operator": "matches_regex",
                            "value": r"(tutorial|guide|how to|learn)",
                        }
                    ],
                    "actions": [{"type": "star"}, {"type": "add_tag", "value": "tutorial"}],
                },
            ],
            preferences={
                "preferred_topics": ["tutorials", "best practices", "tools"],
            },
            is_public=True,
        )
