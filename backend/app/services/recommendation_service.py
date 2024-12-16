from http.client import HTTPException
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.functions import col, expr
from typing import Dict, List, Tuple
import numpy as np # type: ignore

class RecommendationService:
    def __init__(self, spark_service):
        self.spark_service = spark_service
        self.model = None
        self._train_model()
    
    def _train_model(self):
        # Prepare data for ALS using correct column names
        als_data = self.spark_service.get_dataframe().select(
        col("CustomerID"),
        col("TrackId").alias("item"),
        col("UserTrackInteractionCount").alias("rating")
        )
        
        # Split data into training and test sets
        (training, test) = als_data.randomSplit([0.8, 0.2])
        
        # Create ALS model with matching column names
        als = ALS(
            rank=10,
            maxIter=5,
            regParam=0.01,
            alpha = 0.1,
            userCol="CustomerID",
            itemCol="item",
            ratingCol="rating",
            coldStartStrategy="drop"
        )
        
        # Train the model
        self.model = als.fit(training)
        
        # except Exception as e:
        #     raise HTTPException(
        #         status_code=500,
        #         detail=f"Error training recommendation model: {str(e)}"
        #     )
        
    def get_similar_users(self, user_id: int, n=5) -> List[Dict]:
        """Get similar users based on user factors"""
        # Get user factors
        user_factors = self.model.userFactors
        
        # Get target user's features
        target_user_factor = user_factors.filter(
            col("id") == user_id
        ).select("features").first()[0]
        
        # Calculate similarity with other users
        def cosine_similarity(v1, v2):
            return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
        
        # Get similar users using cosine similarity
        similar_users = user_factors.filter(
            col("id") != user_id
        ).rdd.map(
            lambda row: (
                row.id, 
                cosine_similarity(target_user_factor, row.features)
            )
        ).toDF(["similar_user", "similarity"]) \
        .orderBy(col("similarity").desc()) \
        .limit(n)
        
        # Join with user information to get names
        similar_users_with_names = similar_users.join(
            self.spark_service.get_dataframe().select("CustomerID", "Name").distinct(),
            similar_users.similar_user == col("CustomerID")
        ).select(
            col("similar_user").alias("user_id"),
            "Name",
            "similarity"
        )
        
        return similar_users_with_names.collect()
    
    def get_recommendations(self, user_id: int, n=10):
        """Get track recommendations for a user that are different from top songs"""
        # Get user's top songs first
        top_songs, _ = self.spark_service.get_top_songs_and_artists(user_id)
        top_song_ids = [song["TrackId"] for song in top_songs]
        
        # Generate recommendations
        user_recs = self.model.recommendForUserSubset(
            self.spark_service.get_dataframe().select("CustomerID").distinct().filter(
                col("CustomerID") == user_id
            ),
            n * 2  # Get more recommendations to account for filtering
        )
        
        # Extract recommended track IDs and scores
        if not user_recs.isEmpty():
            recommendations = user_recs.select(
                expr("explode(recommendations)")
            ).select(
                col("col.item").alias("TrackId"),
                col("col.rating").alias("score")
            )
            
            # Filter out songs that are in user's top songs
            filtered_recommendations = recommendations.filter(
                ~col("TrackId").isin(top_song_ids)
            )
            
            # Join with track information
            track_info = self.spark_service.get_dataframe().select(
                "TrackId", "Title", "Artist"
            ).distinct()
            
            final_recommendations = filtered_recommendations.join(
                track_info,
                "TrackId"
            ).orderBy(col("score").desc()).limit(n)
            
            return final_recommendations.collect()
        
        return []
    
    def get_user_preferences(self, user_id: int):
        """Get user's listening preferences"""
        user_data = self.spark_service.get_dataframe().filter(
            col("CustomerID") == user_id
        )
        
        # Get favorite genres (using artists as proxy)
        favorite_artists = user_data.groupBy("Artist") \
            .agg({"rating": "sum"}) \
            .orderBy(col("sum(rating)").desc()) \
            .limit(5)
        
        # Get listening patterns
        listening_patterns = user_data.select(
            "DayOfWeek",
            "HourOfDay",
            "IsWeekend",
            "MobileUsageRatio",
            "UserTrackDiversity"
        ).distinct().first()
        
        return {
            "favorite_artists": favorite_artists.collect(),
            "listening_patterns": listening_patterns
        }
