from fastapi import FastAPI, Query
from typing import Optional
import pandas as pd
from database import load_all_tickets
import uvicorn

app = FastAPI(
    title="Sikika AI Data Gateway",
    description="Strategic API for Nairobi Infrastructure & Risk Intelligence.",
    version="1.0.0"
)

@app.get("/", tags=["System"])
def root():
    return {"status": "Operational", "documentation": "/docs", "version": "1.0.0"}

# --- THE DATA SALE ENDPOINT ---
@app.get("/v1/grievances", tags=["Integration Layer"])
def get_grievances(
    sub_county: Optional[str] = Query(None, description="Filter results by Sub-county"),
    status: Optional[str] = Query(None, description="Filter by status (Open, In Progress, Resolved)")
):
    data = load_all_tickets()
    if sub_county:
        data = [t for t in data if t.get('Sub-county', '').lower() == sub_county.lower()]
    if status:
        data = [t for t in data if t.get('Status', '').lower() == status.lower()]
    return data

# --- THE BI & MONETIZATION ENDPOINT ---
@app.get("/v1/analytics/risk-intelligence", tags=["Monetization Layer"])
def get_risk_intelligence():
    """Provides high-level risk scoring for insurance and logistics partners."""
    data = load_all_tickets()
    if not data: return {"error": "Empty database"}
    
    df = pd.DataFrame(data)
    
    # Calculate Risk Score: Critical is weighted 3x, High is 2x
    risk_scores = df.groupby('Sub-county')['AI Priority'].apply(
        lambda x: (x == 'Critical').sum() * 3 + (x == 'High').sum() * 2
    ).to_dict()
    
    return {
        "summary": {
            "total_reports": len(df),
            "resolution_rate": f"{(len(df[df['Status'] == 'Resolved']) / len(df)) * 100:.1f}%"
        },
        "regional_risk_index": risk_scores
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)