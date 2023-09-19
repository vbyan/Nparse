
from abc import ABC, abstractmethod
from os import path

from copy import deepcopy
from rich.progress import Progress

import pickle
from functools import partial
from googletrans import Translator
from dateutil.parser import parse
from datetime import datetime, timedelta
import validators


translator = Translator()
std_parse = partial(parse, dayfirst=True)

class BaseParser(ABC):

    def __init__(self, DOMAIN=None, REGIONS=None, CATEGORIES=None, PARSER_TYPE=None,
                 regions=None, categories=None, n_pages=None, start_date=None,
                 end_date=None, **kwargs):

        self.DOMAIN = self._check_null(DOMAIN, "DOMAIN")
        self.REGIONS = REGIONS
        self.CATEGORIES = self._check_null(CATEGORIES, "CATEGORIES")

        self._regions = regions
        self._categories = self._check_null(categories, "categories")
        self._n_pages = n_pages
        self._start_date = start_date
        self._end_date = end_date

        self._parser_type = self._check_null(PARSER_TYPE, "parser_type")

        for k,v in kwargs.items():
            if k.upper() == k:
                setattr(self, k, self._check_null(v, k))
            else:
                setattr(self, f'_{k}', self._check_null(v, k))

        self._n_pages = self._check_n_pages()
        self._parser_type = self._get_parser_type()

    def _get_parser_type(self):
        if self._start_date:
            return "dates"
        return "pages"

    @staticmethod
    def _check_urls(url, candidates):
        results = {candidate: validators.url(url.replace() for candidate in candidates)}
        return validators.url(url)
    def _get_start_urls(self):
        groups= self._categories
        if self._regions:
            groups = [region + '/' + category for region in self._regions for category in self._categories]
        groups = list(map(self._add_main_domain, groups))

        if self._parser_type == 'dates':
            start_urls = {group[len(self.DOMAIN):]: {k: None for k in self._get_dates()} for group in groups}
        else:
            start_urls = {group[len(self.DOMAIN):]: {f'p{i}': None for i in range(1, self._n_pages + 1)}
                          for group in groups}


        return start_urls


    def _get_dates(self):
        start = std_parse(self._start_date)
        end = std_parse(self._end_date)

        current_date = start
        dates = []

        while current_date <= end:
            date = current_date.strftime("%Y/%m/%d")
            dates.append(date)
            current_date += timedelta(days=1)

        return dates

    def _check_n_pages(self):
        if not hasattr(self, '_n_pages'):
            if (not hasattr(self, '_start_date')) | (not hasattr(self, '_end_date')):
                raise NotImplementedError('At least one of the (n_pages, (start_date, end_date)) arguments must be implemented')
            else:
                return (std_parse(self._end_date) - std_parse(self._start_date)).days
        else:
            return self._n_pages


    @staticmethod
    def _check_null(param, param_name):
        if not param:
            raise ValueError(f'{param_name} cannot be {param}')
        return param

    def _add_main_domain(self, x):
        return self.DOMAIN + x

    @abstractmethod
    def _get_start_urls(self):
        """Returns urls of the pages
                   to search article links in"""
        pass

    @staticmethod
    @abstractmethod
    def _get_url_links(url):
        """Finds and returns all urls
                   using the page url"""
        pass

    def _get_all_urls(self):
        start_urls = self._get_start_urls()
        all_urls = deepcopy(start_urls)

        with Progress() as progress:
            task = progress.add_task("[blue]Getting [purple]links...",
                                     total=len(all_urls) * self._n_pages)
            for k1, v1 in all_urls.items():
                for k2 in v1.keys():
                    all_urls[k1][k2] = self._get_url_links(path.join(self.DOMAIN, k1, k2),
                                                           progress, task)
        return all_urls

    @staticmethod
    @abstractmethod
    def _get_title(soup_obj):
        """Parses the title of an article
                   and returns the text"""
        pass

    @staticmethod
    @abstractmethod
    def _get_body(soup_obj):
        """Parses the body of an article
                   and returns the text"""
        pass

    @abstractmethod
    def _parse(self, progress, task, total, url, category, *args, **kwargs):
        """Returns a dict of parsed data with "title", "body", "category", etc. as keys.
                   - Progress and task args are used to track th progress. They are implemented inside
                   the self.Parse method.
                   - Url is the url link of the current article being parsed"""

    def Parse(self):
        all_urls = self._get_all_urls()
        parsed_articles = deepcopy(all_urls)
        total = Parsed(parsed_articles).count()

        self._iter = 0
        with Progress() as progress:
            task = progress.add_task("[blue]Parsing...", total=total)
            for k1, v1 in parsed_articles.items():
                for k2 in v1.keys():
                    parsed_articles[k1][k2] = [self._parse(progress, task, total,
                                                           url, k1, k2) for url in all_urls[k1][k2]]
        return Parsed(parsed_articles)



class Parsed:
    def __init__(self, parsed_articles):
        self.parsed_articles = parsed_articles
        self.articles_list = self._get_articles_list()

    def __repr__(self):
        return f"""{self.__class__.__name__}:
        - Categories: {self._get_categories()}
        - Subcategories: {self._get_subcategories()}
        - Articles parsed: {self.count()}"""

    def __add__(self,x):
        if isinstance(x, self.__class__):
            return self.articles_list + x.to_list()
        if isinstance(x, list):
            return self.articles_list + x
        raise TypeError(f'{type(x)} is not a {self.__class__.__name__} object or list')

    def __radd__(self,x):
        if isinstance(x, self.__class__):
            return x.tolist() + self.articles_list
        if isinstance(x, list):
            return x + self.articles_list
        raise TypeError(f'{type(x)} is not a Parsed object or list')

    def count(self):
        return len(self.articles_list)

    def _get_articles_list(self):
        articles_list = []
        for k1, v1 in self.parsed_articles.items():
            for k2, v2 in v1.items():
                for article in v2:
                    articles_list.append(article)
        return articles_list

    def to_list(self):
        return self.articles_list

    def to_dict(self):
        return self.parsed_articles

    def get_first(self, n=None):
        if not n:
            return self.articles_list
        return self.articles_list[:n]

    def _get_categories(self):
        f = lambda x: x.split('/')[0]
        if '/' in list(self.parsed_articles.keys())[0]:
            return set(map(f, self.parsed_articles.keys()))
        return set(self.parsed_articles.keys())

    def _get_subcategories(self):
        f = lambda x: x.split('/')[1]
        if '/' in list(self.parsed_articles.keys())[0]:
            return set(map(f, self.parsed_articles.keys()))
        return {}

    def save(self, path_to_file):
        with open(path_to_file, 'wb') as f:
            pickle.dump(self, f)

    def translate(self, which='body', dest='en'):
        transethlator = partial(translator.translate, dest=dest)

        def _alter(d):
            if isinstance(which, list):
                for key in which:
                    d[key] = transethlator(d[key]).text
            else:
                d[which] = transethlator(d[which]).text

            return d

        out = list(map(_alter, deepcopy(self.articles_list)))
        return out
