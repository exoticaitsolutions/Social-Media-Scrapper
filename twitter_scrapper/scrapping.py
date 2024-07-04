from django.http import JsonResponse
from adrf.decorators import api_view
import asyncio
import logging
from pyppeteer.errors import NetworkError, PageError
import time
import json
import re
from .utils import login

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
NUMBER_OF_POSTS = 3
NUMBER_OF_COMMENTS = 3
MAX_THREAD_COUNT = 5
MAX_EXCEPTION_RETRIES = 3


async def retry_exception(
    recalling_method_name, any_generic_parameter, retry_count=0, exception_name=None
):
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

async def fetch_tweets_by_profile(profile_name, retry_count=0):
    try:
        browser, page = await login()
        start_time = time.time()

        await page.waitForXPath("//input[@data-testid='SearchBox_Search_Input']")
        search_box = await page.xpath("//input[@data-testid='SearchBox_Search_Input']")
        await search_box[0].type(profile_name)
        await search_box[0].press("Enter")
        print("Entered the subject and clicked Successfully !!")
        await asyncio.sleep(4)

        await page.waitForXPath("//span[contains(text(),'People')]")
        people_button = await page.xpath("//span[contains(text(),'People')]")
        await people_button[0].click()
        print("Clicked on People Successfully !!")
        await asyncio.sleep(4)

        await page.waitForXPath(
            "//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/section/div/div/div[1]/div/div/button/div/div[2]/div[1]/div[1]/div/div[1]/a/div/div[1]/span/span[1]"
        )
        profile_button = await page.xpath(
            "//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/section/div/div/div[1]/div/div/button/div/div[2]/div[1]/div[1]/div/div[1]/a/div/div[1]/span/span[1]"
        )
        await profile_button[0].click()
        print("Clicked on Profile Successfully !!")

        await asyncio.sleep(5)

        await page.setViewport(
            {"width": 1920, "height": 1080}
        )
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

        with open(f"{profile_name}.json", "w") as json_file:
            json.dump(twitter_data, json_file, indent=4)

        print("Total Posts", len(twitter_data))
        end_time = time.time()
        total_time = end_time - start_time  # Calculate the total time of execution
        print(f"Total execution time: {total_time:.2f} seconds")

        await browser.close()
        return twitter_data

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

async def fetch_tweets_by_hashtag(hashtag, retry_count=0):
    browser, page = await login()
    try:
        start_time = time.time()
        await page.waitForXPath("//input[@data-testid='SearchBox_Search_Input']")
        search_box = await page.xpath("//input[@data-testid='SearchBox_Search_Input']")
        await search_box[0].type(hashtag)
        await search_box[0].press("Enter")
        print("Entered the subject and clicked Successfully !!")
        await asyncio.sleep(3)
        await page.setViewport(
            {"width": 1920, "height": 1080}
        )  # Adjust dimensions as needed

        UserTags = []
        TimeStamps = []
        Tweets = []
        Replies = []
        Retweets = []
        Likes = []
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

        # Create JSON structure
        twitter_data = []
        for i in range(len(UserTags)):
            tweet_data = {
                "Name": hashtag,
                "UserTag": UserTags[i],
                "Timestamp": TimeStamps[i],
                "TweetContent": Tweets[i],
                "Reply": Replies[i],
                "Retweet": Retweets[i],
                "Like": Likes[i],
            }
            # print("Total Posts", len(twitter_data))
            twitter_data.append(tweet_data)

        # Save data to a JSON file
        with open(f"{hashtag}.json", "w") as json_file:
            json.dump(twitter_data, json_file, indent=4)

        await browser.close()
        print("Total Posts", len(twitter_data))
        end_time = time.time()  # Record the end time
        total_time = end_time - start_time  # Calculate the total time
        print(f"Total execution time: {total_time:.2f} seconds")
        await browser.close()
        return twitter_data

    except (NetworkError, PageError) as e:
        print(f"Error interacting with Twitter: {str(e)}")
        await browser.close()
        return await retry_exception(
            fetch_tweets_by_hashtag, hashtag, retry_count, str(e)
        )
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        await browser.close()
        return await retry_exception(
            fetch_tweets_by_hashtag, hashtag, retry_count, str(e)
        )


async def fetch_trending_hashtags(request, retry_count=0):
    browser, page = await login()
    try:
        start_time = time.time()
        await page.waitForXPath(
            "/html/body/div[1]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[2]/div/div[2]/span"
        )
        # Click the element
        explore_btn = await page.xpath(
            "/html/body/div[1]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[2]/div/div[2]/span"
        )
        await explore_btn[0].click()
        print("Clicked on Explore Button successfully.")
        await asyncio.sleep(4)

        trending_btn = await page.xpath(
            "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div[2]/nav/div/div[2]/div/div[2]/a/div/div/span"
        )
        await trending_btn[0].click()
        print("Clicked on Trending Button successfully.")

        await page.waitForXPath('//*[@data-testid="cellInnerDiv"]')
        # Scroll up by 30%
        await page.evaluate("window.scrollBy(0, -document.body.scrollHeight * 0.3);")
        await asyncio.sleep(3)  # Wait for a bit after scrolling

        # Scroll down to load more content
        last_height = await page.evaluate("() => document.body.scrollHeight")
        while True:
            await page.evaluate("window.scrollBy(0, 800);")
            await asyncio.sleep(3)  # Random sleep to simulate human interaction
            new_height = await page.evaluate("() => document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Extract trending topics
        trending_topics = []
        trending_topics_elements = await page.xpath('//*[@data-testid="cellInnerDiv"]')
        print(f"Found {len(trending_topics_elements)} trending topics elements.")

        for element in trending_topics_elements:
            try:
                text = await (await element.getProperty("textContent")).jsonValue()
                text = text.strip()
                print("----------- : "*88)
                print("text : ", text)
                if "·" in text:
                    parts = text.split("·")
                    if len(parts) >= 2:
                        id = parts[0].strip()
                        category = "Trending"
                        trending = parts[1].strip()
                        print("-------------------1111trending : ", trending)
                        match = re.search(r"(\d[\d,.]*)", trending)
                        if match:
                            posts1 = match.group(1).replace(
                                ",", ""
                            )  # '51.3K' -> '51300'
                            print("posts : ", posts1)
                        else:
                            posts1 = "0"

                        item = {
                            "id": id,
                            "category": category,
                            "type": "Trending",
                            "trending": trending,
                            "posts": posts1,
                        }
                        trending_topics.append(item)
            except Exception as e:
                print(f"Error processing element: {str(e)}")

        print("Trending topics extracted successfully")

        if trending_topics:
            # Save trending topics data to a JSON file
            with open("trending_topics.json", "w") as json_file:
                json.dump(trending_topics, json_file, indent=4)
            print("Trending topics saved to trending_topics.json.")
        else:
            print("No valid trending topics found or extracted.")
        end_time = time.time()
        total_time = end_time - start_time  # Calculate the total time of execution
        print(f"Total execution time: {total_time:.2f} seconds")
        await browser.close()
        return {"data": trending_topics}  # Return as a dictionary

    except (NetworkError, PageError) as e:
        print(f"Error interacting with Twitter: {str(e)}")
        await browser.close()
        return await retry_exception(
            fetch_trending_hashtags, request, retry_count, str(e)
        )
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        await browser.close()
        return await retry_exception(
            fetch_trending_hashtags, request, retry_count, str(e)
        )

    
async def scrape_twitter_data_by_post_id(user_name, post_ids, request, retry_count=0):
    browser, page = await login()
    try:
        start_time = time.time()
        # Scrape each tweet page
        tweet_data = []
        for post_id in post_ids:
            twitter_url = f"https://twitter.com/{user_name}/status/{post_id}"
            await page.goto(twitter_url, waitUntil="domcontentloaded")
            await asyncio.sleep(4)  # Adjust sleep time as needed for page load

            # Scroll down 30% of the page height
            await page.evaluate("window.scrollBy(0, window.innerHeight * 0.5);")
            print("Scrolled down 30% of the page.")
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
            views_count = await page.evaluate(
                '() => document.querySelector("span.css-1jxf684").textContent'
            )

            # Append data to tweet_data list
            tweet_data.append(
                {
                    "username": user_name,
                    "tweet_content": tweet_content.strip(),
                    "image_url": image_url,
                    "reply_count": reply_count.strip(),
                    "like_count": like_count.strip(),
                    "repost_count": repost_count.strip(),
                    "bookmark_count": bookmark_count.strip(),
                    "timestamp": timestamp,
                    "views_count": views_count.strip(),
                }
            )
            print("Scraped tweet:", tweet_content.strip())
            end_time = time.time()
            total_time = end_time - start_time  # Calculate the total time of execution
            print(f"Total execution time: {total_time:.2f} seconds")
            await browser.close()
            return tweet_data

        # Save data to JSON file
        with open("twitter_data.json", "w") as json_file:
            json.dump(tweet_data, json_file, indent=4)

        print("Profile scraped and saved to twitter_data.json successfully!")

    except (NetworkError, PageError) as e:
        print(f"Error interacting with Twitter: {str(e)}")
        await browser.close()
        return await retry_exception(
            scrape_twitter_data_by_post_id, request, retry_count, str(e)
        )
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        await browser.close()
        return await retry_exception(
            scrape_twitter_data_by_post_id, request, retry_count, str(e)
        )

async def scrap_get_comments_of_tweet(user_name, post_ids, request, retry_count=0):
    import time

    browser, page = await login()
    try:
        start_time = time.time()
        tweet_data = []
        for post_id in post_ids:
            twitter_url = f"https://twitter.com/{user_name}/status/{post_id}"
            await page.goto(twitter_url, waitUntil="domcontentloaded")
            await asyncio.sleep(4)  # Adjust sleep time as needed for page load

            data = []
            while len(data) < NUMBER_OF_COMMENTS:
                await page.evaluate("window.scrollBy(0, window.innerHeight * 0.5);")
                print("Scrolled down 50% of the page.")
                await asyncio.sleep(4)

                elements = await page.xpath("//*[@role='article']")
                for element in elements:
                    comment_text = await (
                        await element.getProperty("textContent")
                    ).jsonValue()
                    if comment_text:
                        comment_text = comment_text.strip()
                        # Example regex to extract information from comment_text
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
                        time = time_match.group(0).strip() if time_match else "N/A"
                        comment = (
                            comment_text.split(time_match.group(0))[0].strip()
                            if time_match
                            else comment_text
                        )
                        likes = likes_match.group(0).strip() if likes_match else "N/A"
                        views = views_match.group(1).strip() if views_match else "N/A"

                        item = {
                            "Name": name,
                            "Username": username,
                            "Time": time,
                            "Comment": comment,
                            "Likes": likes,
                            "Views": views,
                        }
                        data.append(item)

                # Save formatted comments to JSON file after each batch of scraping
                with open("twitter_comments.json", "w") as json_file:
                    json.dump({"comments": data}, json_file, indent=4)

            # Return the formatted data after all post_ids are processed
            await browser.close()
            return data

    except (NetworkError, PageError) as e:
        print(f"Error interacting with Twitter: {str(e)}")
        await browser.close()
        return await retry_exception(
            scrap_get_comments_of_tweet, request, retry_count, str(e)
        )
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        await browser.close()
        return await retry_exception(
            scrap_get_comments_of_tweet, request, retry_count, str(e)
        )
