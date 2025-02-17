from models import PredictionInput, PredictionOutput
import random

class PredictionManager:
    
    @classmethod
    def predict_promotion(cls, data: PredictionInput) -> PredictionOutput:
        # Example basic logic - this should be replaced with your ML model
        promotion_score = 0

        # Basic scoring based on years of experience
        if data.designationYoE >= 2:
            promotion_score += 0.3

        # Experience ratio impact
        exp_ratio = data.designationYoE / data.totalYoE if data.totalYoE > 0 else 0
        if exp_ratio > 0.5:
            promotion_score += 0.2

        # Calculate hike ranges based on current CTC
        base_hike = 0.10  # 10% base hike
        if promotion_score > 0.5:
            min_hike = base_hike + 0.05
            max_hike = base_hike + 0.15
        else:
            min_hike = base_hike
            max_hike = base_hike + 0.08

        return PredictionOutput(
            promotion_likelihood=promotion_score > 0.5,
            min_hike=round(min_hike * 100, 2),  # Convert to percentage
            max_hike=round(max_hike * 100, 2),
            confidence_score=round(min(abs(promotion_score - 0.5) * 2, 1.0), 2)
        )
    
    @classmethod
    async def predict_promotion_with_genai(cls, data: PredictionInput) -> PredictionOutput:
        from managers import GenAIManager

        prompt = f"An Employee working at {data.company} as a {data.designation} with {data.totalYoE} years of experience in total, working in this role from {data.designationYoE} years and a performance rating of {data.performanceRating} is likely to get a promotion?"

        result = await GenAIManager.generate(prompt)
        result = result.model_dump()

        return PredictionOutput(
            promotion_likelihood=result.get("promotion_likelihood", True),
            min_hike=result.get("min_hike", random.randint(5, 10)),
            max_hike=result.get("max_hike", random.randint(10, 20)),
            confidence_score=result.get("confidence_score", 0.82)
        )