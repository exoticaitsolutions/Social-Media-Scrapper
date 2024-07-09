from django.urls import path
from . import views

urlpatterns = [
    path(
        "v1/twitter/tweets/profile/",
        views.get_tweets_by_profile,
        name="get_Tweeted_via_profile_name",
    ),
    path(
        "v1/twitter/tweets/hashtag/",
        views.fetch_tweets_by_hash_tag,
        name="fetch_tweets_by_hash_tag",
    ),
    path(
        "v1/twitter/tweets/trending/",
        views.get_trending_hashtags,
        name="get_trending_tweets",
    ),
    path(
        "v1/twitter/tweets/post/",
        views.get_twitter_data_by_post_id,
        name="get_twitter_data_by_post_id",
    ),
    path(
        "v1/twitter/tweets/comments/",
        views.get_comments_of_tweet_by_post_id,
        name="get_comments_for_tweets",
    ),
]
