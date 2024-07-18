import os
import platform
import random
import shutil
from django.conf import settings
from fake_useragent import UserAgent

from pyppeteer import launch

HEADLESS = True


# def find_chrome_executable():
#     """
#     Finds the path to the Google Chrome executable based on
#     the current operating system.
#     Returns:
#         str or None: Path to the Chrome executable if found,
#         or None if not found.
#     Raises:
#         None
#     Notes:
#         - On Windows, it checks common installation paths under Program Files
#         and Program Files (x86).
#         - On Linux, it checks for 'google-chrome' and 'google-chrome-stable'
#          in the system PATH.
#     """
#     system = platform.system()
#     print(f"system : {system}")
#     if system == "Windows":
#         chrome_paths = [
#             os.path.join(
#                 os.environ["ProgramFiles"],
#                 "Google",
#                 "Chrome",
#                 "Application",
#                 "chrome.exe",
#             ),
#             os.path.join(
#                 os.environ["ProgramFiles(x86)"],
#                 "Google",
#                 "Chrome",
#                 "Application",
#                 "chrome.exe",
#             ),
#         ]
#         for path in chrome_paths:
#             if os.path.exists(path):
#                 return path
#     elif system == "Linux":
#         chrome_path = shutil.which("google-chrome")
#         if chrome_path is None:
#             chrome_path = shutil.which("google-chrome-stable")
#         return chrome_path
#     return None




import os
import platform
import shutil

def find_chrome_executable():
    """
    Finds the path to the Google Chrome executable on the system.

    Returns:
        str: The path to the Chrome executable if found, otherwise None.
    """
    system = platform.system()
    print(f"System: {system}")

    # Handle Windows systems
    if system == "Windows":
        possible_paths = [
            os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Google", "Chrome", "Application", "chrome.exe"),
        ]

        # Windows 10 and 11 might have additional installation paths
        windows_specific_paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", "C:\\Users\\%USERNAME%\\AppData\\Local"), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("APPDATA", "C:\\Users\\%USERNAME%\\AppData\\Roaming"), "Google\\Chrome\\Application\\chrome.exe"),
        ]
        possible_paths.extend(windows_specific_paths)

        # Check if Chrome exists at any of these paths
        chrome_path = next((path for path in possible_paths if os.path.exists(path)), None)
        
        # Example temporary directory (adjust according to your use case)
        temp_dir = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "chrome_temp")

        # Clean up the temporary directory
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except OSError as e:
            print(f"Error: {e.strerror}")

        return chrome_path

    # Handle Linux systems (Ubuntu)
    elif system == "Linux":
        chrome_path = shutil.which("google-chrome") or shutil.which("google-chrome-stable")
        if chrome_path:
            return chrome_path

        # Additional common paths for Chrome on Ubuntu
        linux_specific_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/opt/google/chrome/google-chrome",
        ]
        return next((path for path in linux_specific_paths if os.path.exists(path)), None)

    # Return None if Chrome is not found
    return None

# Test the function
chrome_path = find_chrome_executable()
print(f"Chrome path: {chrome_path}")


class InitializePuppeteer:
    """
    A utility class to initialize Pyppeteer with different proxy configurations.

    Methods:
    - initialize_paid_proxy(): Initialize Pyppeteer with a paid proxy configuration.
    - initialize_free_proxy(): Initialize Pyppeteer with a free proxy configuration.
    """

    @staticmethod
    async def initialize_paid_proxy():
        """
        Initialize Puppeteer with a paid proxy configuration.

        Returns:
        - browser: Pyppeteer browser instance.
        - page: Pyppeteer page instance.
        """
        print("Paid Proxy is Working")
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
        proxy_url = (
            f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
        )
        browser = await launch(
            headless=HEADLESS,
            executablePath=executable_path,
            defaultViewport=None,
            args=[
                "--no-sandbox",
                f"--window-size={width},{height}",
                f"--user-agent={user_agent}"
                f"--proxy-server={proxy_url}"
                "--start-maximized",
            ],
        )
        page = await browser.newPage()
        return browser, page

    @staticmethod
    async def initialize_free_proxy():
        """
        Initialize Puppeteer with a free proxy configuration.

        Returns:
        - browser: Pyppeteer browser instance.
        - page: Pyppeteer page instance.
        """
        print("Free Proxy is Working")
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
                "--no-sandbox",
                f"--window-size={width},{height}",
                f"--user-agent={user_agent}" "--start-maximized",
            ],
        )

        page = await browser.newPage()
        return browser, page
