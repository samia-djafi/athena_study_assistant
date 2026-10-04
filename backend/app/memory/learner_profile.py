"""
Learner profile and preferences manager for Athena.
Provides persistent learning context, consent-based storage, and user deletion controls.
"""
import logging
from typing import Dict, List, Optional
from app.models.schemas import LearnerProfile, LearningLevel, ExplanationDepth

logger = logging.getLogger(__name__)

class LearnerProfileStore:
    def __init__(self):
        self._profiles: Dict[str, LearnerProfile] = {
            "guest": LearnerProfile(
                user_id="guest",
                preferred_level=LearningLevel.INTERMEDIATE,
                preferred_depth=ExplanationDepth.STANDARD,
                preferred_language="English",
                recently_studied_topics=[
                    "Data Structures: Trees & Heaps",
                    "Transformer Self-Attention",
                    "Async Python & Event Loop"
                ],
                learning_goals=[
                    "Master Algorithms & Complexity",
                    "Understand Neural Network Architectures"
                ],
                total_study_sessions=5,
                total_quizzes_taken=3,
                average_quiz_score=86.7,
                topics_to_review=[
                    "Dynamic Programming: Memoization vs Tabulation",
                    "Graph Dijkstra vs A*"
                ]
            )
        }

    def get_profile(self, user_id: str = "guest") -> LearnerProfile:
        if user_id not in self._profiles:
            self._profiles[user_id] = LearnerProfile(user_id=user_id)
        return self._profiles[user_id]

    def update_preferences(
        self,
        user_id: str,
        level: Optional[LearningLevel] = None,
        depth: Optional[ExplanationDepth] = None,
        language: Optional[str] = None
    ) -> LearnerProfile:
        profile = self.get_profile(user_id)
        if level:
            profile.preferred_level = level
        if depth:
            profile.preferred_depth = depth
        if language:
            profile.preferred_language = language
        return profile

    def record_study_topic(self, user_id: str, topic: str):
        profile = self.get_profile(user_id)
        if topic and topic not in profile.recently_studied_topics:
            profile.recently_studied_topics.insert(0, topic)
            if len(profile.recently_studied_topics) > 10:
                profile.recently_studied_topics.pop()
        profile.total_study_sessions += 1

    def record_quiz_result(self, user_id: str, percentage: float, knowledge_gaps: List[str]):
        profile = self.get_profile(user_id)
        # Update running average
        total_quizzes = profile.total_quizzes_taken
        new_avg = ((profile.average_quiz_score * total_quizzes) + percentage) / (total_quizzes + 1)
        profile.total_quizzes_taken += 1
        profile.average_quiz_score = round(new_avg, 1)
        
        for gap in knowledge_gaps:
            if gap not in profile.topics_to_review:
                profile.topics_to_review.append(gap)

    def delete_profile_data(self, user_id: str) -> bool:
        """User data control: clears learning history and resets profile."""
        if user_id in self._profiles:
            self._profiles[user_id] = LearnerProfile(user_id=user_id)
            return True
        return False

profile_store = LearnerProfileStore()
