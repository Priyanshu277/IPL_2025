from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import joblib
import pandas as pd

# Load trained Pipeline (Logistic Regression + OneHotEncoder)
model = joblib.load("Predictor/models/pipe.pkl")

# 🎯 Render Prediction Page
def prediction_page(request):
    return render(request, "Predictor/prediction.html")

# 🎯 API for prediction
@csrf_exempt
def predict_match_winner(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Extract raw inputs as a list
            input_df = pd.DataFrame([data]) 

            # Predict probability (pipeline handles encoding)
            win_prob = model.predict_proba(input_df)[0][1]  # Probability of batting team winning

            return JsonResponse({"batting_team_win_prob": round(win_prob * 100, 2)})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"message": "Send a POST request with JSON data."})
