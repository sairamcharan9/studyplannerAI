import json
import os
from datetime import datetime

class FacialAnalysisDataService:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.log_file = os.path.join(self.data_dir, "facial_expression_logs.jsonl")

    def save_expression_data(self, user_id: str, study_session_id: str, expression: str, confidence: float):
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            "user_id": user_id,
            "study_session_id": study_session_id,
            "timestamp": timestamp,
            "expression": expression,
            "confidence": confidence
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        return log_entry

# Example usage (for testing, not part of the service itself)
if __name__ == "__main__":
    service = FacialAnalysisDataService()
    service.save_expression_data("user123", "sessionABC", "Focused", 0.92)
    service.save_expression_data("user123", "sessionABC", "Neutral", 0.78)
    print(f"Data logged to {service.log_file}")
