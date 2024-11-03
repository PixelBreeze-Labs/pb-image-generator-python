import os
import re
import requests
from PIL import Image
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import imageio.v3 as iio
import numpy as np
from PIL import Image
import pillow_avif
# import re

headers = {
    "authority":"www.hindustantimes.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-IN,en;q=0.9,gu-IN;q=0.8,gu;q=0.7,en-GB;q=0.6,en-US;q=0.5",
    "cache-control": "max-age=0",
    "sec-ch-ua": "\"Chromium\";v=\"118\", \"Google Chrome\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.118 Safari/537.36"

}
def extract_filename(url):
    pattern = r'/([\w-]+)-\d+x\d+\.avif$'
    match = re.search(pattern, url)
    if match:
        return match.group(1)  # Return the captured group
    else:
        return None
    
def download_avif_to_temp(url):
    try:
        # Extract filename from the URL
        pattern = r'/([\w-]+)-\d+x\d+\.avif$'
        match = re.search(pattern, url)
        
        if match:
            filename = match.group(1)  # Get the extracted filename
        else:
            raise ValueError("Filename could not be extracted from the URL.")
        os.makedirs('/var/www/html/api.pixelbreeze.xyz/temp', exist_ok=True)
        temp_file_path = os.path.abspath(os.path.join('/var/www/html/api.pixelbreeze.xyz/temp', f"{filename}.avif"))
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError("Could not retrieve the image. Check the URL.")
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(response.content)
        print(f"Downloaded to: {temp_file_path}")
        return temp_file_path 
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def is_url(url):
    # Regex to check if the string is a valid URL
    return re.match(r'^https?://', url) is not None

def is_local_path(path):
    # Check if the path exists and is a local path
    return os.path.exists(path)

def convert_into_the_png(convert_image ,file_name):    
    png_save = os.path.abspath(os.path.join('/var/www/html/api.pixelbreeze.xyz/temp', f"{file_name}.jpg"))
    print('png_save:', png_save)
    img = Image.open(convert_image)
    img.save(png_save)
    os.remove(convert_image)
    return png_save

def scrape_artical(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url, headers=headers)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Get the title of the website
            raw_title = soup.title.text.strip()

            if ' - iconstyle' in raw_title:
                index = raw_title.index(' - iconstyle')
            if ' - Gazeta Reforma' in raw_title:
                index = raw_title.index(' - Gazeta Reforma')
            x = slice(0, index)
            title = raw_title[x]
            
            # Try to find the og:image meta tag
            og_image_tag = soup.find('meta', {'property': 'og:image'})
            
            if og_image_tag and 'content' in og_image_tag.attrs:
                img_url = urljoin(url, og_image_tag['content'])
                return title, img_url
            # If og:image is not found, check for the image in the featured div
            featured_div = soup.find('div', class_='jeg_featured featured_image')
            if featured_div:
                img_tag = featured_div.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    avi_img_url = img_tag['src']
                    download_image_url = download_avif_to_temp(avi_img_url)
                    print(download_image_url)
                    if download_image_url:
                        print('downloaded_file URL from featured div:', download_image_url)
                        convet_image_path = convert_into_the_png(download_image_url,extract_filename(avi_img_url))
                        print('convet_image_path URL from featured div:', convet_image_path)

                    return title, convet_image_path
            print('Image not found.')
            return title, None

        else:
            return "Failed to retrieve the website content.", None
    
    except Exception as e:
            return "Failed to retrieve the website content.", None
