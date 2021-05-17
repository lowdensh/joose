from   bs4 import BeautifulSoup
import csv
import datetime
import logging
import os
import re
import requests
from   requests.exceptions import HTTPError

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Scrape supplier websites for product information and save as CSV.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = logging.getLogger('scrape')

        # Dictionary of supported suppliers.
        # Value: URL for all products, initial starting point.
        self.SUPPLIER_START_URL = {
            'badurl': 'nope',
            'vapeclub': 'https://www.vapeclub.co.uk/e-liquids/',
        }

        # Is automatically set after a CSV is successfully created.
        self.csv_path = None

        self.CSV_DIR_NAME = 'scrapes'
        self.CSV_ROOT = settings.MEDIA_ROOT / self.CSV_DIR_NAME
        self.CSV_MULTIVAL_SEP = '/'
        self.CSV_HEADERS = [
            'name',
            'brand',
            'flavours',
            'volumes',
            'vg',
            'strengths',
            'is_shortfill',
            'is_salt_nic',
            'purchase_url',
            'image_url',
            'price',
            'rating',
            'num_ratings',
        ]

        # Skip attempting to scrape a product if specific strings are found.
        self.SKIP_CRITERIA = {
            'product_url_part': [
                'nicotine-shots',
                'vape-pods',
                'flavour-concentrates-diy',
                'vaping-accessories',
                'vape-kits',
            ],
            'product_title': [
                'shot',
                'disposable',
                'pod',
                'concentrate',
                'cbd',
            ],
            'strengths_list': [
                'shortfill',
                'nic-shot included',
                'nic-shots included',
            ]
        }

        # Remove specific strings from product fields if found.
        # List values are used as RegEx patterns.
        self.REMOVE_CRITERIA = {
            'raw_name': [
                'eliquid',
                'e-liquid',
                'hybrid salt',
                'nic salt',
                'shortfill',
                '\d+ml',
            ],
            'raw_brand': [
                'nic salts',
                '\d{2}\/\d{2}',  # e.g. '70/30'
                '- \d+ml',       # e.g. '- 10ml'
                '\d+ml',
                'any tank',
            ],
        }

    def add_arguments(self, parser):
        parser.add_argument('suppliers', nargs='+', type=str)

    def handle(self, *args, **kwargs):
        try:
            if not os.path.exists(self.CSV_ROOT):
                os.mkdir(self.CSV_ROOT)

        except Exception as e:
            m = f'Error when creating CSV directory: {e}'
            self.stdout.write(self.style.ERROR(m))
            self.logger.error(m)
            return
        
        for supplier in kwargs['suppliers']:
            print()
            if supplier not in self.SUPPLIER_START_URL:
                m = f'Error: no support for supplier \'{supplier}\''
                self.stdout.write(self.style.ERROR(m
                    + f'\nSupported suppliers: {list(self.SUPPLIER_START_URL)}'
                ))
                self.logger.error(m)
                continue

            start_url = self.SUPPLIER_START_URL[supplier]
            response = self.try_request(start_url)
            if response is None:
                continue

            self.start_scrape(supplier)
    
    def try_request(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()

        except HTTPError as e:
            m = f'Error: bad status code when making request: {e}'
            self.stdout.write(self.style.ERROR(m))
            self.logger.error(m)
            return None

        except Exception as e:
            m = f'Error when making request: {e}'
            self.stdout.write(self.style.ERROR(m))
            self.logger.error(m)
            return None
            
        return response
    
    def start_scrape(self, supplier):
        m = f'Scraping \'{supplier}\':'
        self.stdout.write(self.style.MIGRATE_HEADING(m))

        # TESTING: Use this explicit path and comment the 'if' block below.
        # self.csv_path = self.CSV_ROOT / 'test.csv'

        self.create_csv(supplier)
        if self.csv_path is None:
            m = f'Error: cannot write to CSV for supplier \'{supplier}\''
            self.stdout.write(self.style.ERROR(m))
            self.logger.error(m)
            return
        
        self.access_page_products_list(
            self.SUPPLIER_START_URL[supplier]
        )
    
    def create_csv(self, supplier):
        fnow = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
        csv_name = f'{fnow}--{supplier}.csv'
        csv_path = self.CSV_ROOT / csv_name

        try:
            with open(f'{csv_path}', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.CSV_HEADERS)
            self.csv_path = csv_path

        except Exception as e:
            m = f'Error when creating CSV: {e}'
            self.stdout.write(self.style.ERROR(m))
            self.logger.error(m)
    
    def csv_append_row(self, item_list):
        if len(item_list) < len(self.CSV_HEADERS):
            self.stdout.write(self.style.ERROR(
                f'Error: expected {len(self.CSV_HEADERS)} items to append '
                f'to CSV, received {len(item_list)}'
                f'\nExpected items: {list(self.CSV_HEADERS)}'
            ))
            return

        try:
            with open(f'{self.csv_path}', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(item_list)

        except Exception as e:
            m = f'Error when appending to CSV: {e}'
            self.stdout.write(self.style.ERROR(m))
            self.logger.error(m)
    
    def access_page_products_list(self, url):
        response = self.try_request(url)
        if response is None:
            return
        
        fnow = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        self.stdout.write(self.style.MIGRATE_LABEL(
            f'[{fnow}] {url}'
        ))
        base_url = 'https://www.vapeclub.co.uk'
        soup = BeautifulSoup(response.content, 'html.parser')

        products = soup.find_all(class_='productGridItem')
        if len(products) == 0:
            # The previous page was the last page of listed products.
            # Nothing more to do for this supplier.
            return
        
        # TESTING: Use these two statements and comment out the 'for' block
        # below to test scraping a single product.
        # product_url_part = products[0].find('h5').find('a').get('href')
        # self.scrape_product(f'{base_url}{product_url_part}')

        for product in products:
            visit = self.should_visit(product)
            if visit:
                product_url_part = product.find('h5').find('a').get('href')
                self.scrape_product(f'{base_url}{product_url_part}')

        next_button = soup.find('a', class_='ajaxAltNext page-link')
        if next_button is None:
            # This is the last page of listed products.
            # Nothing more to do for this supplier.
            return

        next_url_part = next_button.get('href')
        self.access_page_products_list(f'{base_url}{next_url_part}')
    
    def should_visit(self, product_soup):
        product_title = product_soup.find('h5').find('a')
        product_url_part = product_title.get('href')

        if 'e-liquids' not in str(product_url_part).lower():
            return False

        for criterion in self.SKIP_CRITERIA['product_url_part']:
            if criterion in str(product_url_part).lower():
                return False
        
        for criterion in self.SKIP_CRITERIA['product_title']:
            if criterion in str(product_title).lower():
                return False

        return True
    
    def log_cancel(self, topic, field, url):
        m = 'Scrape cancelled for product: '
        if topic == 'html':
            m += f'cannot find HTML for \'{field}\' at \t {url}'
        elif topic == 'format':
            m += f'unaccepted format for \'{field}\' at \t {url}'
        else:
            return
        self.logger.info(m)

    def scrape_product(self, url):
        # TESTING: Use a new URL here to test scraping a specific product.
        # url = ''
        response = self.try_request(url)
        if response is None:
            return
        
        self.stdout.write(f'  - {url}')
        soup = BeautifulSoup(response.content, 'html.parser')

        ############
        # SCRAPING #
        ############

        # Typical procedure:
        # - Find appropriate HTML, cancel scrape if not found
        # - Get data in required format, cancel scrape if not possible

        raw_price = soup.find('p', class_='text-price')
        if raw_price is None:
            self.log_cancel('html', 'price', url)
            return
        
        csv_price = self.clean_price(raw_price)
        if csv_price is None:
            self.log_cancel('format', 'price', url)
            return

        raw_title = soup.find('h1')
        if raw_title is None:
            self.log_cancel('html', 'title', url)
            return

        csv_name, csv_brand = self.clean_name_brand(raw_title)
        if csv_name is None or csv_brand is None:
            self.log_cancel('format', 'name/brand', url)
            return
        
        raw_flavours_dt = soup.find('dt', attrs={'title': 'Eliquid Flavours'})
        raw_flavours_sub = soup.find('span', class_='h6 text-muted')
        if raw_flavours_dt is None and raw_flavours_sub is None:
            self.log_cancel('html', 'flavours', url)
            return
        
        csv_flavours = self.clean_flavours(raw_flavours_dt, raw_flavours_sub)
        if csv_flavours is None:
            self.log_cancel('format', 'flavours', url)
            return

        raw_volumes = soup.find('div', class_='bottleSize')
        if raw_volumes is None:
            self.log_cancel('html', 'volumes', url)
            return
        
        csv_volumes, csv_short = self.clean_volumes(raw_volumes)
        if csv_volumes is None or csv_short is None:
            self.log_cancel('format', 'volumes', url)
            return

        raw_vg = soup.find('div', class_='vg')
        if raw_vg is None:
            self.log_cancel('html', 'vg', url)
            return
        
        csv_vg = self.clean_vg(raw_vg)
        if csv_vg is None:
            self.log_cancel('format', 'vg', url)
            return

        strength_levels = soup.find('div', class_='nicotineLevels')
        if strength_levels is None:
            self.log_cancel('html', 'strengths', url)
            return
        
        csv_strengths = self.clean_strengths(strength_levels)
        if csv_strengths is None:
            self.log_cancel('format', 'strengths', url)
            return

        csv_salt = self.get_salt(raw_title)

        csv_purchase_url = url

        # SupplierInfo.image_url allows the blank empty string.
        image_container = soup.find('div', class_='mainProductImage')
        if image_container is None:
            csv_image_url = ''
        else:
            csv_image_url = self.get_image_url(image_container)

        # Some products have not been rated by any users.
        review_score = soup.find('div', class_='productReviewScore')
        if review_score is None:
            csv_rating, csv_num_ratings = 0, 0
        else:
            csv_rating, csv_num_ratings = self.clean_ratings(review_score)

        ###########
        # WRITING #
        ###########

        write_list = [
            csv_name,
            csv_brand,
            csv_flavours,
            csv_volumes,
            csv_vg,
            csv_strengths,
            csv_short,
            csv_salt,
            csv_purchase_url,
            csv_image_url,
            csv_price,
            csv_rating,
            csv_num_ratings,
        ]
        self.csv_append_row(write_list)
    
    def clean_price(self, raw_price):
        text = raw_price.text.lower()
        from_idx = text.find('from')
        if from_idx != -1:
            # Page is for a collection of product variants.
            # Don't scrape from these pages.
            return None
        
        # Pattern: any amount of digits, single period, and any further digits.
        price_digits = re.search(r'\d+\.\d+', text)
        if price_digits is None:
            return None
        
        clean_price = price_digits.group(0)
        return clean_price
    
    def clean_name_brand(self, raw_title):
        by_idx = raw_title.text.lower().rfind('by')
        if by_idx == -1:
            return None, None

        raw_name = raw_title.text[:by_idx]
        raw_brand = raw_title.text[by_idx+2:]

        for criterion in self.REMOVE_CRITERIA['raw_name']:
            raw_name = re.sub(criterion, '', raw_name, flags=re.IGNORECASE)

        for criterion in self.REMOVE_CRITERIA['raw_brand']:
            raw_brand = re.sub(criterion, '', raw_brand, flags=re.IGNORECASE)

        # Remove multiple consecutive spaces.
        clean_name = ' '.join(raw_name.split())
        clean_brand = ' '.join(raw_brand.split())
        return clean_name, clean_brand
    
    def clean_flavours(self, raw_flavours_dt, raw_flavours_sub):
        if raw_flavours_sub is None:
            return None
        
        # Separate distinct flavours.
        flavours_list_dd = []
        if raw_flavours_dt is not None:
            raw_flavours_dd = raw_flavours_dt.find_next_sibling('dd')
            flavours_list_dd = re.split(',|/', raw_flavours_dd.text)
        flavours_list_sub = re.split(',|/', raw_flavours_sub.text)

        # Trim spaces and create one unique list.
        flavours_list_dd = [f.strip() for f in flavours_list_dd]
        flavours_list_sub = [f.strip() for f in flavours_list_sub]
        flavours_list = sorted(list(
            set(flavours_list_dd) | set(flavours_list_sub)
        ))

        # Create a string to store multiple flavours in one cell in the CSV.
        clean_flavours = self.CSV_MULTIVAL_SEP.join(flavours_list)
        return clean_flavours
    
    def clean_volumes(self, raw_volumes):
        if len(raw_volumes.text) == 0:
            return None, None

        volumes_list = re.split(',', raw_volumes.text)

        # Remove ml units and trim spaces.
        volumes_list = [
            re.sub('ml', '', v.strip(), flags=re.IGNORECASE)
            for v in volumes_list
        ]

        is_shortfill = False
        for v in volumes_list:
            try:
                if int(v) > 10:
                    is_shortfill = True
                    break
            except ValueError:
                # e.g. volume '50+10ml' for shortfills with nic shots.
                # Skip these products.
                return None, None

        # Create a string to store multiple volumes in one cell in the CSV.
        clean_volumes = self.CSV_MULTIVAL_SEP.join(volumes_list)
        return clean_volumes, is_shortfill
    
    def clean_vg(self, raw_vg):
        # Pattern: any amount of digits.
        vg_digits = re.search(r'\d+', str(raw_vg))
        if vg_digits is None:
            return None
        
        clean_vg = vg_digits.group(0)
        return clean_vg
    
    def clean_strengths(self, strength_levels):
        strength_spans = strength_levels.find_all('span')
        if strength_spans is None:
            return None

        strengths_list = [span.text for span in strength_spans]

        if len(strengths_list) == 1:
            val = strengths_list[0].lower()
            if 'shortfill' in val:
                # Shortfills have no nicotine.
                return '0'
            if 'shot' in val:
                # Skip nic shots.
                return None

        # Remove mg units.
        strengths_list = [
            re.sub('mg', '', s, flags=re.IGNORECASE)
            for s in strengths_list
        ]

        # Create a string to store multiple strengths in one cell in the CSV.
        clean_strengths = self.CSV_MULTIVAL_SEP.join(strengths_list)
        return clean_strengths
    
    def get_salt(self, raw_title):
        salt_idx = raw_title.text.lower().find('salt')
        if salt_idx != -1:
            return True
        return False
    
    def get_image_url(self, image_container):
        # Most images have zooming enabled on mouseover.
        # These images are displayed with <a> tags.
        a = image_container.find('a')
        if a is not None:
            href = a.get('href')
            if href is None:
                return ''
            else:
                return href
        
        # Some images are too small for zoom.
        # These are instead displayed with <img> tags.
        img = image_container.find('img')
        if img is not None:
            src = img.get('src')
            if src is None:
                return ''
            else:
                return src
        
        return ''
        
    def clean_ratings(self, review_score):
        review_stars = review_score.find('span', class_='reviewStars')
        if review_stars is None:
            return 0, 0

        raw_rating = review_stars.find('span').get('title')
        # Pattern: any amount of digits. Period and further digits are optional.
        # Ratings are either whole numbers e.g. '4' or decimals e.g. '4.5'
        rating_digits = re.search(r'\d+(\.\d+)?', raw_rating)
        if rating_digits is None:
            return 0, 0

        raw_num_ratings = review_score.find('a', href='#reviews').text
        # Pattern: any amount of digits.
        num_digits = re.search(r'\d+', raw_num_ratings)
        if num_digits is None:
            return 0, 0

        clean_rating = rating_digits.group(0)
        clean_num_ratings = num_digits.group(0)
        return clean_rating, clean_num_ratings