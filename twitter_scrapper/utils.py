import os
import platform
import random
import asyncio
import shutil
from pyppeteer import launch
import time
from .email import *

HEADLESS = False

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


def find_chrome_executable():
    """
    Finds the path to the Google Chrome executable based on
    the current operating system.
    Returns:
        str or None: Path to the Chrome executable if found,
        or None if not found.
    Raises:
        None
    Notes:
        - On Windows, it checks common installation paths under Program Files
        and Program Files (x86).
        - On Linux, it checks for 'google-chrome' and 'google-chrome-stable'
         in the system PATH.
    """
    system = platform.system()
    print(f"system : {system}")
    if system == "Windows":
        chrome_paths = [
            os.path.join(
                os.environ["ProgramFiles"],
                "Google",
                "Chrome",
                "Application",
                "chrome.exe",
            ),
            os.path.join(
                os.environ["ProgramFiles(x86)"],
                "Google",
                "Chrome",
                "Application",
                "chrome.exe",
            ),
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                return path
    elif system == "Linux":
        chrome_path = shutil.which("google-chrome")
        if chrome_path is None:
            chrome_path = shutil.which("google-chrome-stable")
        return chrome_path
    return None

async def login():
    """
    Logs into Twitter using a randomly selected set of credentials.

    This function performs the following steps:
    1. Launches a new browser instance.
    2. Navigates to the Twitter login page.
    3. Enters the username and password from a randomly selected credential set.
    4. Handles potential authentication challenges, including entering a verification code.

    Returns:
        tuple: A tuple containing the browser and page objects for further use.

    Raises:
        Exception: If an error occurs during the login process.
    """
    start_time = time.time()
    credentials = random.choice(USER_CREDENTIALS)
    username_value = credentials["username"]
    password_value = credentials["password"]
    email = credentials["email"]
    executable_path = find_chrome_executable() # Adjust path to Chrome executable
    browser = await launch(
        headless=HEADLESS,
        executablePath=executable_path,
        defaultViewport=None,
        args=["--start-maximized"],
    )
    page = await browser.newPage()

    try:
        await page.goto(
            "https://twitter.com/i/flow/login", waitUntil="domcontentloaded"
        )
        await asyncio.sleep(4)

        # Enter username
        await page.click('input[name="text"]')
        await page.type('input[name="text"]', username_value)
        await page.waitForXPath("//span[contains(text(),'Next')]")
        next_button = await page.xpath("//span[contains(text(),'Next')]")
        await next_button[0].click()
        print("Next Clicked Successfully")

        # Enter password
        await page.waitForXPath("//input[@name='password']")
        password_input = await page.xpath("//input[@name='password']")
        await password_input[0].type(password_value)
        print("Password filled Successfully")

        # Click login
        await page.waitForXPath("//span[contains(text(),'Log in')]")
        log_in_button = await page.xpath("//span[contains(text(),'Log in')]")
        await log_in_button[0].click()
        print("Log in clicked Successfully")
        await asyncio.sleep(4)
        try:
            code_input_box = await page.waitForSelector(
                'input[inputmode="text"]', timeout=10000
            )
            print("Code input box found for authentication")
            code = await get_mailinator_code(
                email
            )  # Fetch verification code from Mailinator
            await code_input_box.type(code)  # Enter the verification code
            await asyncio.sleep(2)  # Optional sleep to simulate human interaction
            print("Confirmation code written")

            await page.click("div.css-175oi2r.r-b9tw7p button")
            await asyncio.sleep(5)  # Optional sleep for navigation

        except:
            # If code input box is not found, handle the scenario where email input
            # box is displayed for authentication
            email_input_box = await page.waitForSelector(
                'input[inputmode="email"]', timeout=10000
            )
            print("Email input box found for authentication")
            await email_input_box.type(email)  # Enter the email address
            await asyncio.sleep(2)  # Optional sleep to simulate human interaction

            # Click the next button to proceed with authentication
            await page.click("div.css-175oi2r.r-b9tw7p button")
            await asyncio.sleep(5)  # Optional sleep for navigation
        finally:
            # Return browser and page objects for further use if needed
            login_process_time = time.time()
            total_time = login_process_time - start_time
            print(f"Login execution time: {total_time:.2f} seconds")
            return browser, page

    except Exception as e:
        print(f"An error occurred during login process: {str(e)}")

    finally:
        # Return browser and page objects for further use if needed
        login_process_time = time.time()
        total_time = login_process_time - start_time
        print(f"Login execution time: {total_time:.2f} seconds")
        return browser, page
