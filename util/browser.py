from playwright.async_api import async_playwright

async def get_browser():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=False,
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-infobars',
            '--remote-debugging-port=9222'
        ]
    )
    return browser, playwright

async def launch_browser(playwright, headless=False):
    return await playwright.chromium.launch(
        headless=headless,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-infobars",
        ],
    )
