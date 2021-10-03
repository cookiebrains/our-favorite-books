import requests

BOOKS_DB_SEARCH = "https://www.googleapis.com/books/v1/volumes"


def get_candidates(query):
    parameters = {
        "q": query
    }
    response = requests.get(url=BOOKS_DB_SEARCH, params=parameters)
    response.raise_for_status()
    return response.json()['items'][:5]


def get_movie_data(book_api_id):
    book_api_url = f"{BOOKS_DB_SEARCH}/{book_api_id}"
    response = requests.get(book_api_url)
    return response.json()
