from .scrapping import *
from .utils import *

@api_view(["GET"])
async def get_tweets_by_profile(request):
    """
    Fetches tweets by profile name.

    This view attempts to fetch tweets from Twitter based on a provided profile name. It first checks 
    if the data is available in the cache. If not, it performs web scraping to fetch the data, 
    caches it, and returns the fetched data.

    Args:
        request (HttpRequest): The request object. The request must include a 'Profile_name' query parameter.

    Returns:
        JsonResponse: A JSON response containing the tweets data for the provided profile name, or an error message 
                      if the 'Profile_name' parameter is not provided.
    """
    profile_name = request.query_params.get("Profile_name")

    # Build full URL of the current request
    full_url = request.build_absolute_uri()

    if not profile_name:
        return JsonResponse({"error": "Profile_name is required."})

    cached_response = get_cache(full_url)
    
    if cached_response:
        return save_data_and_return(cached_response, profile_name)
    else:
        Scrap_profile_data = await fetch_tweets_by_profile(profile_name, 0, full_url)
        return JsonResponse({"data": Scrap_profile_data})
    
@api_view(["GET"])
async def get_tweets_by_hashtag(request):
    """
    Fetches tweets by hashtag.

    This view attempts to fetch tweets from Twitter based on a provided hashtag. It first checks 
    if the data is available in the cache. If not, it performs web scraping to fetch the data, 
    caches it, and returns the fetched data.

    Args:
        request (HttpRequest): The request object. The request must include a 'hashtag' query parameter.

    Returns:
        JsonResponse: A JSON response containing the tweets data for the provided hashtag, or an error message 
                      if the hashtag parameter is not provided.
    """
    hashtag = request.query_params.get("hashtag")

    # Build full URL of the current request
    full_url = request.build_absolute_uri()

    if not hashtag:
        return JsonResponse({"error": "hashtag is required."})

    cached_response = get_cache(full_url)
    
    if cached_response:
        return save_data_and_return(cached_response, hashtag)
    else:
        Scrap_profile_data = await fetch_tweets_by_hashtag(hashtag, 0, full_url)
        return JsonResponse({"data": Scrap_profile_data})
    

@api_view(["GET"])
async def get_trending_hashtags(request):
    """
    Fetches trending hashtags.

    This view attempts to fetch trending hashtags from Twitter. It first checks if the data
    is available in the cache. If not, it performs web scraping to fetch the data, caches it, 
    and returns the fetched data.

    Args:
        request (HttpRequest): The request object.

    Returns:
        JsonResponse: A JSON response containing the trending hashtags data.
    """
    full_url = request.build_absolute_uri()
    cached_response = get_cache(full_url)

    if cached_response:
        return JsonResponse({"data": cached_response})
    else:
        trending_data = await fetch_trending_hashtags(request, full_url=full_url)
        return JsonResponse({"data": trending_data})
    
@api_view(["GET"])
async def get_twitter_data_by_post_id(request):
    """
    Fetches Twitter data by post IDs.

    This view attempts to fetch tweets from Twitter based on a provided username and post IDs. 
    It first checks if the data is available in the cache. If not, it performs web scraping 
    to fetch the data, caches it, and returns the fetched data.

    Args:
        request (HttpRequest): The request object. The request must include 'user_name' and 'post_ids' query parameters.

    Returns:
        JsonResponse: A JSON response containing the tweets data for the provided profile name and post IDs, 
                      or an error message if the parameters are not provided.
    """
    user_name = request.query_params.get("user_name")
    post_ids_str = request.query_params.get("post_ids")
    full_url = request.build_absolute_uri()
    
    if not user_name:
        return JsonResponse({"error": "user_name is required."})
    if not post_ids_str:
        return JsonResponse({"error": "post_ids parameter is required."})

    cached_response = get_cache(full_url)
    
    if cached_response:
        return JsonResponse({"data": cached_response})
    
    post_ids = post_ids_str.split(",")
    post_ids = [post_id.strip() for post_id in post_ids]
    twitter_data = await scrape_twitter_data_by_post_id(user_name, post_ids, request, full_url=full_url)
    return JsonResponse({"data": twitter_data})




@api_view(["GET"])
async def get_comments_of_tweet(request):
    """
    Fetches comments for specified tweet post IDs by a given user.

    Args:
        request (HttpRequest): The HTTP request object containing the user name
                               and post IDs in the query parameters.

    Returns:
        JsonResponse: A JSON response with either the fetched comments or an error message.
    """
    user_name = request.query_params.get("user_name")
    post_ids_str = request.query_params.get("post_ids")
    full_url = request.build_absolute_uri()
    
    if not user_name:
        return JsonResponse({"error": "user_name is required."})
    if not post_ids_str:
        return JsonResponse({"error": "post_ids parameter is required."})

    cached_response = get_cache(full_url)
    
    if cached_response:
        return JsonResponse({"data": cached_response})
    
    post_ids = post_ids_str.split(",")
    post_ids = [post_id.strip() for post_id in post_ids]
    twitter_data = await scrap_get_comments_of_tweet(user_name, post_ids, request, full_url=full_url)
    return JsonResponse({"data": twitter_data})
    