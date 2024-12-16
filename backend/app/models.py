from pydantic import BaseModel
from typing import List, Dict, Optional

class Song(BaseModel):
    title: str
    artist: str
    interaction_count: Optional[int] = None

class Artist(BaseModel):
    name: str
    interaction_count: int

class UserStats(BaseModel):
    total_songs: int
    total_artists: int
    total_listens: int

class MoodDistribution(BaseModel):
    love: float = 22.0
    dramatic: float = 21.0
    sad: float = 21.0
    chill: float = 21.0
    upbeat: float = 12.0

class SimilarUser(BaseModel):
    user_id: int
    name: str
    similarity: float

class UserProfile(BaseModel):
    user_id: int
    name: str
    stats: UserStats
    top_songs: List[Song]
    top_artists: List[Artist]
    mood_distribution: MoodDistribution
    main_character_energy: str
    recommendations: List[Song]
    similar_users: List[SimilarUser]
    similarity_reason: str
