from models import PredictionInput, PredictionOutput
import random
import logging

logger = logging.getLogger(__name__)

class PredictionManager:
    
    @classmethod
    def predict_promotion(cls, data: PredictionInput) -> PredictionOutput:
        # Improved logic for promotion prediction
        promotion_score = 0

        # Basic scoring based on years of experience
        if data.designationYoE >= 2:
            promotion_score += 0.3

        # Experience ratio impact
        exp_ratio = data.designationYoE / data.totalYoE if data.totalYoE > 0 else 0
        if exp_ratio > 0.5:
            promotion_score += 0.2

        # Performance rating impact
        rating_map = {
            "Needs Improvement": 0.1,
            "Meets Expectations": 0.3,
            "Exceeds Expectations": 0.5,
            "Outstanding": 0.7
        }
        promotion_score += rating_map.get(data.performanceRating, 0.3)

        # Calculate hike ranges based on current CTC and promotion score
        base_hike = 0.10  # 10% base hike
        if promotion_score > 0.5:
            min_hike = base_hike + (promotion_score - 0.5) * 0.1
            max_hike = base_hike + 0.15 + (promotion_score - 0.5) * 0.2
        else:
            min_hike = base_hike + promotion_score * 0.1
            max_hike = base_hike + 0.08 + promotion_score * 0.1

        return PredictionOutput(
            promotion_likelihood=promotion_score > 0.5,
            min_hike=round(min_hike * 100, 2),  # Convert to percentage
            max_hike=round(max_hike * 100, 2),
            confidence_score=round(min(abs(promotion_score - 0.5) * 2, 1.0), 2)
        )
    
    @classmethod
    async def predict_promotion_with_genai(cls, data: PredictionInput) -> PredictionOutput:
        from managers import GenAIManager

        prompt = (
            f"An employee working at {data.company} as a {data.designation} with {data.totalYoE} years of total experience, "
            f"{data.designationYoE} years in the current role, and a performance rating of {data.performanceRating} "
            f"is being considered for a promotion. The employee's current CTC is {data.currentCTC}. "
            f"Based on this information, what is the likelihood of the employee getting a promotion, "
            f"and what would be the expected minimum and maximum salary hike percentages?"
        )

        try:
            result = await GenAIManager.generate(prompt)
            result = result.model_dump()

            return PredictionOutput(
                promotion_likelihood=result.get("promotion_likelihood", True),
                min_hike=result.get("min_hike", random.randint(5, 10)),
                max_hike=result.get("max_hike", random.randint(10, 20)),
                confidence_score=result.get("confidence_score", 0.82)
            )
        except Exception as e:
            logger.error("GenAI prediction failed, falling back to original prediction method: %s", e)
            return cls.predict_promotion(data)