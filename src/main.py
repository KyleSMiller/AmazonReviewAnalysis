import pandas as pd
from src.ReviewScraper import ReviewScraper


scraper = ReviewScraper(productKeyword="phosphatidylserine", n=10, reviewN=1)
reviews = pd.DataFrame.from_dict(scraper.getProducts())


# test = {"121231": {"name": "product 1", "price": 10.23, "reviews": [{"name": "bob", "score": 4.5, "review": "loved it"}, {"name": "marley", "score": 1.0, "review": "sucks"}]},
#         "421233": {"name": "product 2", "price": 9.99, "reviews": [{"name": "jim", "score": 5, "review": "perfect"}, {"name": "jane", "score": 2.0, "review": "what"}]}}
# reviews = pd.DataFrame.from_dict(test)

print(reviews)

reviews.to_pickle("../reviews.pkl")