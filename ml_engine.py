import json
import pandas as pd
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN

# 1. INITIALIZE THE MULTILINGUAL AI MODEL
# We use mDeBERTa because it natively understands Swahili, English, and mixed dialects.
print("Loading Multilingual AI Model... (This may take a minute)")
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")

def analyze_complaint(text):
    """
    Uses the Neural Network to determine the type of issue and its priority.
    """

    # THE ULTIMATE KENYAN ROADS CATEGORY LIST
    type_labels = [
        "potholes, ruined tarmac, or damaged road surface", 
        "stolen manhole covers, missing guardrails, or vandalized streetlights", 
        "dead traffic lights, missing road signs, or faded paint", 
        "blocked drainage or flooded roads", 
        "matatu overlapping, boda bodas on sidewalks, or reckless driving", 
        "stalled trucks, illegal parking, or road obstruction", 
        "vehicle collision or severe road accident", 
        "unmarked speed bumps or abandoned road construction",
        "heavy traffic jam and general congestion"
    ]
    
    # DESCRIPTIVE PRIORITY: Gives the AI context on what "Critical" actually means
    priority_labels = [
        "Critical (life threatening or total road blockage)", 
        "Medium (significant delay or hazard)", 
        "Low (minor inconvenience or routine issue)"
    ]
    
    # Run the model for Complaint Type
    type_result = classifier(text, type_labels)
    predicted_type = type_result['labels'][0]
    
    # Run the model for Priority
    priority_result = classifier(text, priority_labels)
    # Extract just the first word (Critical, Medium, or Low) so it fits your dashboard UI cleanly
    predicted_priority = priority_result['labels'][0].split(" ")[0] 
    
    return predicted_type, predicted_priority

def detect_clusters(tickets_list):
    """
    Unsupervised ML to detect patterns/hotspots across all active tickets.
    """
    if len(tickets_list) < 3:
        return tickets_list # Return the list as-is if we don't have enough data to cluster yet
        
    texts = [ticket["complaint_text"] for ticket in tickets_list]
    
    # Convert text into a mathematical matrix
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(texts)
    
    # Run DBSCAN clustering (groups similar complaints together)
    # eps is the distance threshold, min_samples is how many complaints make a "hotspot"
    clustering = DBSCAN(eps=0.5, min_samples=2).fit(X)
    
    # Append the cluster ID back to the tickets
    for i, ticket in enumerate(tickets_list):
        cluster_id = int(clustering.labels_[i])
        ticket["ml_cluster_id"] = cluster_id
        ticket["is_hotspot"] = cluster_id != -1 # -1 means it's an isolated issue
        
    return tickets_list

def process_and_package_ticket(raw_ticket_data, all_historical_tickets):
    """
    The main pipeline: Aggregates, runs ML, detects clusters, and outputs JSON.
    """
    text = raw_ticket_data["complaint_text"]
    
    # 1. Run Multilingual AI for Type and Priority
    complaint_type, priority = analyze_complaint(text)
    
    # 2. Enrich the current ticket
    raw_ticket_data["ml_analysis"] = {
        "detected_category": complaint_type,
        "priority": priority
    }
    raw_ticket_data["status"] = "Escalated 🔴" if priority == "Critical" else "Open"
    
    # 3. Add to our historical list and run Pattern Detection
    all_historical_tickets.append(raw_ticket_data)
    clustered_tickets = detect_clusters(all_historical_tickets)
    
    # 4. Grab the updated ticket with its cluster info
    final_ticket = clustered_tickets[-1]
    
    # 5. Output to strict JSON for the database
    return json.dumps(final_ticket, indent=2)

if __name__ == "__main__":
    # Simulated Database of existing tickets
    db_tickets = [
        {"ticket_id": "MOR-001", "complaint_text": "Kuna shimo kubwa sana hapa Westlands, magari yanaharibika."}, # Swahili
        {"ticket_id": "MOR-002", "complaint_text": "Massive pothole on Waiyaki way causing heavy traffic."} # English (Same issue as above)
    ]
    
    # The new incoming ticket
    new_ticket = {
        "ticket_id": "MOR-003",
        "timestamp": "2026-04-22 16:00",
        "reporter": {"name": "Jane Doe", "phone": "0700000000"},
        "location": {"county": "NAIROBI", "sub_county": "westlands", "ward": "karura"},
        "complaint_text": "Ubers keep parking along side the road only leaving one lane to traffic. They always do it and it causes so much traffic build up."
    }
    
    # Run the engine
    final_json = process_and_package_ticket(new_ticket, db_tickets)
    print(final_json)