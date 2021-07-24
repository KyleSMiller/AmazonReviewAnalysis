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
    def __init__(self, productKeyword, n=-1, reviewN=-1):
        """
        :param productKeyword:  The product to search and scrape reviews from
        :param n:               The number of products to scrape for reviews. -1 for all
        :param reviewN:         The number of pages of reviews to scrape from each product. -1 for all
        """
        self.__productKeyword = productKeyword
        self.__products = {}  # format as:
        """
            {"product_id": 
                {
                "url": str,
                "name": str,
                "rating": float,
                "price": float,
                "count": int
                "pricePer": float
                "reviews": [{"user": str, "rating": float, "text": str}, {"user": str, "rating": float, "text": str}, ...]
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

        self.__session = requests.Session()

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

        for product in self.__products.keys():
            self.__getReviews(product, reviewN)


    """
    Public Methods
    """

    def getProducts(self):
        return self.__products


    """
    Private Methods
    """

    def __openResultsPage(self, page=1):
        """
        Open a page of amazon search results
        :param page:  the page number to open
        :return:      the lxml etree of the page
        """
        self.__session.get("https://www.amazon.com/s?k=" + self.__productKeyword, headers=self.__BAD_HEADERS)  # dummy request
        print("Opening " + self.__productKeyword + " page " + str(page) + "...")
        sleep(12 + (random.random() * 2))
        productListPage = self.__session.get("https://www.amazon.com/s?k=" + self.__productKeyword + "&page=" + str(page), headers=self.__HEADERS)
        productListTree = etree.ElementTree(html.fromstring(productListPage.content))

        title = productListTree.xpath('//title')[0].text
        if title != "Amazon.com : " + self.__productKeyword:
            print("AMAZON CAUGHT THE SCRAPER -- TRY NEW HEADERS")

        return productListTree

    def __openProductReviews(self, url, id, page=1):
        """
        Open the review page of a given product
        :param url:  the url of the product
        :return:     the lxml etree of the page
        """
        basicUrl = re.sub("dp/" + id + ".*", "", url)  # truncate the unneeded parts of the URL

        self.__session.get("https://www.amazon.com/" + basicUrl + "product-reviews/" +
                     id + "/reviewerType=all_reviews&pageNumber=" + str(page), headers=self.__BAD_HEADERS)
        print("Opening ASIN " + str(id) + " reviews: page " + str(page) + "...")
        sleep(12 + (random.random() * 2))
        productReviewPage = self.__session.get("https://www.amazon.com/" + basicUrl + "product-reviews/" +
                                         id + "/reviewerType=all_reviews/ref=cm_cr_getr_d_paging_btm_next_" +
                                               str(page) + "?pageNumber=" + str(page), headers=self.__HEADERS)
        productReviewTree = etree.ElementTree(html.fromstring(productReviewPage.content))
        print(productReviewPage.url)
        return productReviewTree

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
            if len(re.findall("slredirect/", productUrl)) == 0:  # skip special URLs (amazon features, etc.)
                productId = re.findall("B0[A-Z|0-9]{8}", productUrl)[0]
                try:
                    # this should never fail, but since this script takes days to run, I'm catching all remotely possible errors
                    productName = products[i].xpath('.//span[@class="a-size-base-plus a-color-base a-text-normal"]')[0].text
                except:
                    productName = None
                try:
                    productPrice = float(products[i].xpath('.//span[@class="a-price"]')[0].xpath('.//span[@class="a-offscreen"]')[0].text[1:])
                except:
                    continue  # ignore products that do not list their price

                try:
                    count = products[i].xpath('.//span[@class="a-color-information a-text-bold"]')[0].text.strip()
                    count = int(re.sub("Count .*", "", count))
                except:  # not all products have count listed
                    count = None

                try:
                    pricePer = float(re.findall("[0-9]+.?[0-9]+", products[i].xpath('.//span[@class="a-size-base a-color-secondary"]')[0].text)[0])
                except:
                    if count != None:
                        pricePer = productPrice / count
                    else:
                        pricePer = None

                self.__products[productId] = {
                    "url": productUrl,
                    "name": productName,
                    "rating": None,  # get product rating later, as the xPaths needed for it here are very, very messy
                    "price": productPrice,
                    "count": count,  # may be None
                    "pricePer": pricePer,  # may be None
                    "reviews": []
                }

                print("Found Product: " + productId)

    def __getReviews(self, product, n):
        """
        Get the reviews for a specified product
        :param product:  the product's ID (ASIN number)
        :param n:        the number of pages of reviews to scrape
        """
        reviewsTree = self.__openProductReviews(self.__products[product]["url"], product)

        # Data formatted as:  " 3,334 global ratings | 1,110 global reviews "
        # Get the number of global reviews
        try:
            reviewsCount = reviewsTree.xpath('/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[4]/div/span')[0].text.strip()
            totalReviews = int("".join(re.findall("[0-9]+", re.sub(".*\| ", "", reviewsCount))))
        except:
            totalReviews = 0
        if totalReviews == 0:
            return
        else:
            REVIEWS_PER_PAGE = 10
            totalPages = totalReviews // REVIEWS_PER_PAGE

        # get the ratings of the product
        try:
            scoreRaw = reviewsTree.xpath('/html/body/div[1]/div[2]/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div/div[2]/div/span')[0].text.strip()
            self.__products[product]["rating"] = re.findall("[0-9]+.?[0-9]? ", scoreRaw)[0]
        except:
            self.__products[product]["rating"] = None

        # get page 1 of reviews
        try:
            reviews = reviewsTree.xpath('.//div[@class="a-section review aok-relative"]')
            for review in reviews:
                self.__products[product]["reviews"].append(self.__extractReviewInfo(review))
        except:
            return

        # get the rest of the reviews for this product
        for page in range(1, totalPages):
            if n != -1 and page > n:
                return
            else:
                try:
                    reviewsTree = self.__openProductReviews(self.__products[product]["url"], product, page+1)
                    reviews = reviewsTree.xpath('.//div[@class="a-section review aok-relative"]')
                    for review in reviews:
                        self.__products[product]["reviews"].append(self.__extractReviewInfo(review))
                except:
                    return


    def __extractReviewInfo(self, reviewDiv):
        """
        Extract review information from a provided review div
        :param reviewDiv:  an HTML div containing the review
        :return:           a dict with the extracted data
        """
        try:
            user = reviewDiv.xpath('.//span[@class="a-profile-name"]')[0].text
        except:
            user = None
        try:
            rating = float(re.sub(" out of .*", "", reviewDiv.xpath('.//i[@data-hook="review-star-rating"]')[0].xpath('.//span[@class="a-icon-alt"]')[0].text))
        except:
            rating = None
        try:
            text = reviewDiv.xpath('.//span[@class="a-size-base review-text review-text-content"]/span')[0].text.strip()
        except:
            text = None

        print("---------")
        print("USER: " + str(user))
        print("RATING: " + str(rating))
        print("REVIEW: " + str(text))
        print()

        return {"user": user, "rating": rating, "text": text}
