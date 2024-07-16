from pyppeteer import launch
import asyncio


async def get_mailinator_code(browser, page, email):
    """
    Retrieves the verification code from Mailinator for the given email address.

    Args:
        email (str): The email address to check for the verification code.

    Returns:
        str: The verification code if found, else None.
    """
    try:
        username = email.split("@")[0]
        url = f"https://www.mailinator.com/v4/public/inboxes.jsp?to={username}"
        await page.goto(url)  # Navigate to Mailinator inbox
        await asyncio.sleep(4)  # Adjust sleep time as needed for page load
        # Click the email item
        await page.waitForXPath(
            "/html/body/div/main/div[2]/div[3]/div/div[4]/div/div/table/tbody/tr/td[3]"
        )
        email_element = await page.xpath(
            "/html/body/div/main/div[2]/div[3]/div/div[4]/div/div/table/tbody/tr/td[3]"
        )
        await email_element[0].click()
        await asyncio.sleep(2)  # Optional sleep after clicking

        # Get the element containing the code
        code_element = await page.waitForSelector(
            "div.fz-20.ff-futura-demi.gray-color.ng-binding")
        code_text = await code_element.evaluate(
            "(element) => element.textContent")

        # Extract the code
        elements = code_text.split()
        last = elements[-1]
        first = elements[0]
        code = first if first.isdigit() else last.strip()

        print(f"Code is: {code}")
        return code

    except Exception as e:
        print(
            f"An error occurred while fetching code from Mailinator: {str(e)}")
        return None

    finally:
        await browser.close()
