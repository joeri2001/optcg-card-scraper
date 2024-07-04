import requests
from bs4 import BeautifulSoup
import json
import os
import re
import sys

# Toggle to enable or disable image downloading
download_images = True

# Base URLs
base_url = "https://en.onepiece-cardgame.com/cardlist/?series="
image_base_url = "https://en.onepiece-cardgame.com/images/cardlist/card/"

# List of series numbers
series_numbers = [569101, 569102, 569103, 569104, 569105, 569106, 569107, 569201, 569001, 569002, 569003, 569004, 569005, 569006, 569007, 569008, 569009, 569010, 569011, 569012, 569013, 569901, 569801]

# Function to sanitize folder names
def sanitize_folder_name(name):
    return re.sub(r'\W+', '', name)

# Create images directory if it doesn't exist
if download_images and not os.path.exists('images'):
    os.makedirs('images')

# Function to download an image and save it locally
def download_image(img_url, img_name, folder_name):
    if not download_images:
        return None
    folder_path = os.path.join('images', folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    print(f"Downloading image: {img_url}")
    response = requests.get(img_url)
    if response.status_code == 200:
        with open(f'{folder_path}/{img_name}', 'wb') as file:
            file.write(response.content)
        print(f"Saved image to: {folder_path}/{img_name}")
        return f'{folder_path}/{img_name}'
    print(f"Failed to download image: {img_url}")
    return None

# Function to print with utf-8 encoding
def print_utf8(text):
    sys.stdout.buffer.write((text + "\n").encode('utf-8'))

# Function to scrape data from a single URL
def scrape_series(series_number):
    url = f"{base_url}{series_number}"
    print_utf8(f"Scraping URL: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print_utf8(f"Failed to retrieve data for series {series_number}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    card_elements = soup.find_all('dl', class_='modalCol')

    cards = []
    for card_element in card_elements:
        card_id = card_element.get('id', 'N/A')
        
        info_col = card_element.find('div', class_='infoCol')
        if info_col:
            info_text = info_col.text.split('|')
            card_number = info_text[0].strip() if len(info_text) > 0 else 'N/A'
            card_type = info_text[1].strip() if len(info_text) > 1 else 'N/A'
            card_class = info_text[2].strip() if len(info_text) > 2 else 'N/A'
        else:
            card_number = card_type = card_class = 'N/A'
        
        card_name = card_element.find('div', class_='cardName').text.strip() if card_element.find('div', class_='cardName') else 'N/A'

        cost = card_element.find('div', class_='cost').text.replace('Cost', '').strip() if card_element.find('div', class_='cost') else 'N/A'
        
        attribute = card_element.find('div', class_='attribute')
        if attribute:
            attribute_text = attribute.find('i').text.strip() if attribute.find('i') else 'N/A'
        else:
            attribute_text = 'N/A'
        
        power = card_element.find('div', class_='power').text.replace('Power', '').strip() if card_element.find('div', class_='power') else 'N/A'
        
        counter = card_element.find('div', class_='counter').text.replace('Counter', '').strip() if card_element.find('div', class_='counter') else 'N/A'
        
        color = card_element.find('div', class_='color').text.replace('Color', '').strip() if card_element.find('div', class_='color') else 'N/A'
        
        feature = card_element.find('div', class_='feature').text.replace('Type', '').strip() if card_element.find('div', class_='feature') else 'N/A'
        
        effect = card_element.find('div', class_='text').text.replace('Effect', '').strip() if card_element.find('div', class_='text') else 'N/A'
        
        card_set = card_element.find('div', class_='getInfo').text.replace('Card Set(s)', '').strip() if card_element.find('div', class_='getInfo') else 'N/A'
        folder_name = sanitize_folder_name(card_set)

        image_url = f"{image_base_url}{card_id}.png"
        image_path = download_image(image_url, f"{card_id}.png", folder_name) if download_images else f"images/{folder_name}/{card_id}.png"

        cards.append({
            'id': card_id,
            'number': card_number,
            'type': card_type,
            'class': card_class,
            'name': card_name,
            'image_path': image_path,
            'cost': cost,
            'attribute': attribute_text,
            'power': power,
            'counter': counter,
            'color': color,
            'feature': feature,
            'effect': effect,
            'card_set': card_set
        })
        
        print_utf8(f"Scraped card: {card_name} (ID: {card_id}, Number: {card_number})")

    return cards

# Scrape data from all series
all_cards = []
for series_number in series_numbers:
    print_utf8(f"Scraping series {series_number}")
    cards = scrape_series(series_number)
    all_cards.extend(cards)

# Save the data to a JSON file
with open('optcg_cards.json', 'w', encoding='utf-8') as jsonfile:
    json.dump(all_cards, jsonfile, ensure_ascii=False, indent=4)

print_utf8("Scraping completed and data saved to optcg_cards.json")
