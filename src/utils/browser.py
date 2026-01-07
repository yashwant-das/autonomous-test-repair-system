from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def extract_domain(url):
    """Extracts a clean domain name from a URL."""
    from urllib.parse import urlparse
    try:
        netloc = urlparse(url).netloc
        domain = netloc.replace("www.", "").split(".")[0]
        return domain if domain else "test"
    except:
        return "test"


def fetch_page_context(url, max_chars=30000):
    """
    Scrapes a page and returns a cleaned prettified HTML body.
    
    Args:
        url: Validated URL string
        max_chars: Maximum characters to return (default: 30000)
        
    Returns:
        Cleaned HTML body as string, or error message
    """
    print(f"Visiting {url}...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            try:
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
            except Exception as e:
                browser.close()
                return f"Error: Failed to load page - {str(e)}"

            try:
                content = page.content()
            except Exception as e:
                browser.close()
                return f"Error: Failed to get page content - {str(e)}"

            browser.close()

            try:
                soup = BeautifulSoup(content, 'html.parser')
                # Remove junk to save tokens
                for script in soup(["script", "style", "svg", "path", "meta", "link", "noscript"]):
                    script.decompose()

                if soup.body:
                    clean_text = soup.body.prettify()[:max_chars]
                    return clean_text
                else:
                    return "Error: Empty page body found."
            except Exception as e:
                return f"Error: Failed to parse HTML - {str(e)}"

    except Exception as e:
        return f"Error scanning page: {str(e)}"
