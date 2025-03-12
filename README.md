# 🏏 IPL Match Analytics & Prediction  

A Django-based web app that provides **IPL match analytics** with interactive charts and a **machine learning model** to predict match outcomes.  

## 🚀 Features  
- 📊 **Interactive IPL Dashboard** – Team and match statistics  
- 🤖 **Match Outcome Predictor** – ML model estimates win probability  
- 🔥 **REST API** – Get predictions via API calls  
- 🎯 **Tech Stack** – Django, Pandas, Scikit-learn, Seaborn

## 🎯 Project Structure  

```bash
📂 ipl-match-predictor
│── 📁 predictor              # Django App for Predictions
│   │── 📜 models.py          # ML Model Integration
│   │── 📜 views.py           # API Endpoints for Predictions
│   │── 📜 urls.py            # Routes for Prediction Page
│   │── 📜 templates/
│   │   │── prediction.html   # UI for Prediction Page
│── 📁 dashboard              # Django App for Visualizations
│   │── 📜 views.py           # Charts & Analytics
│   │── 📜 templates/
│   │   │── dashboard.html    # UI for IPL Analytics
│── 📁 static                 # Static Files (CSS, JS)
│── 📁 media                  # Stored ML Model & Images
│── 📜 manage.py              # Django Management Script
│── 📜 requirements.txt       # Dependencies
│── 📜 README.md              # Project Documentation
```

## 🏆 Machine Learning Model  
- **Pipeline:** OneHotEncoding → Logistic Regression  
- **Accuracy:** 81%  
- **Features Used:** Batting team, Bowling team, Runs left, Wickets left, etc.  
