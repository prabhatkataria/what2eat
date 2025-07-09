from weather_service import get_weather

def map_weather_to_suitability(weather_data):
    """Maps weather data to our defined suitability tags."""
    if not weather_data:
        return "any"

    main_weather = weather_data.get("weather", [{}])[0].get("main")
    temp = weather_data.get("main", {}).get("temp")

    if main_weather in ["Rain", "Drizzle", "Thunderstorm"]:
        return "rainy"
    if temp is not None:
        if temp < 15:
            return "cold"
        if temp > 25:
            return "hot"
    return "any"

def get_recommendations(recipes, city=None, meal_type=None, cuisine=None, disliked_recipes=None, preference_scores=None, exclude_ids=None):
    """
    Recommends recipes based on weather, filters, and learned preference scores.
    Returns a dictionary with recommendations and weather info.
    """
    weather_data = get_weather(city) if city else None
    weather_suitability = map_weather_to_suitability(weather_data)
    
    disliked_recipes = disliked_recipes or []
    preference_scores = preference_scores or {"cuisine": {}, "tags": {}}
    exclude_ids = set(exclude_ids or [])

    scored_recipes = []
    for recipe in recipes:
        # Skip disliked or already viewed recipes
        if recipe["id"] in disliked_recipes or recipe["id"] in exclude_ids:
            continue

        score = 0
        
        # --- Preference Score from learned affinities ---
        # Boost score based on liked cuisines
        cuisine_score = preference_scores["cuisine"].get(recipe["cuisine"], 0)
        score += cuisine_score
        
        # Boost score based on liked tags
        tag_score = 0
        for tag in recipe["tags"]:
            tag_score += preference_scores["tags"].get(tag, 0)
        score += tag_score

        # --- Weather Score ---
        if weather_suitability in recipe["weather_suitability"] or "any" in recipe["weather_suitability"]:
            score += 5

        # --- Filter Score ---
        if meal_type and meal_type in recipe["meal_type"]:
            score += 10
        if cuisine and cuisine == recipe["cuisine"]:
            score += 10

        scored_recipes.append({"recipe": recipe, "score": score})

    # Sort recipes by score in descending order
    sorted_recommendations = sorted(scored_recipes, key=lambda x: x["score"], reverse=True)
    
    return {
        "recommendations": sorted_recommendations,
        "weather_info": weather_data
    }