# WhatToWatch

A movie recommendation system built using Letterboxd user data. The system analyzes movie ratings from Letterboxd users and provides personalized movie recommendations based on similarity in rating patterns.

## Features

- Scrapes movie ratings from Letterboxd users
- Processes both popular and niche movies
- Converts Letterboxd's star ratings to numerical values
- Uses collaborative filtering with cosine similarity for recommendations
- Includes caching system for faster subsequent runs

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/WhatToWatch.git
cd WhatToWatch
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Data Collection

1. First, collect Letterboxd user data:
```bash
python member_scraper.py
```
This will create a `members_file.txt` containing Letterboxd usernames.

2. Then, collect movie ratings for these users:
```bash
python member_movie_scraper.py
```
This will create a `movies.csv` file containing user ratings.

### Getting Recommendations

```python
from recommend import MovieRecommender

# Initialize the recommender
recommender = MovieRecommender("movies.csv")

# Get recommendations for a movie
recommendations = recommender.recommend("godzilla-minus-one")
print(recommendations)

# Get recommendations including niche movies
recommendations = recommender.recommend("movie-id", include_niche=True)

# Get a specific number of recommendations
recommendations = recommender.recommend("movie-id", n_recommendations=5)
```

## Project Structure

```
WhatToWatch/
├── member_scraper.py         # Scrapes Letterboxd usernames
├── member_movie_scraper.py   # Scrapes movie ratings
├── recommend.py             # Main recommendation system
├── members_file.txt         # Generated list of users
├── movies.csv              # Generated movie ratings data
└── README.md
```

## Data Format

### movies.csv
Contains three columns:
- User: Letterboxd username
- Film ID: Unique identifier for the movie
- Rating: User's rating (½ to ★★★★★)

## Technical Details

- Movies rated by 20 or more users are considered "famous"
- Movies rated by 200 or fewer users are considered "niche"
- Star ratings are converted to a 1-10 scale
- Recommendations are generated using cosine similarity
- First run processes all data and creates a cache file
- Subsequent runs use cached data for faster performance

## Requirements

- Python 3.6+
- pandas
- numpy
- scikit-learn
- BeautifulSoup4
- requests

## Cache Management

The system automatically creates a cache file (`movies_cached.pkl`) after the first run. To force reprocessing of data:

```python
recommender = MovieRecommender("movies.csv", use_cache=False)
```
