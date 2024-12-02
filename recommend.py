import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Optional, Dict, Tuple
import time
import pickle
import os

class MovieRecommender:
    def __init__(self, csv_path: str, use_cache: bool = True):
        """Initialize the recommender system with movie ratings data."""
        self.csv_path = csv_path
        self.cache_path = csv_path.replace('.csv', '_cached.pkl')
        
        # Thresholds for movie categorization
        self.MIN_RATINGS = 20
        self.MAX_RATINGS = 200
        
        if use_cache and os.path.exists(self.cache_path):
            print("Loading from cache...")
            start = time.time()
            self._load_from_cache()
            print(f"Loaded from cache in {time.time() - start:.2f} seconds")
        else:
            print("Processing data from CSV...")
            start_total = time.time()
            
            print("Loading CSV...")
            start = time.time()
            self.movies = pd.read_csv(csv_path)
            print(f"CSV loaded in {time.time() - start:.2f} seconds")
            
            self._prepare_data()
            print(f"Total processing time: {time.time() - start_total:.2f} seconds")
            
            if use_cache:
                print("Saving to cache...")
                start = time.time()
                self._save_to_cache()
                print(f"Saved to cache in {time.time() - start:.2f} seconds")

    def _prepare_data(self) -> None:
        """Prepare the data by filtering movies and creating pivot tables."""
        print("Filtering movies...")
        start = time.time()
        movie_counts = self.movies.groupby("Film ID").count()['Rating']
        
        # Clear separation between famous and niche movies
        self.famous_movies = movie_counts[movie_counts >= self.MIN_RATINGS].index
        self.niche_movies = movie_counts[
            (movie_counts < self.MIN_RATINGS) & 
            (movie_counts <= self.MAX_RATINGS)
        ].index
        print(f"Found {len(self.famous_movies)} famous movies and {len(self.niche_movies)} niche movies")
        print(f"Filtering completed in {time.time() - start:.2f} seconds")
        
        print("Creating rating dataframes...")
        start = time.time()
        self.ratings_famous = self.movies[self.movies["Film ID"].isin(self.famous_movies)].copy()
        self.ratings_niche = self.movies[self.movies["Film ID"].isin(self.niche_movies)].copy()
        print(f"Rating dataframes created in {time.time() - start:.2f} seconds")
        
        print("Converting ratings...")
        start = time.time()
        self.ratings_famous['Rating'] = self.ratings_famous['Rating'].apply(self._star_to_numeric)
        self.ratings_niche['Rating'] = self.ratings_niche['Rating'].apply(self._star_to_numeric)
        print(f"Ratings converted in {time.time() - start:.2f} seconds")
        
        print("Creating pivot tables...")
        start = time.time()
        self.pt_famous = self.ratings_famous.pivot_table(
            index="Film ID", columns="User", values="Rating"
        ).fillna(0)
        self.pt_niche = self.ratings_niche.pivot_table(
            index="Film ID", columns="User", values="Rating"
        ).fillna(0)
        print(f"Pivot tables created in {time.time() - start:.2f} seconds")
        
        print("Calculating similarity matrices...")
        start = time.time()
        self.similarity_famous = cosine_similarity(self.pt_famous)
        self.similarity_niche = cosine_similarity(self.pt_niche)
        print(f"Similarity matrices calculated in {time.time() - start:.2f} seconds")
    
    def _save_to_cache(self):
        """Save processed data to cache file."""
        cache_data = {
            'pt_famous': self.pt_famous,
            'pt_niche': self.pt_niche,
            'similarity_famous': self.similarity_famous,
            'similarity_niche': self.similarity_niche,
            'famous_movies': self.famous_movies,
            'niche_movies': self.niche_movies
        }
        with open(self.cache_path, 'wb') as f:
            pickle.dump(cache_data, f)
    
    def _load_from_cache(self):
        """Load processed data from cache file."""
        with open(self.cache_path, 'rb') as f:
            cache_data = pickle.load(f)
        self.pt_famous = cache_data['pt_famous']
        self.pt_niche = cache_data['pt_niche']
        self.similarity_famous = cache_data['similarity_famous']
        self.similarity_niche = cache_data['similarity_niche']
        self.famous_movies = cache_data['famous_movies']
        self.niche_movies = cache_data['niche_movies']
    
    @staticmethod
    def _star_to_numeric(star_rating: str) -> Optional[int]:
        """Convert Letterboxd star ratings to numeric values."""
        rating_map = {
            '½': 1, '★': 2, '★½': 3, '★★': 4, '★★½': 5,
            '★★★': 6, '★★★½': 7, '★★★★': 8, '★★★★½': 9, '★★★★★': 10
        }
        return rating_map.get(star_rating)
    
    def get_movie_category(self, movie_id: str) -> str:
        """Determine if a movie is famous, niche, or unknown."""
        if movie_id in self.famous_movies:
            return "famous"
        elif movie_id in self.niche_movies:
            return "niche"
        else:
            return "unknown"
    
    def recommend(self, movie_id: str, n_recommendations: int = 8, include_niche: bool = False) -> Dict[str, List[Tuple[str, float]]]:
        """
        Get movie recommendations based on similarity.
        Returns both famous and niche recommendations if requested.
        """
        start = time.time()
        results = {"famous": [], "niche": []}
        movie_category = self.get_movie_category(movie_id)
        
        try:
            # Get famous movie recommendations
            if movie_id in self.pt_famous.index:
                index = np.where(self.pt_famous.index == movie_id)[0][0]
                similar_items = sorted(
                    list(enumerate(self.similarity_famous[index])),
                    key=lambda x: x[1],
                    reverse=True
                )[1:n_recommendations + 1]
                results["famous"] = [(self.pt_famous.index[i[0]], float(i[1])) for i in similar_items]
            
            # Get niche movie recommendations if requested
            if include_niche and movie_id in self.pt_niche.index:
                index = np.where(self.pt_niche.index == movie_id)[0][0]
                similar_items = sorted(
                    list(enumerate(self.similarity_niche[index])),
                    key=lambda x: x[1],
                    reverse=True
                )[1:n_recommendations + 1]
                results["niche"] = [(self.pt_niche.index[i[0]], float(i[1])) for i in similar_items]
            
            if not any(results.values()):
                raise ValueError(f"Movie ID '{movie_id}' not found in dataset")
            
            print(f"Recommendations generated in {time.time() - start:.2f} seconds")
            print(f"Movie '{movie_id}' category: {movie_category}")
            return results
                
        except Exception as e:
            raise ValueError(f"Error generating recommendations: {str(e)}")

if __name__ == "__main__":
    # Example usage
    recommender = MovieRecommender("movies.csv")
    try:
        # Get recommendations for a famous movie
        famous_movie = "inception"
        print(f"\nGetting recommendations for {famous_movie}:")
        recs = recommender.recommend(famous_movie)
        print("\nFamous movie recommendations:")
        for movie, score in recs["famous"]:
            print(f"{movie}: {score:.3f}")
            
        # Get both famous and niche recommendations
        print(f"\nGetting recommendations for {famous_movie} including niche movies:")
        recs = recommender.recommend(famous_movie, include_niche=True)
        print("\nFamous movie recommendations:")
        for movie, score in recs["famous"]:
            print(f"{movie}: {score:.3f}")
        print("\nNiche movie recommendations:")
        for movie, score in recs["niche"]:
            print(f"{movie}: {score:.3f}")
            
    except ValueError as e:
        print(f"Error: {e}")