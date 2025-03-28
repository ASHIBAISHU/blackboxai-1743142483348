from pydantic import BaseModel, Field, validator
from typing import Optional, List

class LeadInput(BaseModel):
    company_name: str
    company_size: int = Field(..., gt=0)
    annual_revenue: float = Field(..., gt=0)
    num_employees: int = Field(..., gt=0)
    industry: str
    lead_source: str
    past_interactions: int = Field(0, ge=0)
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

    @validator('industry')
    def validate_industry(cls, v):
        valid_industries = ['logistics', 'manufacturing', 'retail', 'technology', 'finance']
        if v.lower() not in valid_industries:
            raise ValueError(f"Industry must be one of: {', '.join(valid_industries)}")
        return v.lower()

class LeadPredictionOutput(BaseModel):
    score: float = Field(..., ge=0, le=1)
    prediction: bool
    needs_human_review: bool
    confidence: float = Field(..., ge=0, le=1)
    voice_response: Optional[str] = None
    explanation: Optional[dict] = None

class FeedbackInput(BaseModel):
    lead_id: str
    prediction_score: float = Field(..., ge=0, le=1)
    actual_outcome: bool
    feedback_notes: Optional[str] = None
    accuracy_rating: int = Field(..., ge=1, le=5)

class BatchPredictionInput(BaseModel):
    leads: List[LeadInput]
    include_voice: bool = False
    include_explanation: bool = False