from flask import Blueprint,request, render_template, jsonify
# import requests
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import json
import time
from bs4 import BeautifulSoup 

main = Blueprint('main', __name__)
    
# Route for the homepage
@main.route('/')
def index():
    return render_template('indexe.html')

def scrape_post_with_selenium(url):
    # Setup Selenium WebDriver with Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run headless for performance
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
#     service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service)


    service = Service('/usr/bin/chromedriver')  # Update with your ChromeDriver path
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Load the LinkedIn post page
    driver.get(url)
    time.sleep(5)  # Adjust time as needed to let the page fully load

    # Get the page source (fully rendered HTML)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
#     pretty_html = soup.prettify()

# # Save to an HTML file
#     with open('output.html', 'w', encoding='utf-8') as file:
#      file.write(pretty_html)

    # print("HTML has been saved to output.html")

    # Extract title
    title = "Title not found"
    title_tag = soup.find('h1')
    if title_tag:
        title = title_tag.get_text(strip=True)

    # Extract post content
    content = "Content not found"
    content_tag = soup.find('p', class_="attributed-text-segment-list__content")
    if content_tag:
        content = content_tag.get_text(separator=' ', strip=True)

    # Extract video details
    video_url = None
    poster_url = None
    article = soup.find('article', class_='relative pt-1.5 px-2 pb-0 bg-color-background-container container-lined main-feed-activity-card main-feed-activity-card-with-comments')

# Find the video tag within that article
    video = article.find('video')

# Extract the data-sources attribute
    
    if video:
        data_sources = video.get('data-sources')

        # Replace HTML entities and parse the JSON-like structure
        data_sources = data_sources.replace('&quot;', '"')
        
        # Load the data into a Python object
        try: 
            sources = json.loads(data_sources)

            # Extract CDN URLs
            cdn_urls = [source['src'] for source in sources]
            video_url=cdn_urls[0]
            print("CDN URLs:", cdn_urls)
        except json.JSONDecodeError as e:
            print("Error parsing JSON:", e)
    else:
        print("No video tag found in the specified article.")
    # print(video_url)
    # Extract images from the feed
    images = []
    if article:
        # Find all img tags within the article
        img_tags = article.find_all('img')
        for img in img_tags:
            img_src = img.get('data-delayed-url') or img.get('src')
            if img_src:
                images.append(img_src)
    # Quit the browser
    driver.quit()

    return {
        'title': title,
        'content': content,
        'video_url': video_url,
        'poster_url': poster_url,
        'images': images
    }

@main.route('/linkedin', methods=['GET', 'POST'])
def linkedin():
    video_details = None
    if request.method == 'POST':
        url = request.form['url']
        # video_details = scrape_post(url)
        video_details = scrape_post_with_selenium(url)
    return render_template('linkedin.html', video_details=video_details)

# API route
@main.route('/api/data')
def get_data():
    sample_data = {'key': 'value'}
    return jsonify(sample_data)
 