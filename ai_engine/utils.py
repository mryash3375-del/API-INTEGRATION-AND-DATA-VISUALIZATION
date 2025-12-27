# Simulating AI behavior since I don't have API keys
import random

def get_recommendations(user_id, context=None):
    """
    Mock AI recommendation engine.
    In production, this would call OpenAI/Gemini with user history and menu embeddings.
    """
    # Simulate processing delay or API call
    # Logic: return random menu items (mock IDs)
    return [
        {"id": 1, "name": "Spicy Chicken Pizza", "score": 0.95},
        {"id": 5, "name": "Veggie Burger", "score": 0.88},
        {"id": 12, "name": "Pasta Alfredo", "score": 0.82}
    ]

def predict_demand(restaurant_id):
    """
    Mock Demand Prediction.
    Returns predicted order count for next hour.
    """
    return random.randint(5, 50)
