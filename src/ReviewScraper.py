import random
import requests
from lxml import html, etree

class ReviewScraper:
    """
    Scrape reviews from amazon given a product keyword
    Using requests & lxml libraries
    """
    def __init__(self, productKeyword, n=-1):
        """
        :param productKeyword:  The product to search and scrape reviews from
        :param n:               The number of reviews to scrape. -1 for all
        """
        self.__productKeyword = productKeyword

        # amazon blocks web scraping, so try to get around that
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
        proxiesList = ["128.199.109.241:8080", "113.53.230.195:3128", "125.141.200.53:80", "125.141.200.14:80",
                        "128.199.200.112:138", "149.56.123.99:3128", "128.199.200.112:80", "125.141.200.39:80",
                        "134.213.29.202:4444"]
        proxies = {'https': random.choice(proxiesList)}
        self.__productListPage = requests.get("https://www.amazon.com/s?k=" + self.__productKeyword,
                                              headers=headers) #proxies=proxies)

        self.__productListTree = html.fromstring(self.__productListPage.content)
        self.__productListTree = etree.ElementTree(self.__productListTree)
        self.__products = {}  # format as:
        """
            {"<product_id>": 
                {
                "name": "productName", 
                "reviews": ["review 1", "review 2", ...]
                }
            }
        """
        self.__getProducts(n)

    def __getProducts(self, n):
        """
        Get the first n products that come up for a given keyword search
        Use the found data to set up a dict of all products
        """
        # the number of products that come up when the keyword is searched
        productCount = self.__productListTree.xpath('//title')  #'/html/body/div[1]/div[2]/span/div/span/h1/div/div[1]/div/div/span[1]')
        print(productCount[0].text)
        print(self.__productListPage.content)

        if n == -1:
            n = productCount
        for i in range(n):
            pass



test = ReviewScraper("phosphatidylserine", n=10)