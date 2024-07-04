from .scrapping import *

@api_view(["GET"])
async def get_tweets_by_profile(request):
    """
    Fetches tweets by a given Twitter profile name.

    Args:
        request (HttpRequest): The HTTP request object containing the profile name
                               in the query parameters.

    Returns:
        JsonResponse: A JSON response with either the fetched tweet data or an error message.
    """
    try:
        profile_name = request.query_params.get("Profile_name")
        if not profile_name:
            return JsonResponse({"error": "Profile_name is required."})
        twitter_data = await fetch_tweets_by_profile(profile_name)
        return JsonResponse({"data": twitter_data})

    except (NetworkError, PageError) as e:
        logger.error(f"Error interacting with the twitter: {str(e)}")
        return JsonResponse({"error": "Error interacting with the twitter."})
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return JsonResponse({"error": "An internal error occurred."})

@api_view(["GET"])
async def get_tweets_by_hashtag(request):
    """
    Fetches tweets containing a specific hashtag.

    Args:
        request (HttpRequest): The HTTP request object containing the hashtag
                               in the query parameters.

    Returns:
        JsonResponse: A JSON response with either the fetched tweet data or an error message.
    """
    try:
        hashtag = request.query_params.get("hashtag")
        if not hashtag:
            return JsonResponse({"error": "hashtag is required."})
        twitter_data = await fetch_tweets_by_hashtag(hashtag)
        return JsonResponse({"data": twitter_data})

    except (NetworkError, PageError) as e:
        logger.error(f"Error interacting with the website: {str(e)}")
        return JsonResponse({"error": "Error interacting with the twitter."})
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return JsonResponse({"error": "An internal error occurred."})

@api_view(["GET"])
async def get_trending_hashtags(request):
    """
    Fetches trending hashtags from Twitter.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response with either the fetched trending hashtags data 
                      or an error message.
    """
    try:
        twitter_data = await fetch_trending_hashtags(request)
        return JsonResponse({"data": twitter_data})

    except (NetworkError, PageError) as e:
        logger.error(f"Error interacting with the website: {str(e)}")
        return JsonResponse({"error": "Error interacting with Twitter."})
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return JsonResponse({"error": "An internal error occurred."})

@api_view(["GET"])
async def get_twitter_data_by_post_id(request):
    """
    Fetches Twitter data for specified post IDs by a given user.

    Args:
        request (HttpRequest): The HTTP request object containing the user name
                               and post IDs in the query parameters.

    Returns:
        JsonResponse: A JSON response with either the fetched Twitter data or an error message.
    """
    try:
        user_name = request.query_params.get("user_name")
        post_ids_str = request.query_params.get("post_ids")

        if post_ids_str:
            post_ids = post_ids_str.split(",")
            post_ids = [post_id.strip() for post_id in post_ids]
            twitter_data = await scrape_twitter_data_by_post_id(
                user_name, post_ids, request
            )
            return JsonResponse({"data": twitter_data})
        else:
            return JsonResponse(
                {"error": "post_ids parameter is required."},
            )
    except (NetworkError, PageError) as e:
        logger.error(f"Error interacting with the website: {str(e)}")
        return JsonResponse({"error": "Error interacting with Twitter."})
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return JsonResponse({"error": "An internal error occurred."})

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
    try:
        user_name = request.query_params.get("user_name")
        post_ids_str = request.query_params.get("post_ids")

        if post_ids_str:
            post_ids = post_ids_str.split(",")
            post_ids = [post_id.strip() for post_id in post_ids]
            twitter_data = await scrap_get_comments_of_tweet(
                user_name, post_ids, request
            )
            return JsonResponse({"comments": twitter_data})
        else:
            return JsonResponse(
                {"error": "post_ids parameter is required."},
            )
    except (NetworkError, PageError) as e:
        logger.error(f"Error interacting with the website: {str(e)}")
        return JsonResponse({"error": "Error interacting with Twitter."})
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return JsonResponse({"error": "An internal error occurred."})
