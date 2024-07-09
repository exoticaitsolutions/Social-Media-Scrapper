import os
import platform
import random
import shutil
from django.conf import settings
from fake_useragent import UserAgent

from pyppeteer import launch

HEADLESS = True


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


class InitializePuppeteer:
    @staticmethod
    async def initialize_paid_proxy():  # <-- Added 'self' as the first argument
        print('Paid Proxy is Working')
        executable_path = find_chrome_executable()
        print(f"Using Chrome executable: {executable_path}")
        user_agent = UserAgent().random
        print(f"Using user agent: {user_agent}")
        width = random.randint(800, 1920)
        height = random.randint(600, 1080)
        print(f"Using random window size: {width}x{height}")
        proxy_host = settings.PROXY_HOST
        proxy_port = settings.PROXY_PORT
        proxy_username = settings.PROXY_USERNAME
        proxy_password = settings.PROXY_PASSWORD
        proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
        browser = await launch(
            headless=HEADLESS,
            executablePath=executable_path,
            defaultViewport=None,
            args=[
                '--no-sandbox',
                f'--window-size={width},{height}',
                f'--user-agent={user_agent}'
                f'--proxy-server={proxy_url}'
                "--start-maximized"
            ]
        )
        page = await browser.newPage()
        return browser, page

    @staticmethod
    async def initialize_free_proxy():  # <-- Added 'self' as the first argument
        print('Free Proxy is Working')
        executable_path = find_chrome_executable()
        print(f"Using Chrome executable: {executable_path}")
        user_agent = UserAgent().random
        print(f"Using user agent: {user_agent}")
        width = random.randint(800, 1920)
        height = random.randint(600, 1080)
        print(f"Using random window size: {width}x{height}")
        browser = await launch(
            headless=HEADLESS,

            executablePath=executable_path,
            defaultViewport=None,
            args=[
                '--no-sandbox',
                f'--window-size={width},{height}',
                f'--user-agent={user_agent}'
                "--start-maximized"
            ]
        )

        page = await browser.newPage()
        return browser, page
