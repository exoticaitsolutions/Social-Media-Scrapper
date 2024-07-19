import asyncio
import logging
import re
import time
import re

from django.http import JsonResponse
from pyppeteer.errors import NetworkError, PageError

from .utils import login, set_cache
from django.core.cache import cache

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
NUMBER_OF_POSTS = 5
NUMBER_OF_COMMENTS = 3
MAX_THREAD_COUNT = 5
MAX_EXCEPTION_RETRIES = 3
CACHE_TIMEOUT = 3600


async def retry_exception(
    recalling_method_name, any_generic_parameter, retry_count=0, exception_name=None
):
    """
    retry calling a method after encountering an exception up to a maximum number of retries.

    Args:
        recalling_method_name (function): The method to retry.
        any_generic_parameter (object): Any parameter required by the method.
        retry_count (int, optional): Current retry attempt count. defaults to 0.
        exception_name (str, optional): Name of the exception encountered. defaults to None.

    Returns:
        dict or JsonResponse: Result of the retried method call or a JSON response indicating error.
    """
    # If tweet elements are not found, check if retry attempts are exhausted
    if retry_count < MAX_EXCEPTION_RETRIES:
        retry_count += 1
        # Retry the function after a delay
        print(
            f"******* Retrying attempt after {exception_name} in {recalling_method_name.__name__}, Attempt #: {retry_count}"
        )
        await asyncio.sleep(3)
        return await recalling_method_name(any_generic_parameter, retry_count)
    else:
        print(
            "!!!!!!!!!!!!! All the retry attempts exhausted. Throwing error now........"
        )
        return JsonResponse({"error": "Element not found"})


async def fetch_tweets_by_profile(profile_name, retry_count=0, full_url=None):
    """
    Fetches tweets from a specific profile on Twitter.

    Args:
        profile_name (str): The Twitter profile name to search for and fetch tweets.
        retry_count (int, optional): Number of retries attempted in case of failure. Defaults to 0.
        full_url (str, optional): The full URL of the request for caching purposes. Defaults to None.

    Returns:
        list: A list of dictionaries containing tweet data, saved to a JSON file and cached.
    """
    start_time = time.time()

    success, message, browser, page = await login()
    if not success:
        return success, message
    twitter_data = []
    try:
        print(f"login status  {message}")
        await page.waitForXPath("//input[@data-testid='SearchBox_Search_Input']")
        search_box = await page.xpath("//input[@data-testid='SearchBox_Search_Input']")
        print("Search element is found")
        await asyncio.sleep(3)
        await search_box[0].type(profile_name)
        print("Search element is found and type the values")
        await search_box[0].press("Enter")
        print("Entered the subject and clicked Successfully !!")
        await asyncio.sleep(3)
        await page.waitForXPath("//span[contains(text(),'People')]")
        people_button = await page.xpath("//span[contains(text(),'People')]")
        print("people element is found")
        await people_button[0].click()
        print("Clicked on People Successfully !!")
        await asyncio.sleep(3)
        await page.waitForXPath(
            "//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/section/div/div/div[1]/div/div/button/div/div[2]/div[1]/div[1]/div/div[1]/a/div/div[1]/span/span[1]"
        )
        profile_button = await page.xpath(
            "//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/section/div/div/div[1]/div/div/button/div/div[2]/div[1]/div[1]/div/div[1]/a/div/div[1]/span/span[1]"
        )
        print("profile_button element is found}")
        await profile_button[0].click()
        print("Clicked on Profile Successfully !!")
        await asyncio.sleep(3)

        UserTags, TimeStamps, Tweets, Replies, Retweets, Likes = [], [], [], [], [], []
        # Scrape tweets
        while len(Tweets) < NUMBER_OF_POSTS:
            await page.waitForXPath("//article[@data-testid='tweet']")
            articles = await page.xpath("//article[@data-testid='tweet']")

            for article in articles:
                try:
                    UserTag = await article.querySelectorEval(
                        'div[dir="ltr"] span', "node => node.innerText"
                    )
                except Exception:
                    UserTag = ""
                UserTags.append(UserTag)

                timestamp = await article.querySelectorEval(
                    "time", 'node => node.getAttribute("datetime")'
                )
                TimeStamps.append(timestamp)

                tweet = await article.querySelectorEval(
                    "div[lang]", "node => node.innerText"
                )
                Tweets.append(tweet)

                try:
                    reply = await page.evaluate(
                        "(article) => article.querySelector(\"[data-testid='reply']\").innerText",
                        article,
                    )
                except Exception:
                    reply = "0"
                Replies.append(reply)

                try:
                    retweet = await page.evaluate(
                        "(article) => article.querySelector(\"[data-testid='retweet'] span\").innerText",
                        article,
                    )
                except Exception:
                    retweet = "0"
                Retweets.append(retweet)

                try:
                    like = await page.evaluate(
                        "(article) => article.querySelector(\"[data-testid='like'] span\").innerText",
                        article,
                    )
                except Exception:
                    like = "0"
                Likes.append(like)

                if len(Tweets) >= NUMBER_OF_POSTS:
                    break

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)

        twitter_data = [
            {
                "Name": profile_name,
                "UserTag": UserTags[i],
                "Timestamp": TimeStamps[i],
                "TweetContent": Tweets[i],
                "Reply": Replies[i],
                "Retweet": Retweets[i],
                "Like": Likes[i],
            }
            for i in range(len(UserTags))
        ]
    except (NetworkError, PageError) as e:
        print(f"Error interacting with Twitter: {str(e)}")
        await browser.close()
        return await retry_exception(
            fetch_tweets_by_profile, profile_name, retry_count, str(e)
        )
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        await browser.close()
        return await retry_exception(
            fetch_tweets_by_profile, profile_name, retry_count, str(e)
        )
    finally:
        end_time = time.time()
        total_time = end_time - start_time  # Calculate the total time of execution
        await browser.close()
        print(f"Total execution time: {total_time:.2f} seconds")
    cache.set(full_url, twitter_data, timeout=CACHE_TIMEOUT)
    return True, twitter_data


async def fetch_tweets_by_hashtag(hashtag, retry_count=0, full_url=None):
    """
    Fetches tweets based on a given hashtag.

    Args:
        hashtag (str): The hashtag to search for.
        retry_count (int, optional): The current retry attempt count. Defaults to 0.
        full_url (str, optional): The full URL used for caching. Defaults to None.

    Returns:
        tuple: A tuple containing a boolean indicating success and either a list of fetched tweet
               data or an error message.
    """
    start_time = time.time()
    twitter_data = []

    # Login and get browser and page instances
    success, message, browser, page = await login()
    if not success:
        return success, message

    try:
        print(f"Login status: {message}")

        # Wait for the search box and enter the hashtag
        await page.waitForXPath("//input[@data-testid='SearchBox_Search_Input']")
        search_box = await page.xpath("//input[@data-testid='SearchBox_Search_Input']")
        print("Search element is found")
        await asyncio.sleep(5)  # Wait for 5 seconds
        await search_box[0].type(hashtag)
        print("Typed hashtag into search box")
        await search_box[0].press("Enter")
        print("Entered the subject and clicked Successfully !!")
        await asyncio.sleep(3)

        # Initialize lists to store tweet data
        UserTags, TimeStamps, Tweets, Replies, Retweets, Likes = [], [], [], [], [], []

        while len(Tweets) < NUMBER_OF_POSTS:
            await page.waitForXPath("//article[@data-testid='tweet']")
            articles = await page.xpath("//article[@data-testid='tweet']")

            for article in articles:
                try:
                    UserTag = await article.querySelectorEval(
                        'div[dir="ltr"] span', "node => node.innerText"
                    )
                except Exception:
                    UserTag = ""
                UserTags.append(UserTag)

                timestamp = await article.querySelectorEval(
                    "time", 'node => node.getAttribute("datetime")'
                )
                TimeStamps.append(timestamp)

                tweet = await article.querySelectorEval(
                    "div[lang]", "node => node.innerText"
                )
                Tweets.append(tweet)

                try:
                    reply = await page.evaluate(
                        "(article) => article.querySelector(\"[data-testid='reply']\").innerText",
                        article,
                    )
                except Exception:
                    reply = "0"
                Replies.append(reply)

                try:
                    retweet = await page.evaluate(
                        "(article) => article.querySelector(\"[data-testid='retweet'] span\").innerText",
                        article,
                    )
                except Exception:
                    retweet = "0"
                Retweets.append(retweet)

                try:
                    like = await page.evaluate(
                        "(article) => article.querySelector(\"[data-testid='like'] span\").innerText",
                        article,
                    )
                except Exception:
                    like = "0"
                Likes.append(like)

                if len(Tweets) >= NUMBER_OF_POSTS:
                    break

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)

        twitter_data = [
            {
                "Name": hashtag,
                "UserTag": UserTags[i],
                "Timestamp": TimeStamps[i],
                "TweetContent": Tweets[i],
                "Reply": Replies[i],
                "Retweet": Retweets[i],
                "Like": Likes[i],
            }
            for i in range(len(UserTags))
        ]

    except (NetworkError, PageError) as e:
        print(f"Error interacting with Twitter: {str(e)}")
        await browser.close()
        return await retry_exception(
            fetch_tweets_by_hashtag, hashtag, retry_count + 1, full_url
        )
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        await browser.close()
        return await retry_exception(
            fetch_tweets_by_hashtag, hashtag, retry_count + 1, full_url
        )
    finally:
        end_time = time.time()
        total_time = end_time - start_time
        await browser.close()
        print(f"Total execution time: {total_time:.2f} seconds")

    cache.set(full_url, twitter_data, timeout=CACHE_TIMEOUT)
    return True, twitter_data


async def fetch_tweets_by_hashtag(hashtag, retry_count=0, full_url=None):
    """
    Fetches tweets based on a given hashtag.

    Args:
        hashtag (str): The hashtag to search for.
        retry_count (int, optional): The current retry attempt count. Defaults to 0.
        full_url (str, optional): The full URL used for caching. Defaults to None.

    Returns:
        tuple: A tuple containing a boolean indicating success and either a list of fetched tweet
               data or an error message.
    """
    start_time = time.time()
    twitter_data = []

    # Login and get browser and page instances
    success, message, browser, page = await login()
    if not success:
        return success, message

    try:
        print(f"Login status: {message}")

        # Wait for the search box and enter the hashtag
        await page.waitForXPath("//input[@data-testid='SearchBox_Search_Input']")
        search_box = await page.xpath("//input[@data-testid='SearchBox_Search_Input']")
        print("Search element is found")
        await asyncio.sleep(5)  # Wait for 5 seconds
        await search_box[0].type(hashtag)
        print("Typed hashtag into search box")
        await search_box[0].press("Enter")
        print("Entered the subject and clicked Successfully !!")
        await asyncio.sleep(3)

        # Initialize lists to store tweet data
        UserTags, TimeStamps, Tweets, Replies, Retweets, Likes = [], [], [], [], [], []

        while len(Tweets) < NUMBER_OF_POSTS:
            await page.waitForXPath("//article[@data-testid='tweet']")
            articles = await page.xpath("//article[@data-testid='tweet']")

            for article in articles:
                try:
                    UserTag = await article.querySelectorEval(
                        'div[dir="ltr"] span', "node => node.innerText"
                    )
                except Exception:
                    UserTag = ""
                UserTags.append(UserTag)

                try:
                    timestamp = await article.querySelectorEval(
                        "time", 'node => node.getAttribute("datetime")'
                    )
                except Exception:
                    timestamp = ""
                TimeStamps.append(timestamp)

                tweet = await article.querySelectorEval(
                    "div[lang]", "node => node.innerText"
                )
                Tweets.append(tweet)

                try:
                    reply = await page.evaluate(
                        "(article) => article.querySelector(\"[data-testid='reply']\").innerText",
                        article,
                    )
                except Exception:
                    reply = "0"
                Replies.append(reply)

                try:
                    retweet = await page.evaluate(
                        "(article) => article.querySelector(\"[data-testid='retweet'] span\").innerText",
                        article,
                    )
                except Exception:
                    retweet = "0"
                Retweets.append(retweet)

                try:
                    like = await page.evaluate(
                        "(article) => article.querySelector(\"[data-testid='like'] span\").innerText",
                        article,
                    )
                except Exception:
                    like = "0"
                Likes.append(like)

                if len(Tweets) >= NUMBER_OF_POSTS:
                    break

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)

        twitter_data = [
            {
                "Name": hashtag,
                "UserTag": UserTags[i],
                "Timestamp": TimeStamps[i],
                "TweetContent": Tweets[i],
                "Reply": Replies[i],
                "Retweet": Retweets[i],
                "Like": Likes[i],
            }
            for i in range(len(UserTags))
        ]

    except (NetworkError, PageError) as e:
        print(f"Error interacting with Twitter: {str(e)}")
        await browser.close()
        return await retry_exception(
            fetch_tweets_by_hashtag, hashtag, retry_count + 1, full_url
        )
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        await browser.close()
        return await retry_exception(
            fetch_tweets_by_hashtag, hashtag, retry_count + 1, full_url
        )
    finally:
        end_time = time.time()
        total_time = end_time - start_time
        await browser.close()
        print(f"Total execution time: {total_time:.2f} seconds")

    cache.set(full_url, twitter_data, timeout=CACHE_TIMEOUT)
    return True, twitter_data


async def fetch_trending_hashtags(trending_data, retry_count=0, full_url=None):
    """
    Fetches trending hashtags from Twitter's explore page.

    This function logs into Twitter, navigates to the trending keywords page, scrolls through the page
    to load all trending topics, and extracts relevant information about each trending topic. The data
    is stored in a list and cached for future use.

    Args:
        trending_data (list): A list to store the fetched trending data.
        retry_count (int, optional): The current retry attempt count. Defaults to 0.
        full_url (str, optional): The full URL used for caching. Defaults to None.

    Returns:
        tuple: A tuple containing a boolean indicating success and either a list of fetched trending
               data or an error message.
    """
    start_time = time.time()
    twitter_data = []
    success, message, browser, page = await login()
    if not success:
        return success, message
    try:
        print(f"login status  {message}")
        print(
            f"Opening trending url page from URL: {'https://x.com/explore/tabs/keyword'}"
        )
        await page.goto(
            "https://x.com/explore/tabs/keyword", waitUntil="domcontentloaded"
        )
        await page.waitForNavigation()
        print(f"opened  successfully")
        await asyncio.sleep(4)
        await page.waitForXPath('//*[@data-testid="cellInnerDiv"]')
        # Scroll up by 30%
        await page.evaluate("window.scrollBy(0, -document.body.scrollHeight * 0.3);")
        await asyncio.sleep(3)
        last_height = await page.evaluate("() => document.body.scrollHeight")
        print(f"last_height element is found")
        while True:
            await page.evaluate("window.scrollBy(0, 200);")
            await asyncio.sleep(3)  # Random sleep to simulate human interaction
            new_height = await page.evaluate("() => document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        trending_topics_elements = await page.xpath('//*[@data-testid="trend"]')
        print(f"trending_topics_elements element is found {trending_topics_elements}")
        elements1 = await page.xpath(
            '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/section/div/div/div[3]/div/div/div'
        )
        print(f"elements1 element is found {elements1}")
        text_content1 = await page.evaluate(
            "(element) => element.textContent", elements1[0]
        )
        print(f"text_content1 element is found")
        print(f"Found {len(trending_topics_elements)} trending topics elements.")
        for index, element in enumerate(trending_topics_elements, start=1):
            text = await (await element.getProperty("textContent")).jsonValue()
            if "Trending" in text:
                data = text.split("·")
                if len(data) == 2:
                    combined = data[1].strip()
                    category = "Trending"
                elif len(data) == 3:
                    category = data[1].strip()
                    combined = data[2].strip()
                else:
                    return None
                # Extracting a trending
                type_trending_match = re.search(r"Trending(.+?)(?=\d|$)", combined)
                # Extracting posts with optional commas and decimals
                posts_match = re.search(
                    r"([\d,\.]+K?)\s*posts", combined, re.IGNORECASE
                )
                item = {
                    "id": data[0],
                    "type": category,
                    "trending": (
                        type_trending_match.group(1).strip()
                        if type_trending_match
                        else ""
                    ),
                    "posts": (
                        posts_match.group(1).strip() + " posts" if posts_match else "0"
                    ),
                }
                twitter_data.append(item)
    except (NetworkError, PageError) as e:
        print(f"Error interacting with Twitter: {str(e)}")
        await browser.close()
        return await retry_exception(
            fetch_trending_hashtags, trending_data, retry_count, str(e)
        )
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        await browser.close()
        return await retry_exception(
            fetch_trending_hashtags, trending_data, retry_count, str(e)
        )
    finally:
        end_time = time.time()
        total_time = end_time - start_time  # Calculate the total time of execution
        await browser.close()
        print(f"Total execution time: {total_time:.2f} seconds")
    cache.set(full_url, twitter_data, timeout=CACHE_TIMEOUT)
    return True, twitter_data


async def scrape_twitter_data_by_post_id(
    user_name, post_ids_str, retry_count=0, full_url=None
):
    """
    Scrapes detailed information from specified tweet posts for a given Twitter user.

    This function logs into Twitter, navigates to each specified tweet, extracts tweet content, image URL,
    reply count, like count, repost count, bookmark count, and timestamp, and stores the data in a list.

    Args:
        user_name (str): The Twitter username whose tweets are to be scraped.
        post_ids_str (str): Comma-separated string of tweet post IDs to scrape.
        retry_count (int, optional): The current retry attempt count. Defaults to 0.
        full_url (str, optional): The full URL used for caching. Defaults to None.

    Returns:
        tuple: A tuple containing a boolean indicating success and either a list of scraped tweet data
               or an error message.
    """
    start_time = time.time()
    twitter_data = []
    success, message, browser, page = await login()
    if not success:
        return success, message
    try:
        print(f"login status  {message}")
        post_ids = post_ids_str.split(",")
        post_ids = [post_id.strip() for post_id in post_ids]
        for post_id in post_ids:
            twitter_url = f"https://twitter.com/{user_name}/status/{post_id}"

            print(f"Opening trending url page from URL: {twitter_url}")
            await page.goto(twitter_url, waitUntil="domcontentloaded")
            await page.waitForNavigation()
            print(f"opened  successfully")
            await asyncio.sleep(4)
            # Scroll down 30% of the page height
            await page.evaluate("window.scrollBy(0, window.innerHeight * 0.5);")
            print("scrolling................")
            await asyncio.sleep(4)
            # Extract tweet content
            tweet_content = await page.evaluate(
                "() => document.querySelector(\"div[data-testid='tweetText']\").textContent"
            )
            image_url = await page.evaluate(
                '() => document.querySelector("div[data-testid=\'tweetPhoto\'] img").getAttribute("src")'
            )
            reply_count = await page.evaluate(
                "() => document.querySelector(\"button[data-testid='reply']\").textContent"
            )
            like_count = await page.evaluate(
                "() => document.querySelector(\"button[data-testid='like']\").textContent"
            )
            repost_count = await page.evaluate(
                "() => document.querySelector(\"button[data-testid='retweet']\").textContent"
            )
            bookmark_count = await page.evaluate(
                "() => document.querySelector(\"button[data-testid='bookmark']\").textContent"
            )
            timestamp = await page.evaluate(
                '() => document.querySelector("time").getAttribute("datetime")'
            )
            twitter_data.append(
                {
                    "username": user_name,
                    "tweet_content": tweet_content.strip() if tweet_content else "",
                    "image_url": image_url if image_url else "",
                    "reply_count": reply_count.strip() if reply_count else "0",
                    "like_count": like_count.strip() if like_count else "0",
                    "repost_count": repost_count.strip() if repost_count else "0",
                    "bookmark_count": bookmark_count.strip() if bookmark_count else "0",
                    "timestamp": timestamp if timestamp else "",
                }
            )
    except (NetworkError, PageError) as e:
        print(f"Error interacting with Twitter: {str(e)}")
        await browser.close()
        return await retry_exception(
            scrape_twitter_data_by_post_id, user_name, post_ids_str, retry_count, str(e)
        )
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        await browser.close()
        return await retry_exception(
            scrape_twitter_data_by_post_id, user_name, post_ids_str, retry_count, str(e)
        )
    finally:
        end_time = time.time()
        total_time = end_time - start_time  # Calculate the total time of execution
        await browser.close()
        print(f"Total execution time: {total_time:.2f} seconds")
    cache.set(full_url, twitter_data, timeout=CACHE_TIMEOUT)
    return True, twitter_data


# async def scrap_get_comments_of_tweet(user_name, post_ids_str, retry_count=0, full_url=None):
#     """
#     Scrapes comments from specified tweet posts for a given Twitter user.

#     Args:
#         user_name (str): The Twitter username to scrape comments from.
#         post_ids_str (str): Comma-separated string of tweet post IDs to scrape.
#         retry_count (int, optional): The current retry attempt count. Defaults to 0.
#         full_url (str, optional): The full URL used for caching. Defaults to None.

#     Returns:
#         tuple: A tuple containing a boolean indicating success and either a list of comment data
#                or an error message.
#     """
#     start_time = time.time()
#     twitter_data = []
#     success, message, browser, page = await login()
#     if not success:
#         return success, message
#     try:
#         print("login status")
#         post_ids = post_ids_str.split(",")
#         post_ids = [post_id.strip() for post_id in post_ids]
#         for post_id in post_ids:
#             twitter_url = f"https://twitter.com/{user_name}/status/{post_id}"

#             print(f"Opening tweet page from URL: {twitter_url}")
#             await page.goto(twitter_url, waitUntil="domcontentloaded")
#             await page.waitForNavigation()
#             print("Page opened successfully")
#             await asyncio.sleep(4)
#             while len(twitter_data) < NUMBER_OF_COMMENTS:
#                 await page.evaluate("window.scrollBy(0, window.innerHeight * 0.5);")
#                 await asyncio.sleep(4)
#                 elements = await page.xpath("//*[@role='article']")
#                 print("Elements found")
#                 for element in elements:
#                     comment_text = await (await element.getProperty("textContent")).jsonValue()
#                     if comment_text:
#                         comment_text = comment_text.strip()
#                         name_match = re.search(r"^(.*?)(@[\w_]+)", comment_text)
#                         time_match = re.search(r"(\d{1,2}:\d{2} [APM]{2} \u00b7 \w{3} \d{1,2}, \d{4})", comment_text)
#                         likes_match = re.search(r"(\d+\.\d+K|\d+K|\d+)", comment_text)
#                         views_match = re.search(r"(\d+\.\d+K|\d+K|\d+)\s+Views", comment_text)

#                         name = name_match.group(1).strip() if name_match else "N/A"
#                         username = name_match.group(2).strip() if name_match else "N/A"
#                         timed = time_match.group(0).strip() if time_match else "N/A"
#                         comment = (comment_text.split(time_match.group(0))[0].strip() if time_match else comment_text)
#                         extra, comment = comment.split("h", 1)
#                         likes = likes_match.group(0).strip() if likes_match else "N/A"
#                         views = views_match.group(1).strip() if views_match else "N/A"

#                         item = {
#                             "Name": name,
#                             "Username": username,
#                             "Comment": comment,
#                             "Likes": likes,
#                         }
#                         twitter_data.append(item)
#     except (NetworkError, PageError) as e:
#         print(f"Error interacting with Twitter: {str(e)}")
#         await browser.close()
#         return await retry_exception(scrap_get_comments_of_tweet, user_name, post_ids_str, retry_count, str(e))
#     except Exception as e:
#         print(f"An unexpected error occurred: {str(e)}")
#         await browser.close()
#         return await retry_exception(scrap_get_comments_of_tweet, user_name, post_ids_str, retry_count, str(e))
#     finally:
#         end_time = time.time()
#         total_time = end_time - start_time  # Calculate the total time of execution
#         await browser.close()
#         print(f"Total execution time: {total_time:.2f} seconds")

#     cache.set(full_url, twitter_data, timeout=CACHE_TIMEOUT)
#     return True, twitter_data


async def scrap_get_comments_of_tweet(
    user_name, post_ids_str, retry_count=0, full_url=None
):
    """
    Scrapes comments from specified tweet posts for a given Twitter user.

    Args:
        user_name (str): The Twitter username to scrape comments from.
        post_ids_str (str): Comma-separated string of tweet post IDs to scrape.
        retry_count (int, optional): The current retry attempt count. Defaults to 0.
        full_url (str, optional): The full URL used for caching. Defaults to None.

    Returns:
        tuple: A tuple containing a boolean indicating success and either a list of comment data
               or an error message.
    """
    start_time = time.time()
    twitter_data = []
    success, message, browser, page = await login()
    if not success:
        return success, message
    try:
        print("login status")
        post_ids = post_ids_str.split(",")
        post_ids = [post_id.strip() for post_id in post_ids]
        for post_id in post_ids:
            twitter_url = f"https://twitter.com/{user_name}/status/{post_id}"

            print(f"Opening tweet page from URL: {twitter_url}")
            await page.goto(twitter_url, waitUntil="domcontentloaded")
            await page.waitForNavigation()
            print("Page opened successfully")
            await asyncio.sleep(4)
            while len(twitter_data) < NUMBER_OF_COMMENTS:
                await page.evaluate("window.scrollBy(0, window.innerHeight * 0.5);")
                await asyncio.sleep(4)
                elements = await page.xpath("//*[@role='article']")
                print("Elements found")
                for element in elements:
                    comment_text = await (
                        await element.getProperty("textContent")
                    ).jsonValue()
                    if comment_text:
                        comment_text = comment_text.strip()
                        name_match = re.search(r"^(.*?)(@[\w_]+)", comment_text)
                        time_match = re.search(
                            r"(\d{1,2}:\d{2} [APM]{2} \u00b7 \w{3} \d{1,2}, \d{4})",
                            comment_text,
                        )
                        likes_match = re.search(r"(\d+\.\d+K|\d+K|\d+)", comment_text)
                        views_match = re.search(
                            r"(\d+\.\d+K|\d+K|\d+)\s+Views", comment_text
                        )

                        name = name_match.group(1).strip() if name_match else "N/A"
                        username = name_match.group(2).strip() if name_match else "N/A"
                        timed = time_match.group(0).strip() if time_match else "N/A"
                        comment = (
                            comment_text.split(time_match.group(0))[0].strip()
                            if time_match
                            else comment_text
                        )
                        # extra, comment = comment.split("h", 1)
                        likes = likes_match.group(0).strip() if likes_match else "N/A"
                        views = views_match.group(1).strip() if views_match else "N/A"

                        item = {
                            "Name": name,
                            "Username": username,
                            "Comment": comment,
                            "Likes": likes,
                        }
                        twitter_data.append(item)
    except (NetworkError, PageError) as e:
        print(f"Error interacting with Twitter: {str(e)}")
        await browser.close()
        return await retry_exception(
            scrap_get_comments_of_tweet,
            user_name,
            post_ids_str,
            retry_count,
            str(e),
            full_url,
        )
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        await browser.close()
        return await retry_exception(
            scrap_get_comments_of_tweet,
            user_name,
            post_ids_str,
            retry_count,
            str(e),
            full_url,
        )
    finally:
        end_time = time.time()
        total_time = end_time - start_time  # Calculate the total time of execution
        await browser.close()
        print(f"Total execution time: {total_time:.2f} seconds")

    cache.set(full_url, twitter_data, timeout=CACHE_TIMEOUT)
    return True, twitter_data
