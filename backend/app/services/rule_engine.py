"""Rule engine for filtering and processing articles."""

import re
from typing import Any

from sqlalchemy.orm import Session

from app.models.feed import Article
from app.models.rule import Rule


class RuleEngine:
    """Execute rules on articles."""

    def __init__(self, db: Session):
        """Initialize rule engine."""
        self.db = db

    def evaluate_condition(self, condition: dict[str, Any], article: Article) -> bool:
        """Evaluate a single condition against an article."""
        field = condition.get("field", "")
        operator = condition.get("operator", "")
        value = condition.get("value", "")

        # Get field value from article
        article_value = self._get_article_field(article, field)

        if article_value is None:
            return False

        # Convert to string for text operations
        article_value_str = str(article_value).lower()
        if isinstance(value, str):
            value = value.lower()

        # Evaluate based on operator
        if operator == "contains":
            return value in article_value_str
        elif operator == "not_contains":
            return value not in article_value_str
        elif operator == "equals":
            return article_value_str == str(value).lower()
        elif operator == "not_equals":
            return article_value_str != str(value).lower()
        elif operator == "matches_regex":
            return bool(re.search(value, article_value_str))
        elif operator == "greater_than":
            try:
                return float(article_value) > float(value)
            except (ValueError, TypeError):
                return False
        elif operator == "less_than":
            try:
                return float(article_value) < float(value)
            except (ValueError, TypeError):
                return False
        elif operator == "in_list":
            if isinstance(value, list):
                return article_value_str in [str(v).lower() for v in value]
            return False
        elif operator == "not_in_list":
            if isinstance(value, list):
                return article_value_str not in [str(v).lower() for v in value]
            return True

        return False

    def evaluate_rule(self, rule: Rule, article: Article) -> bool:
        """Evaluate if rule conditions match article."""
        if not rule.is_active:
            return False

        conditions = rule.conditions or []
        if not conditions:
            return True  # No conditions means always match

        # All conditions must be true (AND logic)
        # Could be extended to support OR logic with condition groups
        return all(self.evaluate_condition(cond, article) for cond in conditions)

    def execute_actions(self, actions: list[dict[str, Any]], article: Article) -> dict[str, Any]:
        """Execute actions on an article."""
        results = {"executed": [], "skipped": [], "errors": []}

        for action in actions:
            action_type = action.get("type", "")
            action_value = action.get("value")

            try:
                if action_type == "hide":
                    article.is_read = True
                    results["executed"].append("Hidden article")

                elif action_type == "star":
                    article.is_bookmarked = True
                    results["executed"].append("Starred article")

                elif action_type == "set_priority":
                    # Could add priority field to Article model
                    results["executed"].append(f"Set priority to {action_value}")

                elif action_type == "add_tag":
                    if article.topics is None:
                        article.topics = []
                    if action_value and action_value not in article.topics:
                        article.topics.append(action_value)
                    results["executed"].append(f"Added tag: {action_value}")

                elif action_type == "remove_tag":
                    if article.topics and action_value in article.topics:
                        article.topics.remove(action_value)
                    results["executed"].append(f"Removed tag: {action_value}")

                elif action_type == "mark_read":
                    article.is_read = True
                    results["executed"].append("Marked as read")

                elif action_type == "categorize":
                    # Could add category field or use tags
                    if article.topics is None:
                        article.topics = []
                    if action_value:
                        article.topics.append(f"category:{action_value}")
                    results["executed"].append(f"Categorized as: {action_value}")

                else:
                    results["skipped"].append(f"Unknown action type: {action_type}")

            except Exception as e:
                results["errors"].append(f"Error executing {action_type}: {str(e)}")

        return results

    def apply_rule(self, rule: Rule, article: Article) -> dict[str, Any]:
        """Apply a rule to an article."""
        if not self.evaluate_rule(rule, article):
            return {"matched": False}

        actions = rule.actions or []
        action_results = self.execute_actions(actions, article)

        return {
            "matched": True,
            "rule_id": rule.id,
            "rule_name": rule.name,
            "actions": action_results,
        }

    def apply_all_rules(self, user_id: int, article: Article) -> list[dict[str, Any]]:
        """Apply all user's rules to an article."""
        rules = (
            self.db.query(Rule)
            .filter(Rule.user_id == user_id, Rule.is_active.is_(True))
            .order_by(Rule.priority.desc())
            .all()
        )

        results = []
        for rule in rules:
            result = self.apply_rule(rule, article)
            if result["matched"]:
                results.append(result)

                # Check if we should skip further processing
                for action in rule.actions or []:
                    if action.get("type") == "skip":
                        break

        if results:
            self.db.commit()

        return results

    def _get_article_field(self, article: Article, field: str) -> Any:
        """Get field value from article."""
        field_map = {
            "title": article.title,
            "content": article.content or article.description,
            "description": article.description,
            "author": article.author,
            "link": article.link,
            "sentiment": article.sentiment_score,
            "topics": article.topics,
        }

        return field_map.get(field)
