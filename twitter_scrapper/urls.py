from django.urls import path
from .views import (
    get_tweets_by_profile,
    get_tweets_by_hashtag,
    get_trending_hashtags,
    get_twitter_data_by_post_id,
    get_comments_of_tweet,
)

urlpatterns = [
    path("get-tweets-by-profile/", get_tweets_by_profile, name="get-tweets-by-profile"),
    path("get-tweets-by-hashtag/", get_tweets_by_hashtag, name="get-tweets-by-hashtag"),
    path("get-trending-hashtags/", get_trending_hashtags, name="get-trending-hashtags"),
    path(
        "get-twitter-data-by-post-id/",
        get_twitter_data_by_post_id,
        name="get-twitter-data-by-post-id",
    ),
    path("get-comments-of-tweet/", get_comments_of_tweet, name="get-comments-of-tweet"),
]
