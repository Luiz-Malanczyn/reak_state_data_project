from playwright.sync_api import sync_playwright

def get_browser():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=False,
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-infobars',
            '--remote-debugging-port=9222'
        ]
    )
    return browser, playwright
