from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, desc, countDistinct, sum, to_timestamp, 
    dayofweek, hour, when, count, datediff, 
    current_date, max, to_date
)
from pyspark.sql.window import Window
from app.config import settings
from typing import Tuple
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler

class SparkService:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName(settings.APP_NAME) \
            .master(settings.SPARK_MASTER) \
            .getOrCreate()
        
        # Load and clean the data
        self._load_and_clean_data()
        
    def _load_and_clean_data(self):
        # Load raw dataframes
        music_df = self.spark.read.csv("data/music.csv", header=True, inferSchema=True)
        tracks_df = self.spark.read.csv("data/tracks.csv", header=True, inferSchema=True)
        cust_df = self.spark.read.csv("data/cust.csv", header=True, inferSchema=True)
        
        #Making column names consistent
        tracks_df = tracks_df.withColumnRenamed("ZipCode", "ListeningZIP").withColumnRenamed("CustID", "CustomerID")
        cust_df = cust_df.withColumnRenamed("zip", "ZIP").withColumnRenamed("CustID", "CustomerID")

        #converting to date dtype
        cust_df = cust_df.withColumn("SignDate", to_date("SignDate", "MM/dd/yyyy"))

        tracks_df = tracks_df.withColumn("DateTime", to_timestamp("DateTime", "M/d/yy H:mm"))

        #Dropping the na values since they are less than 5% of the total
        music_df = music_df.na.drop(subset=["Length"])

        songs = tracks_df.join(music_df, on="TrackId", how="inner")

        #Combined all three datasets
        self.joined_df = songs.join(cust_df, on="CustomerID", how="inner")

        # # Time-based features
        # joined_df = joined_df.withColumn("DateTime", to_timestamp("DateTime"))
        # joined_df = joined_df.withColumn("DayOfWeek", dayofweek("DateTime"))
        # joined_df = joined_df.withColumn("HourOfDay", hour("DateTime"))
        # joined_df = joined_df.withColumn("IsWeekend", when((col("DayOfWeek") == 1) | (col("DayOfWeek") == 7), 1).otherwise(0))

        # # User listening frequency
        # window_spec = Window.partitionBy("CustomerID")
        # joined_df = joined_df.withColumn("UserListeningCount", count("EventID").over(window_spec))

        # # Track popularity
        # track_window = Window.partitionBy("TrackId")
        # joined_df = joined_df.withColumn("TrackPopularity", count("EventID").over(track_window))

        # # User-Track interaction features
        # user_track_window = Window.partitionBy("CustomerID", "TrackId")
        # joined_df = joined_df.withColumn("UserTrackInteractionCount", count("EventID").over(user_track_window))

        # # Mobile usage ratio
        # joined_df = joined_df.withColumn("MobileUsageRatio", 
        #                          sum("Mobile").over(window_spec) / count("EventID").over(window_spec))
        
        # # User tenure
        # joined_df = joined_df.withColumn("SignDate", to_date("SignDate"))
        # joined_df = joined_df.withColumn("UserTenure", datediff(current_date(), "SignDate"))

        # # Genre features
        # artist_indexer = StringIndexer(inputCol="Artist", outputCol="ArtistIndex")
        # artist_encoder = OneHotEncoder(inputCol="ArtistIndex", outputCol="ArtistVector")

        # # Normalize continuous features
        # joined_df = joined_df.withColumn("NormalizedLength", col("Length") / 1000)

        # # Recency feature
        # joined_df = joined_df.withColumn("LastListenDate", max("DateTime").over(window_spec))
        # joined_df = joined_df.withColumn("DaysSinceLastListen", datediff(current_date(), "LastListenDate"))

        # # Select relevant columns for the final feature set
        # feature_cols = ["CustomerID", "TrackId", "DayOfWeek", "HourOfDay", "IsWeekend", "UserListeningCount", 
        #                 "TrackPopularity", "UserTrackInteractionCount", "MobileUsageRatio", "UserTenure", 
        #                 "NormalizedLength", "UserTrackDiversity", "DaysSinceLastListen", "ArtistVector"]
        
        
        
        
        # # 3. Join the dataframes
        # self.joined_df = music_df.join(
        #     tracks_df, "TrackId"
        # ).join(
        #     cust_df, 
        #     music_df.CustomerID == cust_df.CustID
        # )
        
        # 4. Apply feature engineering
        self._apply_feature_engineering()
    
    def _apply_feature_engineering(self):
        # 1. Time-based features
        self.joined_df = self.joined_df.withColumn("DayOfWeek", dayofweek("DateTime"))
        self.joined_df = self.joined_df.withColumn("HourOfDay", hour("DateTime"))
        self.joined_df = self.joined_df.withColumn(
            "IsWeekend", 
            when((col("DayOfWeek").isin(1, 7)), 1).otherwise(0)
        )
        
        # 2. User listening frequency
        window_spec = Window.partitionBy("CustomerID")
        self.joined_df = self.joined_df.withColumn(
            "UserListeningCount", 
            count("EventID").over(window_spec)
        )
        
        # 3. Track popularity
        track_window = Window.partitionBy("TrackId")
        self.joined_df = self.joined_df.withColumn(
            "TrackPopularity", 
            count("EventID").over(track_window)
        )
        
        # 4. User-Track interaction features
        user_track_window = Window.partitionBy("CustomerID", "TrackId")
        self.joined_df = self.joined_df.withColumn(
            "UserTrackInteractionCount", 
            count("EventID").over(user_track_window)
        )
        
        # 5. Mobile usage ratio
        self.joined_df = self.joined_df.withColumn(
            "MobileUsageRatio",
            sum("Mobile").over(window_spec) / count("EventID").over(window_spec)
        )
        
        # 6. User tenure
        self.joined_df = self.joined_df.withColumn(
            "UserTenure",
            datediff(current_date(), "SignDate")
        )
        
        # 7. Normalize track length
        self.joined_df = self.joined_df.withColumn(
            "NormalizedLength",
            col("Length") / 1000
        )
        
        # 8. User track diversity
        self.joined_df = self.joined_df.withColumn(
            "UserTrackDiversity",
            count("TrackId").over(window_spec) / sum("UserTrackInteractionCount").over(window_spec)
        )
        
        # 9. Recency feature
        self.joined_df = self.joined_df.withColumn(
            "LastListenDate",
            max("DateTime").over(window_spec)
        )
        self.joined_df = self.joined_df.withColumn(
            "DaysSinceLastListen",
            datediff(current_date(), "LastListenDate")
        )

    def get_user_name(self, user_id: int) -> str:
        return self.joined_df.filter(
            col("CustomerID") == user_id
        ).select("Name").first()[0]

    def get_user_stats(self, user_id: int):
        return self.joined_df.filter(col("CustomerID") == user_id).agg(
            countDistinct("TrackId").alias("total_songs"),
            countDistinct("Artist").alias("total_artists"),
            sum("UserTrackInteractionCount").alias("total_listens")
        ).first()

    def get_top_songs_and_artists(self, user_id: int, n=5) -> Tuple:
        # Get top songs
        top_songs = self.joined_df.filter(col("CustomerID") == user_id) \
            .groupBy("TrackId", "Title", "Artist") \
            .agg({"UserTrackInteractionCount": "sum"}) \
            .orderBy(desc("sum(UserTrackInteractionCount)")) \
            .limit(n)
        
        # Get top artists
        top_artists = self.joined_df.filter(col("CustomerID") == user_id) \
            .groupBy("Artist") \
            .agg({"UserTrackInteractionCount": "sum"}) \
            .orderBy(desc("sum(UserTrackInteractionCount)")) \
            .limit(n)
        
        return top_songs.collect(), top_artists.collect()

    def get_dataframe(self):
        return self.joined_df
