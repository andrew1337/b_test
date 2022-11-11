import os
from requests import get as request_get

from backend import movie as movie_model


class LoaderError(Exception):
    pass


class OMDBToMoviesLoader:
    base_url_many = "https://www.omdbapi.com/?apikey=%s&s=%s&page=%i"
    base_url_one = "https://www.omdbapi.com/?apikey=%s&t=%s"
    api_key = os.getenv("OMDB_API_KEY")

    @staticmethod
    def _make_api_request(url: str):
        try:
            resp = request_get(url)
            resp.raise_for_status()
            data = resp.json()
            return data
        except Exception as e:
            raise LoaderError(e)

    @staticmethod
    def _do_save(movie: dict):
        fields_mapping = {
            "Title": "title",
            "Year": "year",
            "imdbID": "imdb_id",
            "Type": "m_type",
        }
        movie_details = {v: movie.get(k) for k, v in fields_mapping.items()}
        return movie_model.Movie.create(**movie_details)

    @staticmethod
    def _check_paginated_count(data: dict, quantity: int):
        if int(data.get("totalResults", 0)) < quantity:
            raise LoaderError(
                f"The current number of results is less than required {quantity=}"
            )

    @staticmethod
    def _check_response_status(data: dict):
        if data.get("Response") == "False":
            raise LoaderError(f"An api error occurred {data.get('Error')=}")

    @classmethod
    def fetch_one(cls, title_contains: str):
        data = cls._make_api_request(cls.base_url_one % (cls.api_key, title_contains))
        cls._check_response_status(data)
        return cls._do_save(data)

    @classmethod
    def fetch_many(cls, title_contains: str, quantity: int):
        movies_count = 0
        page = 1
        while movies_count < quantity:
            data = cls._make_api_request(
                cls.base_url_many % (cls.api_key, title_contains, page)
            )
            cls._check_response_status(data)
            cls._check_paginated_count(data, quantity)
            movies = data.get("Search")
            for movie in movies:
                cls._do_save(movie)
                movies_count += 1
                if movies_count == quantity:
                    break
            page += 1
