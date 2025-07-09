import streamlit as st
import json
from recommendation_engine import get_recommendations
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Load recipes from the JSON file
with open('recipes.json', 'r') as f:
    recipes = json.load(f)

st.title("What to Eat?")

st.write("Don't know what to eat? Let me help you!")

# Get unique cuisines for the filter
cuisines = [""] + sorted(list(set(recipe["cuisine"] for recipe in recipes)))

# User inputs
meal_type = st.selectbox("Meal Type", ["breakfast", "lunch", "dinner", "snack"])
cuisine = st.selectbox("Cuisine (optional)", cuisines)
city = st.text_input("Enter your city for weather-based recommendations (optional)")

if 'recommendation' not in st.session_state:
    st.session_state.recommendation = None
if 'weather_info' not in st.session_state:
    st.session_state.weather_info = None
if 'liked_recipes' not in st.session_state:
    st.session_state.liked_recipes = []
if 'disliked_recipes' not in st.session_state:
    st.session_state.disliked_recipes = []
if 'preference_scores' not in st.session_state:
    st.session_state.preference_scores = {"cuisine": {}, "tags": {}}
if 'seen_recipes' not in st.session_state:
    st.session_state.seen_recipes = []

def fetch_and_set_recommendation():
    """Fetches a new recommendation and updates the session state."""
    # Combine disliked and already seen recipes to exclude them all
    exclude_ids = st.session_state.disliked_recipes + st.session_state.seen_recipes
    logger.info(f"Fetching new recommendation. Excluding IDs: {exclude_ids}")
    
    result = get_recommendations(
        recipes,
        city=city if city else None,
        meal_type=meal_type,
        cuisine=cuisine if cuisine else None,
        disliked_recipes=st.session_state.disliked_recipes,
        preference_scores=st.session_state.preference_scores,
        exclude_ids=exclude_ids
    )
    recommendations = result["recommendations"]
    st.session_state.weather_info = result["weather_info"]

    if recommendations:
        new_rec = recommendations[0]["recipe"]
        st.session_state.recommendation = new_rec
        st.session_state.seen_recipes.append(new_rec['id'])
    else:
        st.session_state.recommendation = None
        st.write("No more recommendations found for your criteria! Try changing your filters.")
        st.session_state.seen_recipes = [] # Reset seen list

if st.button("Suggest a meal"):
    fetch_and_set_recommendation()

# Reset seen recipes if filters change
filter_key = f"{meal_type}-{cuisine}"
if 'last_filter_key' not in st.session_state or st.session_state.last_filter_key != filter_key:
    st.session_state.seen_recipes = []
    st.session_state.last_filter_key = filter_key

if st.session_state.weather_info:
    weather = st.session_state.weather_info
    st.sidebar.subheader(f"Weather in {weather['name']}")
    st.sidebar.write(f"**Condition:** {weather['weather'][0]['main']}")
    st.sidebar.write(f"**Temperature:** {weather['main']['temp']}°C")

# Display Liked Dishes in the sidebar
if st.session_state.liked_recipes:
    st.sidebar.header("Your Liked Dishes")
    liked_recipe_names = [rec["name"] for rec in recipes if rec["id"] in st.session_state.liked_recipes]
    for name in liked_recipe_names:
        st.sidebar.write(f"- {name}")

if st.session_state.recommendation:
    rec = st.session_state.recommendation
    st.subheader(rec['name'])
    st.write(f"Cuisine: {rec['cuisine']}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Like"):
            # Add to liked list for display
            if rec['id'] not in st.session_state.liked_recipes:
                st.session_state.liked_recipes.append(rec['id'])
            
            # Update preference scores
            st.session_state.preference_scores["cuisine"][rec["cuisine"]] = st.session_state.preference_scores["cuisine"].get(rec["cuisine"], 0) + 2
            for tag in rec["tags"]:
                st.session_state.preference_scores["tags"][tag] = st.session_state.preference_scores["tags"].get(tag, 0) + 1

            st.success(f"Great! We'll look for more dishes like {rec['name']}.")
    with col2:
        if st.button("Dislike"):
            # Add to disliked list
            if rec['id'] not in st.session_state.disliked_recipes:
                st.session_state.disliked_recipes.append(rec['id'])
            # Remove from liked list if it's there
            if rec['id'] in st.session_state.liked_recipes:
                st.session_state.liked_recipes.remove(rec['id'])
            
            # Fetch a new recommendation and force an immediate rerun
            fetch_and_set_recommendation()
            st.rerun()