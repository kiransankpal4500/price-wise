# Core recommendation algorithm for selecting the best product listing across platforms

# Normalizes a numeric value to a 0-1 scale relative to minimum and maximum range
def normalize_metric(val: float, min_val: float, max_val: float) -> float:
    if max_val > min_val:
        return (val - min_val) / (max_val - min_val)
    return 1.0

# Calculates relative scores and determines the optimal platform listing for a product
def calculate_best_product(platform_listings: list) -> dict:
    if not platform_listings:
        return {"bestPickPlatform": "", "platformsWithScores": [], "bestPickScore": 0}

    # Helper function to access fields whether listing is a dict or Pydantic object
    def get_val(item, key, default=None):
        if isinstance(item, dict):
            return item.get(key, default)
        return getattr(item, key, default)

    # Extract price range across all available store listings
    prices = [get_val(p, 'price') for p in platform_listings if get_val(p, 'price') is not None]
    min_price = min(prices) if prices else 0.0
    max_price = max(prices) if prices else 0.0

    # Extract rating range across all store listings
    ratings = [get_val(p, 'rating') for p in platform_listings if get_val(p, 'rating') is not None]
    min_rating = min(ratings) if ratings else 0.0
    max_rating = max(ratings) if ratings else 5.0

    # Extract review counts only for stores that provide review data
    reviews = [get_val(p, 'reviewCount') for p in platform_listings if get_val(p, 'reviewCount') is not None]
    min_reviews = min(reviews) if reviews else 0
    max_reviews = max(reviews) if reviews else 0

    highest_score = -1.0
    best_platform_name = ""
    scored_platforms = []

    # Score each platform using relative price, rating, and review metrics
    for listing in platform_listings:
        p_name = get_val(listing, 'platformName', '')
        price = get_val(listing, 'price', 0.0)
        rating = get_val(listing, 'rating', 0.0)
        review_count = get_val(listing, 'reviewCount')
        in_stock = get_val(listing, 'inStock', True)

        # 1. Price Score: Inverted so lower prices produce higher scores
        if max_price > min_price:
            price_score = (max_price - price) / (max_price - min_price)
        else:
            price_score = 1.0

        # 2. Rating Score: Higher rating gives higher score relative to min/max ratings
        if max_rating > min_rating:
            rating_score = (rating - min_rating) / (max_rating - min_rating)
        else:
            rating_score = rating / 5.0

        # 3. Review Count Score: Evaluates social proof if review count is present
        review_score = None
        if review_count is not None:
            if max_reviews > min_reviews:
                review_score = (review_count - min_reviews) / (max_reviews - min_reviews)
            else:
                review_score = 0.5

        # Weighted formula calculation with proportional weight redistribution for missing reviews
        if review_score is not None:
            # Standard weights: Price 40%, Rating 35%, Reviews 25%
            final_score = (0.4 * price_score) + (0.35 * rating_score) + (0.25 * review_score)
        else:
            # Exclude review factor and redistribute 25% weight proportionally to price and rating
            price_weight = 0.4 / 0.75
            rating_weight = 0.35 / 0.75
            final_score = (price_weight * price_score) + (rating_weight * rating_score)

        # Apply out-of-stock penalty to prioritize available items
        if not in_stock:
            final_score *= 0.5

        # Convert score to an integer out of 100 for display
        computed_score = round(final_score * 100)

        # Track the platform with the highest overall score
        if final_score > highest_score:
            highest_score = final_score
            best_platform_name = p_name

        # Create updated listing with computed score
        if isinstance(listing, dict):
            updated_item = dict(listing)
            updated_item['computedScore'] = computed_score
        else:
            updated_item = listing.model_copy(update={'computedScore': computed_score})
        
        scored_platforms.append(updated_item)

    # Return winning platform name and full platform list with calculated scores
    return {
        "bestPickPlatform": best_platform_name,
        "platformsWithScores": scored_platforms,
        "bestPickScore": round(highest_score * 100) if highest_score >= 0 else 0
    }
