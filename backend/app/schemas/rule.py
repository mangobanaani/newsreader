"""Rule and template schemas."""

from datetime import datetime

from pydantic import BaseModel


class RuleCondition(BaseModel):
    """Rule condition schema."""

    field: str  # title, content, author, source, etc.
    operator: str  # contains, equals, matches_regex, etc.
    value: str | int | float | list[str]


class RuleAction(BaseModel):
    """Rule action schema."""

    type: str  # hide, star, add_tag, run_prompt, etc.
    value: str | int | dict | None = None


class RuleBase(BaseModel):
    """Base rule schema."""

    name: str
    description: str | None = None
    rule_type: str
    is_active: bool = True
    priority: int = 0
    conditions: list[RuleCondition] = []
    actions: list[RuleAction] = []
    settings: dict = {}


class RuleCreate(RuleBase):
    """Rule creation schema."""

    pass


class RuleUpdate(BaseModel):
    """Rule update schema."""

    name: str | None = None
    description: str | None = None
    rule_type: str | None = None
    is_active: bool | None = None
    priority: int | None = None
    conditions: list[RuleCondition] | None = None
    actions: list[RuleAction] | None = None
    settings: dict | None = None


class Rule(RuleBase):
    """Public rule schema."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PromptTemplateBase(BaseModel):
    """Base prompt template schema."""

    name: str
    description: str | None = None
    category: str | None = None
    prompt_text: str
    is_public: bool = False
    is_active: bool = True
    variables: list[str] = []
    output_format: str = "text"


class PromptTemplateCreate(PromptTemplateBase):
    """Prompt template creation schema."""

    pass


class PromptTemplateUpdate(BaseModel):
    """Prompt template update schema."""

    name: str | None = None
    description: str | None = None
    category: str | None = None
    prompt_text: str | None = None
    is_public: bool | None = None
    is_active: bool | None = None
    variables: list[str] | None = None
    output_format: str | None = None


class PromptTemplate(PromptTemplateBase):
    """Public prompt template schema."""

    id: int
    user_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedTemplateBase(BaseModel):
    """Base feed template schema."""

    name: str
    description: str | None = None
    category: str | None = None
    icon: str | None = None
    suggested_feeds: list[str] = []
    rules: list[dict] = []
    preferences: dict = {}


class FeedTemplate(FeedTemplateBase):
    """Public feed template schema."""

    id: int
    is_public: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplyTemplateRequest(BaseModel):
    """Request to apply a feed template."""

    template_id: int
    apply_feeds: bool = True
    apply_rules: bool = True
    apply_preferences: bool = True
