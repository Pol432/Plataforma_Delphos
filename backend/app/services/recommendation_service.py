"""
Recommendation Service
ML-powered matching algorithm for user-simulation engagement prediction.
"""
from typing import Dict, List, Set
from app.schemas.ml import MatchingInput, MatchingOutput, UserFeaturesInput, SimulationFeaturesInput

class RecommendationService:
    """
    Recommendation engine for matching users to simulations.
    Algorithm:
    1. Skill overlap (Jaccard similarity)
    2. Psychometric profile matching
    3. Difficulty alignment
    4. Duration preference
    """
    
    # Weights for scoring components
    SKILL_OVERLAP_WEIGHT = 0.4
    PSYCHOMETRIC_WEIGHT = 0.3
    DIFFICULTY_WEIGHT = 0.2
    DURATION_WEIGHT = 0.1
    
    # Difficulty-to-score mapping
    DIFFICULTY_THRESHOLDS = {
        "Beginner": (0, 40),
        "Intermediate": (30, 70),
        "Advanced": (60, 90),
        "Expert": (80, 100)
    }
    
    def calculate_skill_overlap(self, user_skills: List[int], sim_skills: List[int]) -> float:
        """Calculate Jaccard similarity between skill sets"""
        if not user_skills and not sim_skills:
            raise ValueError("Both skill lists are empty")
        
        if not sim_skills or not user_skills:
            return 0.0
        
        user_set = set(user_skills)
        sim_set = set(sim_skills)
        
        intersection = len(user_set & sim_set)
        union = len(user_set | sim_set)
        
        return intersection / union if union > 0 else 0.0

    def calculate_psychometric_match(self, user_features: UserFeaturesInput, sim_features: SimulationFeaturesInput) -> float:
        """Calculate psychometric profile alignment based on category weights"""
        category = sim_features.simulation_categoria.value
        
        # Matrix of weights per category
        weights = {
            "STEM": {"analytical": 0.4, "hands_on": 0.3, "creative": 0.1, "social": 0.1, "linguistic": 0.1},
            "Business": {"social": 0.3, "linguistic": 0.3, "analytical": 0.2, "creative": 0.1, "hands_on": 0.1},
            "Arts": {"creative": 0.4, "linguistic": 0.2, "analytical": 0.1, "social": 0.2, "hands_on": 0.1},
            "Health": {"analytical": 0.3, "social": 0.3, "hands_on": 0.2, "linguistic": 0.1, "creative": 0.1},
            "Law": {"linguistic": 0.4, "analytical": 0.3, "social": 0.2, "creative": 0.05, "hands_on": 0.05}
        }
        
        cat_weights = weights.get(category, weights["STEM"])
        
        # Weighted score (normalized 0-1)
        score = (
            user_features.analytical_score * cat_weights["analytical"] +
            user_features.creative_score * cat_weights["creative"] +
            user_features.social_score * cat_weights["social"] +
            user_features.linguistic_score * cat_weights["linguistic"] +
            user_features.hands_on_score * cat_weights["hands_on"]
        ) / 100.0
        return score

    def calculate_difficulty_match(self, user_features: UserFeaturesInput, sim_features: SimulationFeaturesInput) -> float:
        """Check if user skill level aligns with simulation difficulty"""
        difficulty = sim_features.simulation_nivel_dificultad.value
        thresholds = self.DIFFICULTY_THRESHOLDS.get(difficulty, (0, 100))
        
        user_level = user_features.analytical_score # Proxy for competence
        min_t, max_t = thresholds
        
        if min_t <= user_level <= max_t:
            return 1.0
        elif user_level < min_t:
            gap = min_t - user_level
            return max(0.0, 1.0 - (gap / 100.0))
        else:
            gap = user_level - max_t
            return max(0.0, 1.0 - (gap / 100.0))

    def calculate_duration_match(self, user_features: UserFeaturesInput, sim_features: SimulationFeaturesInput) -> float:
        """Heuristic: High hands_on score -> prefers longer simulations"""
        duration = sim_features.simulation_duracion_horas
        hands_on = user_features.hands_on_score
        
        if hands_on >= 70:
            p_min, p_max = 6.0, 20.0
        elif hands_on >= 40:
            p_min, p_max = 3.0, 10.0
        else:
            p_min, p_max = 1.0, 5.0
            
        if p_min <= duration <= p_max:
            return 1.0
        elif duration < p_min:
            gap = p_min - duration
            return max(0.0, 1.0 - (gap / p_max))
        else:
            gap = duration - p_max
            return max(0.0, 1.0 - (gap / 20.0))

    def predict(self, matching_input: MatchingInput) -> MatchingOutput:
        """Main prediction pipeline"""
        user = matching_input.user_features
        sim = matching_input.simulation_features
        
        skill_score = self.calculate_skill_overlap(user.user_skill_ids, sim.simulation_skill_ids)
        psycho_score = self.calculate_psychometric_match(user, sim)
        diff_score = self.calculate_difficulty_match(user, sim)
        dur_score = self.calculate_duration_match(user, sim)
        
        # Weighted Ensemble
        prob = (
            skill_score * self.SKILL_OVERLAP_WEIGHT +
            psycho_score * self.PSYCHOMETRIC_WEIGHT +
            diff_score * self.DIFFICULTY_WEIGHT +
            dur_score * self.DURATION_WEIGHT
        )
        
        prob = max(0.0, min(1.0, prob))
        label = 1 if prob >= 0.6 else 0
        
        return MatchingOutput(
            label=label,
            engagement_probability=round(prob, 4),
            skill_overlap_score=round(skill_score, 4),
            difficulty_match_score=round(diff_score, 4),
            confidence_interval=(max(0.0, prob - 0.1), min(1.0, prob + 0.1))
        )
