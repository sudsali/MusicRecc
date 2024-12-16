# app/services/analysis_service.py
from openai import OpenAI
from app.config import settings
from typing import Dict, List
import os

class AnalysisService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        pass
        
    def analyze_character_and_moods(self, top_songs: List, top_artists: List) -> Dict:
        songs_info = [f"{song.Title} by {song.Artist}" for song in top_songs]
        artists_info = [artist.Artist for artist in top_artists]
        
        prompt = f"""
            Based on these top songs:
            {', '.join(songs_info)}
            
            And top artists:
            {', '.join(artists_info)}
            
            Analyze the songs and artists above carefully.
            Please provide:
            1. Main Character Energy: Give a creative title and one-line description that captures the essence of this music taste.
            2. Music Taste: Give 1-2 words for the mood of music listened to. Keep the wording slightly different from Main Character Energy's title.

            Format your response exactly like this:
            Main Character Energy: [title] - [description]
            Music Taste: [taste]

            Examples:
            Main Character Energy: [Rocking Legends] - [Unapologetically classic rock vibes with a touch of nostalgia.]
            Music Taste: [energetic fury]

            Main Character Energy: [Retro Revivalists] - [Embracing the timeless sounds of classic rock with a modern twist.]
            Music Taste: [nostalgic]
            """
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a music analyst providing insights on listener preferences."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    
    def analyze_why_compatible(self, top_songs: List, top_artists: List, top_songs_partner: List, top_artists_partner: List) -> Dict:
        songs_info = [f"{song.Title} by {song.Artist}" for song in top_songs]
        artists_info = [artist.Artist for artist in top_artists]
        songs_info_partner = [f"{song.Title} by {song.Artist}" for song in top_songs_partner]
        artists_info_partner = [artist.Artist for artist in top_artists_partner]
        
        prompt = f"""
            Here are two user profiles:
            User 1
            top songs:
            {', '.join(songs_info)}
            
            And top artists:
            {', '.join(artists_info)}
            
            User 2
            top songs:
            {', '.join(songs_info_partner)}

            And top artists:
            {', '.join(artists_info_partner)}

            Analyze the songs and artists above carefully.
            Please provide:
            One to two short sentences. First sentence should start with "We think you'll make a good pair because" and continue with a plausible reason for why the two users will make a good pair based on their profiles.

            Examples:
            We think you'll make a good pair because you share interest in rock music and the song Take on me is the top song for both of you.

            We think you'll make a good pair because Kendrick Lamar is their favorite artist just like you.

            We think you'll make a good pair because both of you like chill music with a lofi vibe. You can talk about how you like more nostalgic songs vs them liking more futuristic beats.
            """
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a music analyst providing insights on listener preferences."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    
    def generate_report(self, target_user_id: int, target_user_name: str, 
                   similar_users: List, similar_user_names: List, 
                   recommended_tracks: List, top_songs: List, 
                   top_artists: List, spark_service) -> str:
    
        # Get user stats directly from spark_service instead of calculating
        stats = spark_service.get_user_stats(target_user_id)
        
        # Get character analysis and moods
        character_and_moods = self.analyze_character_and_moods(top_songs, top_artists)
        
        # Prepare the input for the final report
        similar_users_info = [f"{id}: {name}" for id, name in zip(similar_users, similar_user_names)]
        tracks_info = [f"{track.Title} by {track.Artist}" for track in recommended_tracks]
        top_songs_info = [f"{song.Title} by {song.Artist}" for song in top_songs]
        top_artists_info = [artist.Artist for artist in top_artists]
        
        prompt = f"""
        Generate a creative report for a music recommendation system with the following information:
        
        Target User: {target_user_name} (ID: {target_user_id})
        
        Listening Stats:
        Total Songs: {stats["total_songs"]}
        Total Artists: {stats["total_artists"]}
        Total Listens: {stats["total_listens"]}
        
        {character_and_moods}
        
        Top 5 Songs:
        {', '.join(top_songs_info)}
        
        Top 5 Artists:
        {', '.join(top_artists_info)}
        
        Top Similar Users:
        {', '.join(similar_users_info)}
        
        Recommended Tracks:
        {', '.join(tracks_info)}
        
        Please provide a creative and engaging summary that includes:
        1. A list of top 5 songs, 5 artists, 5 similar users and 5 recommended tracks as well as main character energy and moods
        2. Overview of the user's listening habits and stats
        3. Analysis of their music taste based on top songs and artists
        4. Description of their musical personality and mood preferences
        5. List the name of the top match (Your top match is name_of_the_user!)
        6. Explanation of why they match with their top similar user
        7. Personalized recommendations explanation
        """

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a music analyst providing insights on listener preferences."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content