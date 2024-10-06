from flask import Blueprint,request, render_template, jsonify,send_file
import requests
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import json
import time
from bs4 import BeautifulSoup 
from io import BytesIO
main = Blueprint('main', __name__)
    

def scrape_post_with_selenium(url):
  try:
        # Setup Selenium WebDriver with Chrome options
        # print(url)
        if not url.startswith('https://www.linkedin.com/posts/'):
            # print("in if")
            return {'error': 'Invalid URL: The URL must start with https://www.linkedin.com/posts/'}
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run headless for performance
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        service = Service('/usr/bin/chromedriver')  # Update with your ChromeDriver path
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Load the LinkedIn post page
        driver.get(url)
        time.sleep(5)  # Adjust time as needed to let the page fully load

        # Get the page source and parse it with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Extract post title
        title = "Title not found"
        try:
            title_tag = soup.find('h1')
            if title_tag:
                title = title_tag.get_text(strip=True)
        except Exception as e:
            return {'error': f"Error extracting title: {e}"}

        # Extract post content
        content = "Content not found"
        try:
            content_tag = soup.find('p', class_="attributed-text-segment-list__content")
            if content_tag:
                content = content_tag.get_text(separator=' ', strip=True)
        except Exception as e:
            return {'error': f"Error extracting content: {e}"}

        # Extract video details
        video_url = None
        poster_url = None
        try:
            article = soup.find('article', class_='relative pt-1.5 px-2 pb-0 bg-color-background-container container-lined main-feed-activity-card main-feed-activity-card-with-comments')

            # Find the video tag within the article
            if article:
                video = article.find('video')

                if video:
                    data_sources = video.get('data-sources')

                    # Replace HTML entities and parse the JSON-like structure
                    if data_sources:
                        data_sources = data_sources.replace('&quot;', '"')
                        sources = json.loads(data_sources)

                        # Extract CDN URLs
                        cdn_urls = [source['src'] for source in sources]
                        video_url = cdn_urls[0] if cdn_urls else None
                    else:
                        return {
                                'title': None,
                                'content': None,
                                'video_url': None,
                                'poster_url': None,
                                'images': None,
                                'success':None,                
                                'error': "No data-sources attribute in video tag"}
                else:
                    return {
                        'title': None,
                                'content': None,
                                'video_url': None,
                                'poster_url': None,
                                'images': None,
                                'success':None,
                        'error': "No video tag found in the specified article"}
            else:
                return {
                    'title': None,
                                'content': None,
                                'video_url': None,
                                'poster_url': None,
                                'images': None,
                                'success':None,
                    'error': "No article found in the page"}
        except json.JSONDecodeError as e:
            return {
                'title': None,
                                'content': None,
                                'video_url': None,
                                'poster_url': None,
                                'images': None,
                                'success':None,
                'error': f"Error parsing video data JSON: {e}"}
        except Exception as e:
            return {
                'title': None,
                                'content': None,
                                'video_url': None,
                                'poster_url': None,
                                'images': None,
                                'success':None,
                'error': f"Error extracting video details: {e}"}

        # Extract images from the feed
        # images = []
        # try:
        #     if article:
        #         # Find all img tags within the article
        #         img_tags = article.find_all('img')
        #         for img in img_tags:
        #             img_src = img.get('data-delayed-url') or img.get('src')
        #             if img_src:
        #                 images.append(img_src)
        # except Exception as e:
        #     return {'error': f"Error extracting images: {e}"}
        
        # Quit the browser
        driver.quit()

        # Return the extracted data
        return {
            'video_url': video_url,
            'poster_url': poster_url,
            'success':"video downloaded successfully",
            'error':None
        }

  except Exception as e:
    # Return error if any part of the process fails
    return {'error': str(e)}
  
def download_video(response):
    print("in download func")
    return send_file(response, as_attachment=True, download_name='video.mp4', mimetype='video/mp4')
# def download_video(response):
                    # print(response.content)
                    # response.headers["Content-Disposition"] = "attachment; filename=video.mp4"
                    # return send_file(response.content,
                    #                 as_attachment=True,
                    #                 download_name='video.mp4',
                    #                 mimetype='video/mp4')
                    # with open('temp_video.mp4', 'wb') as f:
                    #     f.write(response.content)
                    # return send_file('temp_video.mp4', as_attachment=True, download_name='video.mp4', mimetype='video/mp4')
                    

@main.route('/', methods=['GET', 'POST'])
def linkedin():
    video_details = None
    url=None
    if request.method == 'POST':
        url = request.form['url']
        # video_details = scrape_post(url)
        video_details = scrape_post_with_selenium(url)
        if(not video_details['error']):
            print(video_details)
            video_url =video_details['video_url']   # Replace with the actual video URL
            response = requests.get(video_url)
            if response.status_code == 200:
                return send_file(BytesIO(response.content), as_attachment=True, download_name='video.mp4', mimetype='video/mp4')
                # download_video(BytesIO(response.content))
                # return render_template('linkedin.html', video_details=video_details)
            else:
                return render_template('linkedin.html', video_details=video_details)
        else:
            return render_template('linkedin.html', video_details=video_details)            
    return render_template('linkedin.html', video_details=video_details)
 