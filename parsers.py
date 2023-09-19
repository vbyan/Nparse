from urllib.parse import urljoin
from functools import partial
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from core import BaseParser

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from datetime import datetime, timedelta
from helpers import ARM_MONTHS
import re

std_parse = partial(parse, dayfirst=True)


class NewsAm(BaseParser):

    def __init__(self, regions=None, categories=None, start_date=None, end_date=None):
        super().__init__(DOMAIN="https://news.am/arm/news/",
                         CATEGORIES=('politics', 'economics', 'analytics', 'society', 'innovations', 'incidents',
                                     'culture', 'carworld'),
                         PARSER_TYPE='dates',
                         REGIONS=('allregions', 'world', 'armenia', 'arcakh', 'diaspora', 'azerbaijan',
                                  'georgia', 'russia', 'turkey', 'iran', 'middleeast'),
                         regions=regions,
                         categories=categories,
                         start_date=start_date,
                         end_date=end_date
                         )

    def _get_start_urls(self):
        groups = [region + '/' + category for region in self._regions for category in self._categories]
        groups = list(map(self._add_main_domain, groups))

        start_urls = {group[len(self.DOMAIN):]: {k: None for k in self._get_dates()} for group in groups}

        return start_urls


    @staticmethod
    def _get_url_links(url, progress, task):

        response = requests.get(url)

        urls = set()
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all anchor (a) tags in the HTML
            articles = soup.find('div', class_='articles-list casual')
            links = articles.find_all('a', class_='photo-link')

            #print(soup.prettify(response))
            # Extract and print the href attribute of each anchor tag
            for link in links:
                href = link.get('href')
                if href:
                    if href.startswith('arm/news') & href.endswith('html'):
                        # Ensure the URL is absolute or join with the base URL if it's relative
                        absolute_url = urljoin('https://news.am', href)
                        urls = urls | set([absolute_url])

            progress.update(task, advance=1)

        else:
            print("Failed to retrieve the web page. Status code:")

        return urls

    @staticmethod
    def _get_title(soup_obj):
        title = soup_obj.find('div', class_='article-title')
        if title:
            return title.getText()
        return

    @staticmethod
    def _get_body(soup_obj):
        body = soup_obj.find('span', class_='article-body')
        if body:
            return body.getText()
        return


    def _parse(self, progress, task, total, url, group, date):

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = self._get_title(soup)
        body = self._get_body(soup)

        region = group.split('/')[0]
        category = group.split('/')[1]

        progress.update(task, advance=1, description=f"[blue]Parsing... [purple][{self._iter}/{total}]")

        self._iter += 1

        return {'title': title,
                'body': body,
                'category': category,
                'region': region,
                'date': date,
                'url': url}


class MamulAm(BaseParser):
    def __init__(self, categories=None, n_pages=None):
        super().__init__(DOMAIN="https://mamul.am/am/part/",
                         CATEGORIES=('պաշտոնական', 'քաղաքականություն', 'հասարակություն', 'առողջապահություն',
                                     'տնտեսություն', 'կրթություն', 'գիտություն', 'մշակույթ', 'մանկական',
                                     'սպորտ', 'արտակարգ-դեպք', 'շոու-բիզնես', 'ֆլորա-և-ֆաունա', 'ավտոմեքենաներ',
                                     '18'),
                         PARSER_TYPE='pages',
                         categories=categories,
                         n_pages=n_pages
                         )

    def _get_start_urls(self):
        groups = list(map(self._add_main_domain, self._categories))

        start_urls = {group[len(self.DOMAIN):]: {f'p{i}': None for i in range(1, self._n_pages + 1)}
                      for group in groups}

        return start_urls

    @staticmethod
    def _get_url_links(url, progress=None, task=None):

        pattern = r"\d{6}"

        # Send an HTTP GET request to the URL
        response = requests.get(url)
        urls = set()
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all anchor (a) tags in the HTML
            articles = soup.find_all('div', class_='titler2')
            links = [article.find('a') for article in articles]

            # Extract and print the href attribute of each anchor tag
            for link in links:
                href = link.get('href')
                if href:
                    if re.match(pattern, href[-6:]):
                        urls = urls | set([href])
            progress.update(task, advance=1)

        else:
            print("Failed to retrieve the web page.")

        return urls

    @staticmethod
    def _get_title(soup_obj):
        title = soup_obj.find('h2')
        if title:
            return title.getText()
        return

    @staticmethod
    def _get_body(soup_obj):
        body = soup_obj.find('p')
        if body:
            return body.getText()
        return

    @staticmethod
    def _get_date(soup_obj):
        def _parse_date():
            date_list = date.getText().split(', ')
            day = date_list[2][:2]
            month = ARM_MONTHS[date_list[2][3:]]
            year = date_list[3][:4]

            return f'{day}/{month}/{year}'

        date = soup_obj.find('div', class_='dater2')
        if date:
            return _parse_date()

    def _parse(self, progress, task, total, url, category, *args, **kwargs):

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        soup = soup.find('div', class_='cont')

        title = self._get_title(soup)
        body = self._get_body(soup)
        date = self._get_date(soup)

        progress.update(task, advance=1, description=f"[blue]Parsing... [purple][{self._iter}/{total}]")

        self._iter += 1

        return {'title': title,
                'body': body,
                'category': category,
                'date': date,
                'url': url}


class TertAm(BaseParser):
    DOMAIN = "https://tert.am/am/news/"

    CATEGORIES = ['politics', 'law', 'business', 'Sports', 'press-digest',
                  'event', 'culture']

    def __init__(self, categories=None, n_pages=None):
        if not categories:
            categories = ['politics', 'law', 'business']

        if not n_pages:
            n_pages = 3

        self.categories = categories
        self.n_pages = n_pages

    def _add_main_domain(self, x):
        return self.DOMAIN + x

    def _get_start_urls(self):
        groups = list(map(self._add_main_domain, self.categories))

        start_urls = {group[len(self.DOMAIN):]: {f'{i}': None for i in range(1, self.n_pages + 1)}
                      for group in groups}

        return start_urls

    @staticmethod
    def _get_url_links(url, progress=None, task=None):
        pattern = r"\d{7}"

        # Send an HTTP GET request to the URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; V2105 Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/108.0.5359.128 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/396.1.0.28.104;]'}
        response = requests.get(url, headers=headers)
        urls = set()
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all anchor (a) tags in the HTML
            articles = soup.find('div', class_='inner-content clear-fix')
            links = articles.find_all('a')

            # Extract and print the href attribute of each anchor tag
            for link in links:
                href = link.get('href')
                if href:
                    if re.match(pattern, href[-7:]):
                        absolute_url = urljoin('https://tert.am', href)
                        urls = urls | set([absolute_url])
            progress.update(task, advance=1)

        else:
            print("Failed to retrieve the web page. Status code:", response.status_code)

        return urls

    @staticmethod
    def _get_title(soup_obj):
        title = soup_obj.find('h1')
        if title:
            return title.getText()
        return

    @staticmethod
    def _get_body(soup_obj):
        body = soup_obj.find('div', id='news-content-container')
        if body:
            return body.getText()
        return

    @staticmethod
    def _get_date(soup_obj):
        def _parse_date():
            parsed_date = date.getText().split('•')[1]

            return parsed_date.replace('.', '/')

        date = soup_obj.find('div', class_='inner-content__article-date fb fs12')
        if date:
            return _parse_date()

    def _parse(self, progress, task, total, url, category, *args, **kwargs):

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        soup = soup.find('div', class_='inner-content clear-fix')
        title = self._get_title(soup)
        body = self._get_body(soup)
        date = self._get_date(soup)

        progress.update(task, advance=1, description=f"[blue]Parsing... [purple][{self._iter}/{total}]")

        self._iter += 1

        return {'title': title,
                'body': body,
                'category': category,
                'date': date,
                'url': url}
