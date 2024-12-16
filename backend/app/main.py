# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.spark_service import SparkService
from app.services.recommendation_service import RecommendationService
from app.services.analysis_service import AnalysisService
from app.models import SimilarUser, UserProfile, UserStats, Song, Artist, MoodDistribution
from typing import List

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
spark_service = SparkService()
recommendation_service = RecommendationService(spark_service)
analysis_service = AnalysisService()

@app.get("/api/user/{user_id}")
async def get_user_profile(user_id: int) -> UserProfile:
    try:
        # Get user stats
        stats_row = spark_service.get_user_stats(user_id)
        stats = UserStats(
            total_songs=stats_row["total_songs"],
            total_artists=stats_row["total_artists"],
            total_listens=stats_row["total_listens"]
        )

        # Get top songs and artists
        top_songs_rows, top_artists_rows = spark_service.get_top_songs_and_artists(user_id)
        
        # Convert song rows to Song models
        top_songs = [
            Song(
                title=row["Title"],
                artist=row["Artist"],
                interaction_count=row["sum(UserTrackInteractionCount)"]
            ) for row in top_songs_rows
        ]

        # Convert artist rows to Artist models
        top_artists = [
            Artist(
                name=row["Artist"],
                interaction_count=row["sum(UserTrackInteractionCount)"]
            ) for row in top_artists_rows
        ]

        # Get character analysis
        character_analysis = analysis_service.analyze_character_and_moods(top_songs_rows, top_artists_rows)
        # character_analysis = "None"
        

        recommended_tracks = recommendation_service.get_recommendations(user_id, n=5)  # Get top 5
        
        # Convert recommendations to Song models
        recommendations = [
            Song(
                title=track["Title"],
                artist=track["Artist"],
                interaction_count=0  # New recommendations don't have interaction counts
            ) for track in recommended_tracks
        ]

        similar_users_rows = recommendation_service.get_similar_users(user_id)
        similar_users = [
            SimilarUser(
                user_id=row["user_id"],
                name=row["Name"],
                similarity=row["similarity"]
            ) for row in similar_users_rows
        ]

        similar_users_rows.sort(key= lambda x: x["similarity"], reverse=True)
        partner_user_id = similar_users_rows[0]["user_id"]
        top_songs_rows_partner, top_artists_rows_partner = spark_service.get_top_songs_and_artists(partner_user_id)
        similarity_reason = analysis_service.analyze_why_compatible(top_songs_rows, top_artists_rows, top_songs_rows_partner, top_artists_rows_partner)

        # Create UserProfile object
        user_profile = UserProfile(
            user_id=user_id,
            name=spark_service.get_user_name(user_id),
            stats=stats,
            top_songs=top_songs,
            top_artists=top_artists,
            mood_distribution=MoodDistribution(),
            main_character_energy=character_analysis,
            recommendations=recommendations,
            similar_users=similar_users,  # Add similar users
            similarity_reason=similarity_reason
        )

        return user_profile
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/report/{user_id}")
async def get_user_report(user_id: int):
    try:
        # Get all necessary data
        stats = spark_service.get_user_stats(user_id)
        top_songs, top_artists = spark_service.get_top_songs_and_artists(user_id)
        similar_users = recommendation_service.get_similar_users(user_id)
        recommendations = recommendation_service.get_recommendations(user_id)
        
        # Get names
        target_user_name = spark_service.get_user_name(user_id)
        # Fix: Access the correct column name from similar_users Row objects
        similar_user_ids = [user["user_id"] for user in similar_users]  # Changed from similar_user to user_id
        similar_user_names = [spark_service.get_user_name(uid) for uid in similar_user_ids]
        
        # Generate report
        report = analysis_service.generate_report(
            user_id,
            target_user_name,
            similar_user_ids,
            similar_user_names,
            recommendations,
            top_songs,
            top_artists,
            spark_service
        )
        
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))