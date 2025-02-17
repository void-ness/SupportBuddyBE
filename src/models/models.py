from pydantic import BaseModel
from typing import Optional, Any, Union

# Input model
class PredictionInput(BaseModel):
    company: Optional[str]
    designation: Optional[str]
    currentCTC: Optional[float]
    totalYoE: Optional[float]
    designationYoE: Optional[float]
    performanceRating: Optional[str]

# Output model
class PredictionOutput(BaseModel):
    promotion_likelihood: bool
    min_hike: float
    max_hike: float
    confidence_score: float