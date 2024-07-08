import json
import os
import random
import asyncio
from typing import Dict, Optional
from django.conf import settings
from django.http import JsonResponse
import time
from django.utils import timezone
from .webdriver import InitializePuppeteer
from .email import get_mailinator_code
from django.core.cache import cache
from rest_framework import status
HEADLESS = False
init_puppeteers = InitializePuppeteer()
USER_CREDENTIALS = [
    {
        "full name": "Melvin Barber",
        "username": "MelvinBarb10693",
        "email": "zavow@mailinator.com",
        "password": "EF7T6TJwZnE9fakzJLiRfRFDNJuL",
    },
    {
        "full name": "Mariam Park",
        "username": "MariamPark98427",
        "email": "gipo@mailinator.com",
        "password": "asdf123@",
    },
    {
        "full name": "demetria63800",
        "username": "demetria63800",
        "email": "pifoga@mailinator.com",
        "password": "3TVNhFa2wJfhYq0",
    },
    {
        "full name": "JoelClay287888",
        "username": "JoelClay287888",
        "email": "gery@mailinator.com",
        "password": "asdf123@",
    },
    {
        "full name": "knight_may39057",
        "username": "knight_may39057",
        "email": "paro@mailinator.com",
        "password": "asdf123@",
    },
    {
        "full name": "ShaeleighT54515",
        "username": "ShaeleighT54515",
        "email": "kazoruzog@mailinator.com",
        "password": "asdf123@",
    },
    {
        "full name": "rocha_domi30885",
        "username": "rocha_domi30885",
        "email": "xawi@mailinator.com",
        "password": "asdf123@",
    },
    {
        "full name": "jemima_rui69057",
        "username": "jemima_rui69057",
        "email": "noxy@mailinator.com",
        "password": "asdf123@",
    },
    {
        "full name": "ChristianF88294",
        "username": "ChristianF88294",
        "email": "nutihidyf@mailinator.com",
        "password": "asdf123@",
    },
    {
        "full name": "ConstanceF3888",
        "username": "ConstanceF3888",
        "email": "dasavoxoga@mailinator.com",
        "password": "asdf123@",
    },
    {
        "full name": "WeissJorde72850",
        "username": "WeissJorde72850",
        "email": "racibezasa@mailinator.com",
        "password": "asdf123@",
    },
]




async def login():
    """
    Logs into Twitter using a randomly selected set of credentials.

    Returns:
        tuple: A tuple containing the browser and page objects for further use.
    """
    start_time = time.time()
    credentials = random.choice(USER_CREDENTIALS)
    username_value = credentials["username"]
    password_value = credentials["password"]
    email = credentials["email"]
    browser, page = await (init_puppeteers.initialize_paid_proxy() if settings.PAIDPROXY else init_puppeteers.initialize_free_proxy()) 
    # executable_path = find_chrome_executable()
    # browser = await launch(
    #     headless=HEADLESS,
    #     executablePath=executable_path,
    #     defaultViewport=None,
    #     args=["--start-maximized"],
    # )
    # page = await browser.newPage()

    try:
        await page.goto(
            "https://twitter.com/i/flow/login", waitUntil="domcontentloaded"
        )
        await asyncio.sleep(4)

        # Enter username and proceed
        await page.click('input[name="text"]')
        await page.type('input[name="text"]', username_value)
        await page.waitForXPath("//span[contains(text(),'Next')]")
        next_button = await page.xpath("//span[contains(text(),'Next')]")
        await next_button[0].click()
        print("Next Clicked Successfully")
        await asyncio.sleep(5)

        # Handle email popup if present
        try:
            print("---------")
            # await page.waitForXPath('//input[@data-testid="ocfEnterTextTextInput"]')
            email_popup = await page.xpath(
                '//input[@data-testid="ocfEnterTextTextInput"]'
            )
            await email_popup[0].click()
            await email_popup[0].type(email)
            await page.waitForXPath("//span[contains(text(),'Next')]")
            next_button = await page.xpath("//span[contains(text(),'Next')]")
            await next_button[0].click()
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Email popup handling failed: {str(e)}")

        # Enter password
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        await page.waitForXPath("//input[@name='password']")
        password_input = await page.xpath("//input[@name='password']")
        await password_input[0].type(password_value)
        print("Password filled Successfully")

        # Click login button
        await page.waitForXPath("//span[contains(text(),'Log in')]")
        log_in_button = await page.xpath("//span[contains(text(),'Log in')]")
        await log_in_button[0].click()
        print("Log in clicked Successfully")
        await asyncio.sleep(4)

        # Handle verification code if prompted
        try:
            code_input_box = await page.waitForSelector(
                'input[inputmode="text"]', timeout=10000
            )
            print("Code input box found for authentication")
            code = await get_mailinator_code(browser, page, email)  # Fetch verification code
            await code_input_box.type(code)  # Enter the verification code
            await asyncio.sleep(2)
            print("Confirmation code written")

            await page.click("div.css-175oi2r.r-b9tw7p button")
            await asyncio.sleep(5)

        except Exception as e:
            print(f"Verification code handling failed: {str(e)}")

    except Exception as e:
        print(f"An error occurred during login process: {str(e)}")

    finally:
        login_process_time = time.time() - start_time
        print(f"Login execution time: {login_process_time:.2f} seconds")
        return browser, page


def set_cache(key, value, timeout=None):
    """
    Set a value in the cache.
    :param timeout:
    :param key: Cache key
    :param value: Value to cache    :param timeout:  timeout in seconds. Defaults to the default timeout if None.
    """
    print(
        "Setting the key = ",
        key,
        " and value = ",
        value,
        " for timeout = ",
        timeout,
        " in Redis cache.",
    )
    cache.set(key, value, timeout)


def get_cache(key, default=None):
    return cache.get(key, default)




def message_json_response( code: int, error_type: str, error_message: str, data: Optional[Dict] = None,total_time = None) -> JsonResponse:
    """
    Create a JSON response with the provided code, error type, error message, and optional data.
    Parameters:
    - code (int): The HTTP status code to be returned.
    - error_type (str): The type of error.
    - error_message (str): The error message.
    - data (dict, optional): Additional data to include in the response.
    Returns:
    - JsonResponse: A JSON response containing the provided data and status code.
    """
    response_data = {
        "code": code,
        "type": error_type,
        "message": error_message,
    }
    if data:
        response_data["data"] = data

    return JsonResponse(response_data, status=code, json_dumps_params=dict(indent=2))


def save_data_in_directory(folder_name, file_name, json_data: dict):
    """
    Saves JSON data in a specified directory with the provided file name.
    If the specified directory does not exist, it creates the directory.
    Parameters:
    - folder_name (str): The name of the directory where the data will be saved.
    - file_name (str): The name of the file to be created (without the extension).
    - json_data (dict): The JSON data to be saved.
    Returns:
    - None
    Example:
    json_data = {"key": "value"}
    save_data_in_directory("my_folder", "my_file", json_data)
    This will create a file named "my_file.json" inside the "my_folder" directory and save the JSON data in it.
    """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    file_path = os.path.join(folder_name, f"{file_name}.json")
    print(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    return True

def save_data_and_return(data, data_append):
    save_data_in_directory(f"json_Response/{timezone.now().date()}/", data_append, data)
    return message_json_response(
        status.HTTP_200_OK, "success", "Tweets retrieved successfully", data=data
    )