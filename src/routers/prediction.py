from fastapi import APIRouter, HTTPException, Request
from models import PredictionInput, PredictionOutput
from managers import PredictionManager, GenAIManager
from utils import strip_values, connect_with_neondb

router = APIRouter()

@router.post("/predict", response_model=PredictionOutput)
async def get_prediction(data: PredictionInput):
    try:
        print("data received", data)
        
        # Define size limits for fields
        size_limits = {
            "company": 255,
            "designation": 255,
            "performanceRating": 50
        }
        
        # Strip values if they exceed the size limits
        data = strip_values(data, size_limits)
        
        # Store the input data
        conn = connect_with_neondb()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO predictions (
                company, designation, current_ctc, 
                total_yoe, designation_yoe, performance_rating
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data.company, data.designation, data.currentCTC,
            data.totalYoE, data.designationYoE, data.performanceRating
        ))

        conn.commit()
        cur.close()
        conn.close()

        # Get prediction
        # prediction = PredictionManager.predict_promotion(data)
        prediction = await PredictionManager.predict_promotion_with_genai(data)

        return prediction
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/genai-generate")
async def genai_generate(request: Request):
    try:
        body = await request.json()
        prompt = body.get("prompt")
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        result = await GenAIManager.generate(prompt)
        return {"response": result}
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=str(e))