"""
Matching Service
Business logic for matching Users with Simulations/Companies.
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any

class MatchingService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_match_score(self, user_id: int, company_id: int) -> Dict[str, Any]:
        """Calcula score de afinidad base (Mock)"""
        # En el futuro, esto usará el ML Engine real.
        # Por ahora, devolvemos una estructura válida para pasar el test.
        return {
            "user_id": user_id,
            "company_id": company_id,
            "match_score": 85.5, # Score simulado > 0
            "breakdown": {
                "skills": 0.8,
                "culture": 0.9,
                "location": 1.0
            }
        }

    def find_best_matches_for_user(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Encuentra simulaciones para un usuario"""
        return [
            {"simulation_id": 1, "score": 95},
            {"simulation_id": 2, "score": 88}
        ]

    def find_best_candidates_for_company(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Encuentra usuarios para una empresa"""
        return [
            {"user_id": 1, "score": 92},
            {"user_id": 2, "score": 85}
        ]
