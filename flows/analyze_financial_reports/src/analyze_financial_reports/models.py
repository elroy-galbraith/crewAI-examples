from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
import json


class ResearchQuestion(BaseModel):
    """A research question generated during portfolio manager-analyst conversation."""
    question: str
    category: str  # e.g., "Industry Analysis", "Financial Ratios", "Growth Metrics"
    priority: str = "medium"  # low, medium, high


class QuestionsList(BaseModel):
    """Collection of research questions."""
    questions: List[ResearchQuestion]


class ReportSection(BaseModel):
    """An individual section of the financial report."""
    title: str
    description: str
    required_tools: List[str] = Field(
        default_factory=list,
        description="Tools needed: financial_rag, ratio_calculator, web_search, visualization"
    )
    order: int = 1


class ReportOutline(BaseModel):
    """Complete outline for the financial report."""
    sections: List[ReportSection]


class FinancialData(BaseModel):
    """Financial data and calculations for a report section."""
    model_config = ConfigDict(extra='forbid')
    
    section_title: str
    metrics: str = Field(default="", description="JSON string of metrics data")
    calculations: str = Field(default="", description="JSON string of calculations")
    visualizations: List[str] = Field(
        default_factory=list,
        description="Paths to generated visualization files"
    )
    research_notes: str = ""
    
    @field_validator('metrics', 'calculations', mode='before')
    @classmethod
    def convert_dict_to_json(cls, v):
        """
        Convert dict to JSON string if LLM returns dict instead of string.
        This makes the model more forgiving of LLM output format variations.
        """
        if isinstance(v, dict):
            return json.dumps(v)
        if v is None:
            return ""
        return str(v)


class CompletedSection(BaseModel):
    """A completed report section with all content."""
    title: str
    content: str  # Markdown formatted content
    order: int


class CompanyScore(BaseModel):
    """Final score and evaluation of the company."""
    model_config = ConfigDict(extra='forbid')
    
    company_name: str
    overall_score: float = Field(ge=0, le=100)
    category_scores: str = Field(default="", description="JSON string of category scores")
    meets_criteria: bool
    recommendation: str  # "Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"
    key_strengths: List[str] = Field(default_factory=list)
    key_concerns: List[str] = Field(default_factory=list)
    summary: str = ""
    
    @field_validator('category_scores', mode='before')
    @classmethod
    def convert_dict_to_json(cls, v):
        """
        Convert dict to JSON string if LLM returns dict instead of string.
        This makes the model more forgiving of LLM output format variations.
        """
        if isinstance(v, dict):
            return json.dumps(v)
        if v is None:
            return ""
        return str(v)


class InvestmentPersona(BaseModel):
    """Investment strategy and criteria."""
    model_config = ConfigDict(extra='allow')  # Allow extra fields for rich persona configs
    
    name: str
    strategy_type: str  # "Value", "Growth", "Dividend", "GARP", etc.
    key_metrics: List[str] = Field(default_factory=list)
    criteria: str = Field(default="", description="JSON string of investment criteria")
    risk_tolerance: str = "medium"  # low, medium, high
    time_horizon: str = "long-term"  # short-term, medium-term, long-term
    
    # Optional fields that may be in YAML files
    description: Optional[str] = None
    investment_philosophy: Optional[str] = None
    jse_specific_considerations: Optional[Dict[str, Any]] = None  # For JSE-specific data
    
    @field_validator('criteria', mode='before')
    @classmethod
    def convert_dict_to_json(cls, v):
        """
        Convert dict to JSON string if needed.
        This makes the model more forgiving of input format variations.
        """
        if isinstance(v, dict):
            return json.dumps(v)
        if v is None:
            return ""
        return str(v)
