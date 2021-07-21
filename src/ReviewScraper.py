import random
import requests
from lxml import html, etree
from time import sleep
import regex as re

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
        self.__products = {}  # format as:
        """
            {"<product_id>": 
                {
                "url": "url",
                "name": "productName",
                "rating": rating,
                "price": price,
                "count": count
                "pricePer": price per pill
                "reviews": ["review 1", "review 2", ...]
                }
            }
        """

        self.__HEADERS = ({'User-Agent':
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit / 537.36(KHTML, like Gecko)Chrome / 44.0.2403.157 Safari / 537.36',
                    'Accept-Language': 'en-US, en;q=0.5'
                    })

        self.__BAD_HEADERS = {'user-agent':
                           'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
                       }
        # Amazon will catch and block web-scrapers if you use the same headers twice in a row
        # So, use this other set of headers (BAD_HEADERS) to break up the pattern
        # This first set of headers will get rejected by Amazon, but that's okay
        # They're only intended to make Amazon forget about the previous headers we used
        # I also recommend you just open up amazon yourself and load a random page between each usage of this class
        # It's not required, but anything to help your PC not look like a web-scraper is good practice

        # find n products that match the given keyword
        PRODUCTS_PER_PAGE = 48  # temp hard-code of products per page
        for page in range((n // PRODUCTS_PER_PAGE) + 1):
            nForPage = (PRODUCTS_PER_PAGE if (n - (PRODUCTS_PER_PAGE * (page+1))) >= 0 else
                        PRODUCTS_PER_PAGE + (n - (PRODUCTS_PER_PAGE * (page+1))))
            self.__getProducts(nForPage, page+1)


    """
    Public Methods
    """






    """
    Private Methods
    """

    def __openResultsPage(self, page=1):
        """
        Open a page of amazon search results
        :param page:  the page number to open
        :return:      the lxml etree of the page
        """
        requests.get("https://www.amazon.com/s?k=" + self.__productKeyword, headers=self.__BAD_HEADERS)  # dummy request
        print("Opening " + self.__productKeyword + " page " + str(page) + "...")
        sleep(10)
        productListPage = requests.get("https://www.amazon.com/s?k=" + self.__productKeyword + "&page=" + str(page), headers=self.__HEADERS)
        productListTree = etree.ElementTree(html.fromstring(productListPage.content))

        title = productListTree.xpath('//title')[0].text
        if title != "Amazon.com : " + self.__productKeyword:
            print("AMAZON CAUGHT THE SCRAPER -- TRY NEW HEADERS")

        return productListTree

    def __openProductReviews(self, url):
        requests.get("https://www.amazon.com", headers=self.__BAD_HEADERS)
        print("Opening ")
        sleep(10)
        productReviewPage = requests.get("https://www.amazon.com/" + url + "")



    def __getProducts(self, n, page):
        """
        Get the first n products that come up for a given keyword search
        Use the found data to set up a dict of all products
        """
        # the number of products that come up when the keyword is searched
        productListTree = self.__openResultsPage(page)

        showingResults = productListTree.xpath('/html/body/div[1]/div[2]/span/div/span/h1/div/div[1]/div/div/span[1]')[0].text
        productCount = int(re.sub(" results for", "", re.sub("[0-9]+-[0-9]+ of ", "", showingResults)))
        # print("There are " + str(productCount) + " results for the keyword: " + self.__productKeyword)

        products = productListTree.xpath('//div[@data-component-type="s-search-result"]')

        if n == -1:
            n = int(productCount)
        for i in range(n):
            productHref = products[i].xpath('.//a[@class="a-link-normal s-no-outline"]')
            productUrl = str(productHref[0].get("href"))
            productId = re.findall("B0[A-Z|0-9]{8}", productUrl)
            self.__products[productId] = {
                "url": productUrl,
                "name": None,
                "rating": None,
                "price": None,
                "count": None,
                "pricePer": None,
                "reviews": []
            }
            # TODO: currently, some odd IDs are getting captured. They redirect you to other IDs.
            # TODO: I think the [@class="a-link-normal s-no-outline"] isn't a perfect system.
            # TODO: Figure out a fix for it, or ignore it if it's only a very small number of ID's
            # TODO: I think it's linked to the Amazon recommended products thing
            # print("HREF: " + str(productHref[0].get("href")))
            # print("ID: " + productId)



test = ReviewScraper("phosphatidylserine", 10)

class AmazonReview:
    # just a way to easily store review data
    def __init__(self, user, productID, rating, txt):
        self.user = user
        self.productID = productID
        self.rating = rating
        self.txt = txt