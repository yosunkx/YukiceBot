import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import wordninja


async def scrape_wikipedia(url):
    print("Scraping:", url)
    async with httpx.AsyncClient(timeout=10.0) as client:  # Increase timeout to 10 seconds
        response = await client.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get domain from the URL
    domain_parts = urlparse(url).netloc.split('.')
    if len(domain_parts) > 1:
        domain_str = domain_parts[-2]
    else:
        domain_str = domain_parts[0]

    domain = ' '.join(wordninja.split(domain_str))

    title = soup.find('h1', class_='firstHeading').text
    # Prepend domain to the title
    title = f"{domain}: {title}"

    body_content = soup.find('div', id='bodyContent')

    data = []

    current_section = 'None'
    for element in body_content.find_all(['p', 'h2', 'h3']):
        if element.name == 'p':
            text = element.text.strip()
            if len(text.split()) > 5:
                data.append({
                    'title': title,
                    'section': current_section,
                    'text': text
                })
        else:
            # It's an 'h2' or 'h3', so update the current section name
            current_section = element.text.strip()
            current_section = current_section.replace("[edit]", "")

    # returns [{'title': 'your_title', 'section': 'your_section', 'text': 'your_text'},{...}, ...]
    return data
