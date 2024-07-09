# Project Name
## Social Media Scrapping
* This project focuses on creating a comprehensive tool for scraping data from various social media platforms such as Instagram, Twitter, and Facebook using Python and Django. The tool will allow users to gather and analyze social media data efficiently.
### Overview
* The Social Media Scraping Tool is designed to extract data from multiple social media platforms. This document details the module specifically for Twitter scraping, outlining the available APIs and their functionalities.

## Module Name 
### Twitter Scrapper
* The Twitter Scraper module provides APIs to scrape data from Twitter using various approaches, such as profile names, hashtags, trending topics, and post IDs.
### APIs

***Profile Data Scraping***-
Retrieve detailed information about Twitter profiles using profile names. This API enables users to gather comprehensive data on specific Twitter profiles.

***Trending Hashtags Scraping***-
Extract the latest trending hashtags on Twitter to stay updated with current trends.

***Hashtag-based Data Scraping***-
Collect tweets and associated data by searching specific hashtags. This API enables users to gather tweets related to specific topics of interest.

***Scraping Using Post-Ids*** -
Fetch information about specific posts using their unique post IDs. This API provides detailed data on individual Twitter posts.

***Scraping Post Comments***-
Fetch comments associated with specific posts using their unique post IDs. This API allows users to collect and analyze comments on specific Twitter posts.


# Setup Instructions

## Installation

### Python Installation Process
Before proceeding, ensure Python is installed on your system. If not, you can download and install Python from [python.org](https://www.python.org/downloads/).

### Setting up a Virtual Environment
To work with Django, it's recommended to create a virtual environment. Follow the steps outlined in the [Python documentation](https://docs.python.org/3/tutorial/venv.html) or use tools like `virtualenv` or `venv`.

### Installing Django
Once the virtual environment is set up, you can install Django within it. Refer to the [Django documentation](https://docs.djangoproject.com/en/stable/intro/install/) for detailed instructions on installing Django.

## Getting Started

### Clone the Project
```bash
git clone https://github.com/exoticaitsolutions/Twitter-Scrapping
```

## Navigate to the Project Directory

```bash
  cd Twitter-Scrapping
```

# Install Dependencies
### Using requirements.txt
```
pip install -r requirements.txt
```

# Individual Dependencies

***Core Headers***
```
pip install django-cors-headers
```
***blinker***
```
pip install blinker==1.7.0
```

***Fake Useragent***
```
pip install fake-useragent
```

***python-dotenv***
```
pip install python-dotenv
```

## Environment Variables
 To run this project, you will need to add the following environment variables to your .env file
# Create .env file
in linux
```
touch .env
```
in window 
```
type nul > .env
```
## Setup .env File 
```
PAIDPROXY = FALSE
PROXY_HOST = PROXY_HOST
PROXY_PORT = PROXY_PORT
PROXY_USERNAME = PROXY_USERNAME
PROXY_PASSWORD = PROXY_PASSWORD
```

# Run Project
```bash
uvicorn social_media_scrapping.asgi:application
```

***If you encounter the following error***
ERROR: [Errno 98] error while attempting to bind on address ('127.0.0.1', 8000): address already in use

***Resolve the port conflict by terminating the process using port 8000***

```bash
kill -9 $(lsof -t -i:8000)
```
Restart the Uvicorn server:
```
uvicorn social_media_scrapping.asgi:application
```