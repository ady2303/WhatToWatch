import streamlit as st
import pandas as pd
from recommend import MovieRecommender
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="WhatToWatch - Movie Recommendations",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .recommendation-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_recommender():
    """Load the movie recommender system."""
    return MovieRecommender("movies.csv")

def main():
    # Header
    st.title("🎬 WhatToWatch")
    st.subheader("Get personalized movie recommendations")
    
    # Initialize recommender
    try:
        recommender = load_recommender()
    except Exception as e:
        st.error(f"Error loading recommender system: {str(e)}")
        return

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        n_recommendations = st.slider(
            "Number of recommendations",
            min_value=1,
            max_value=20,
            value=8
        )
        include_niche = st.checkbox("Include niche movies", value=False)
        
        st.markdown("---")
        st.markdown("""
        ### About
        WhatToWatch uses collaborative filtering to recommend movies based on Letterboxd user ratings.
        
        - **Famous movies**: Movies with 20+ ratings
        - **Niche movies**: Movies with fewer ratings
        """)

    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        movie_id = st.text_input(
            "Enter a movie ID from Letterboxd (e.g., 'inception', 'godzilla-minus-one')",
            key="movie_input"
        )

    if movie_id:
        try:
            # Get movie category
            movie_category = recommender.get_movie_category(movie_id)
            
            # Get recommendations
            recommendations = recommender.recommend(
                movie_id,
                n_recommendations=n_recommendations,
                include_niche=include_niche
            )
            
            # Display results
            st.markdown("---")
            st.subheader("Recommendations")
            
            # Movie info
            st.markdown(f"**Input movie**: {movie_id}")
            st.markdown(f"**Category**: {movie_category.title()}")
            
            # Create tabs for different recommendation types
            if include_niche:
                famous_tab, niche_tab = st.tabs(["Famous Movies", "Niche Movies"])
            else:
                famous_tab = st.tabs(["Famous Movies"])[0]
            
            # Famous movies recommendations
            with famous_tab:
                if recommendations["famous"]:
                    for movie, score in recommendations["famous"]:
                        with st.container():
                            st.markdown(f"""
                            <div class="recommendation-card">
                                <h4>{movie}</h4>
                                <p>Similarity Score: {score:.3f}</p>
                                <a href="https://letterboxd.com/film/{movie}" target="_blank">View on Letterboxd</a>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No famous movie recommendations found.")
            
            # Niche movies recommendations
            if include_niche:
                with niche_tab:
                    if recommendations["niche"]:
                        for movie, score in recommendations["niche"]:
                            with st.container():
                                st.markdown(f"""
                                <div class="recommendation-card">
                                    <h4>{movie}</h4>
                                    <p>Similarity Score: {score:.3f}</p>
                                    <a href="https://letterboxd.com/film/{movie}" target="_blank">View on Letterboxd</a>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("No niche movie recommendations found.")
            
            # Visualization
            if any(recommendations.values()):
                st.markdown("---")
                st.subheader("Similarity Scores Visualization")
                
                # Prepare data for visualization
                viz_data = []
                for movie, score in recommendations["famous"]:
                    viz_data.append({
                        "movie": movie,
                        "similarity": score,
                        "category": "Famous"
                    })
                if include_niche:
                    for movie, score in recommendations.get("niche", []):
                        viz_data.append({
                            "movie": movie,
                            "similarity": score,
                            "category": "Niche"
                        })
                
                # Create bar chart
                df = pd.DataFrame(viz_data)
                fig = px.bar(
                    df,
                    x="movie",
                    y="similarity",
                    color="category",
                    title=f"Similarity Scores for {movie_id}",
                    labels={"movie": "Movie", "similarity": "Similarity Score"},
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()