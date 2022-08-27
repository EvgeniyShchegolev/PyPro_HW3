from functools import reduce
import re
from time import sleep
import requests
import bs4


class ArticleHubr:
    """Класс для выборки статей из сайта Хабр по ключевым словам"""
    def __init__(self, keywords=list):
        self.keywords = set(keywords)
        self.url = 'https://habr.com'
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru - RU, ru; q = 0.9, en - US; q = 0.8, en; q = 0.7",
            "Connection": "keep - alive",
            "Cookie": "_ym_d = 1647427542; _ym_uid = 1647427542315364557; "
                      "_ga = GA1.2.1828127353.1647427543; fl = ru; hl = ru; "
                      "habr_web_home_feed = / all /; _ym_isad = 2",
            "Host": "habr.com",
            "If-None-Match": 'W/"2e97-M/h3KkFAZXgTcBdsKz1SCh6O9l4"',
            "Referer": "https://habr.com/ru/all/",
            "sec-ch-ua": '"Not A;Brand"; v = "99", "Chromium"; v = "104", "Opera"; v = "90"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "Windows",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0(Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36(KHTML, like Gecko) '
                          'Chrome/104.0.5112.102 Safari/537.36 '
                          'OPR/90.0.4480.54 (Edition Yx 05)',
            'x-app-version': '2.87.0'
        }

    def _get_soup_of_request(self, url_article='/ru/all'):
        """Отправляет запрос по url'у и на выход передаёт файл-суп"""
        resp = requests.get(url=self.url + url_article, headers=self.headers)
        soup = bs4.BeautifulSoup(resp.text, features="html.parser")
        return soup

    def get_article(self):
        """Выбирает статьи из страницы preview по ключевым словам"""
        soup = self._get_soup_of_request()
        articles = soup.find_all(class_="tm-article-snippet")

        for article in articles:
            sleep(0.5)
            # Заголовки статей
            title = article.find('h2').find('a')
            title_set = set(self._clear_text_list(title.text))
            # Хабы статей
            hubs = article.find_all(class_='tm-article-snippet__hubs-item')
            hubs_set = {hub.find('a').text.replace('*', '').lower() for hub in hubs}
            # Тело preview статьи
            prev_body = article.find(class_='article-formatted-body '
                                            'article-formatted-body '
                                            'article-formatted-body_version-2')
            # Если текст preview статьи есть:
            if prev_body:
                text_body = [self._clear_text_list(text_.text) for text_ in prev_body]
                text_set = set(reduce(lambda x, y: set(x) | set(y), text_body))

                if (title_set | text_set | hubs_set) & self.keywords:
                    self._print_result(article.find('time')['title'], title.text, title['href'])
                    continue
            # Если текст preview статьи отсутствует:
            else:
                if (title_set | hubs_set) & self.keywords:
                    self._print_result(article.find('time')['title'], title.text, title['href'])
                    continue
            # Поиск внутри статей
            soup_in = self._get_soup_of_request(title['href'])
            article_in = soup_in.find(class_='article-formatted-body '
                                             'article-formatted-body '
                                             'article-formatted-body_version-2')
            # Если версия не 2
            if not article_in:
                article_in = soup_in.find(class_='article-formatted-body '
                                                 'article-formatted-body '
                                                 'article-formatted-body_version-1')

                if self._check_keywords_in_article(article_in):
                    self._print_result(article.find('time')['title'], title.text, title['href'])
                    continue
            # Если версия 2
            if self._check_keywords_in_article(article_in):
                self._print_result(article.find('time')['title'], title.text, title['href'])

    def _check_keywords_in_article(self, text_in='bs4.element.Tag'):
        """Проверяет есть ли в тексте статьи ключевые слова"""
        text_article = [self._clear_text_list(body.text) for body in text_in]
        text_article_set = set(reduce(lambda x, y: set(x) | set(y), text_article))
        return text_article_set & self.keywords

    @staticmethod
    def _clear_text_list(text=str):
        """Принимает на вход строку и выдаёт на выход список из очищенных от лишних знаков слов"""
        text_clear = re.sub(r'\W', ' ', text).lower()
        return text_clear.split()

    def _print_result(self, date=str, title=str, url=str):
        """Принимает на вход данные и выводит в отформатированном варианте на экран"""
        url_ = self.url + url
        print(f"{date} - {title} - {url_}")


if __name__ == "__main__":
    KEYWORDS = ['дизайн', 'фото', 'web', 'python']
    ar = ArticleHubr(KEYWORDS)
    ar.get_article()
