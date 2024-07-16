from adrf.decorators import api_view
from rest_framework import status
from .scrapping import *
from .utils import message_json_response, get_cache, save_data_and_return


@api_view(["GET"])
async def get_tweets_by_profile(request):
    profile_name = request.query_params.get("profile_name")
    # Build full URL of the current request
    full_url = request.build_absolute_uri()
    if not profile_name:
        return message_json_response(
            status.HTTP_400_BAD_REQUEST, "error", 'Profile_name is required.'
        )
    cached_response = get_cache(full_url)
    if cached_response:
        return save_data_and_return(cached_response, profile_name)
    else:
        success, response = await fetch_tweets_by_profile(profile_name, 0, full_url)
        return save_data_and_return(response, profile_name) if success else message_json_response(
            status.HTTP_400_BAD_REQUEST, "error", 'Something Wrong'
        )


@api_view(["GET"])
async def fetch_tweets_by_hash_tag(request):
    hashtag = request.query_params.get("hashtags")
    full_url = request.build_absolute_uri()
    if not hashtag:
        return message_json_response(
            status.HTTP_400_BAD_REQUEST, "error", 'Hashtag is required.'
        )
    cached_response = get_cache(full_url)
    if cached_response:
        return save_data_and_return(cached_response, hashtag)
    else:
        success, response = await fetch_tweets_by_hashtag(hashtag, 0, full_url)
        return save_data_and_return(response, hashtag) if success else message_json_response(
            status.HTTP_400_BAD_REQUEST, "error", 'Something Wrong'
        )


#
@api_view(["GET"])
async def get_trending_hashtags(request):
    full_url = request.build_absolute_uri()
    cached_response = get_cache(full_url)
    if cached_response:
        return save_data_and_return(cached_response, 'trending_data')
    else:
        success, response = await fetch_trending_hashtags('trending_data', 0, full_url)
        return save_data_and_return(response, 'trending_data') if success else message_json_response(
            status.HTTP_400_BAD_REQUEST, "error", 'Something Wrong'
        )


@api_view(["GET"])
async def get_twitter_data_by_post_id(request):
    user_name = request.query_params.get("user_name")
    post_ids_str = request.query_params.get("post_ids")

    full_url = request.build_absolute_uri()
    if not user_name:
        return message_json_response(
            status.HTTP_400_BAD_REQUEST, "error", 'user_name is required.'
        )
    if not post_ids_str:
        return message_json_response(
            status.HTTP_400_BAD_REQUEST, "error", 'post_ids parameter is required.'
        )
    cached_response = get_cache(full_url)
    if cached_response:
        return save_data_and_return(cached_response, user_name)
    else:
        success, response = await scrape_twitter_data_by_post_id(user_name, post_ids_str, 0, full_url)
        return save_data_and_return(response, 'trending_data') if success else message_json_response(
            status.HTTP_400_BAD_REQUEST, "error", 'Something Wrong'
        )


@api_view(["GET"])
async def get_comments_of_tweet_by_post_id(request):
    user_name = request.query_params.get("user_name")
    post_ids_str = request.query_params.get("post_ids")

    full_url = request.build_absolute_uri()
    if not user_name:
        return message_json_response(
            status.HTTP_400_BAD_REQUEST, "error", 'user_name is required.'
        )
    if not post_ids_str:
        return message_json_response(
            status.HTTP_400_BAD_REQUEST, "error", 'post_ids parameter is required.'
        )
    cached_response = get_cache(full_url)
    if cached_response:
        return save_data_and_return(cached_response, user_name)
    else:
        success, response = await scrap_get_comments_of_tweet(user_name, post_ids_str, 0, full_url)
        return save_data_and_return(response, 'trending_data') if success else message_json_response(
            status.HTTP_400_BAD_REQUEST, "error", 'Something Wrong'
        )