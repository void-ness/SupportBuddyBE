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
            f"You are an HR expert with deep knowledge of compensation trends, employee appraisals, and promotion criteria. "
            f"Evaluate the following employee profile and provide a clear, reasoned assessment:\n\n"
            f"Company: {data.company}\n"
            f"Designation: {data.designation}\n"
            f"Total Years of Experience: {data.totalYoE}\n"
            f"Years in Current Role: {data.designationYoE}\n"
            f"Performance Rating (out of 5): {data.performanceRating}\n"
            f"Employment Type: {data.employmentType} (e.g., Full-time, Contract)\n"
            f"Current CTC: {data.currentCTC}\n\n"
            f"The employee is being considered for an annual appraisal and a potential promotion.\n\n"
            f"Based on industry standards, performance, and experience, answer the following:\n"
            f"1. What is the likelihood of the employee receiving a promotion?\n"
            f"2. What is the minimum and maximum expected salary hike percentage?\n"
        )

        try:
            result = await GenAIManager.generate(prompt)
            result = result.model_dump()

            return PredictionOutput(
                promotion_likelihood=result.get("promotion_likelihood", True),
                min_hike=result.get("min_hike", random.randint(5, 10)),
                max_hike=result.get("max_hike", random.randint(10, 20)),
                confidence_score=result.get("confidence_score", round(random.uniform(0.5, 1.0), 2))
            )
        except Exception as e:
            logger.error("GenAI prediction failed, falling back to original prediction method: %s", e)
            return cls.predict_promotion(data)