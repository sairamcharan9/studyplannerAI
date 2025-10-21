from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:8000")
    page.click("#chat-bubble")
    page.fill("#chat-input", "Test message")
    page.click("#send-chat-btn")
    page.screenshot(path="jules-scratch/verification/chatbox.png")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
