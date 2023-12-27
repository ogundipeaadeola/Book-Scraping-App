import requests
import csv
from bs4 import BeautifulSoup4
import os

def scrape_books_in_category(url):
    base_url = 'https://books.toscrape.com/'
    current_url = url

    while current_url:
        print(f"Scraping: {current_url}")
        response = requests.get(current_url)

        if response.status_code == 200:
            soup = BeautifulSoup4(response.content, 'html.parser')
            book_list = soup.find_all('article', class_='product_pod')

            for book in book_list:
                relative_url = book.h3.a['href']
                book_link_parts = relative_url.split('/')
                if 'catalogue' not in book_link_parts:
                    book_link = base_url + 'catalogue/' + relative_url.lstrip('../')
                else:
                    book_link = base_url + relative_url.lstrip('../')

                extract_book_details(book_link)

            next_page = soup.find('li', class_='next')
            if next_page:
                next_page_url = next_page.a['href']
                if 'catalogue' not in next_page_url:
                    next_page_url = 'catalogue/' + next_page_url
                current_url = base_url + next_page_url
            else:
                break

    print("SUCCESS")


def extract_book_details(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup4(response.content, 'html.parser')

        upc = soup.find('th', string='UPC').find_next('td').get_text(strip=True)
        book_title = soup.find('h1').text.strip()
        price_incl_tax = soup.find('th', string='Price (incl. tax)').find_next('td').get_text(strip=True)
        price_excl_tax = soup.find('th', string='Price (excl. tax)').find_next('td').get_text(strip=True)
        quantity_available = soup.find('p', class_='instock availability').text.strip()
        product_description = soup.find('meta', attrs={'name': 'description'})['content']
        category = soup.find('ul', class_='breadcrumb').find_all('li')[-2].text.strip()
        review_rating = soup.find('p', class_='star-rating')['class'][1]
        image_url = 'https://books.toscrape.com/' + soup.find('div', class_='item active').img['src'].replace('../', '')

        base_output_folder = 'Book Scraping Results'

        category_image_folder = os.path.join(base_output_folder, 'book images', category)
        if not os.path.exists(category_image_folder):
            os.makedirs(category_image_folder)

        image_name = f"{book_title}.jpg"
        image_path = os.path.join(category_image_folder, image_name)
        download_image(image_url, image_path)
        
    csv_file_path = os.path.join(base_output_folder, f"{category}.csv")
    write_book_details_to_csv(csv_file_path, {
            'product_page_url': url,
            'universal_product_code': upc,
            'book_title': book_title,
            'price_including_tax': price_incl_tax,
            'price_excluding_tax': price_excl_tax,
            'quantity_available': quantity_available,
            'product_description': product_description,
            'category': category,
            'review_rating': review_rating,
            'image_url': image_url,
            'image_filename': image_name 
        })


def download_image(url, filepath):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to download image from {url}")

def write_book_details_to_csv(filename, details):
    fieldnames = ['product_page_url', 'universal_product_code', 'book_title',
                  'price_including_tax', 'price_excluding_tax', 'quantity_available',
                  'product_description', 'category', 'review_rating', 'image_url', 'image_filename']
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow(details)

base_output_folder = 'Book Scraping Results'
if not os.path.exists(base_output_folder):
    os.makedirs(base_output_folder)

category_url = "https://books.toscrape.com"
scrape_books_in_category(category_url)
