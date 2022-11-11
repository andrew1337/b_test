import typing

from google.cloud import ndb
from backend import error
from backend import movie_loader


class NotFound(error.Error):
    pass


class LoadError(error.Error):
    pass


class Movie(ndb.Model):
    title = ndb.StringProperty(indexed=True, required=True)
    normalized_title = ndb.ComputedProperty(
        lambda self: self.title.lower(), indexed=True
    )
    year = ndb.StringProperty()
    imdb_id = ndb.StringProperty(indexed=True)
    m_type = ndb.StringProperty()

    def __hash__(self):
        return hash((self.__class__.__name__, self.id))

    def delete(self):
        self.key.delete()

    @property
    def id(self):
        return self.key.urlsafe().decode("utf-8")

    @classmethod
    def get_ordered_and_paginated_list(cls, offset: int, limit: int):
        return cls.search(None, offset=offset, limit=limit, order_by_title=True)

    @classmethod
    def get(cls, id):
        entity = ndb.Key(urlsafe=id).get()
        if entity is None or not isinstance(entity, cls):
            raise NotFound(f"No movie found with {id=}")
        return entity

    @classmethod
    def get_by_title(cls, title: str):
        try:
            entity = cls.search(title, offset=0, limit=1)[0]
        except IndexError:
            raise NotFound(f"No movie found with {title=}")
        return entity

    @classmethod
    def add(cls, title):
        try:
            return movie_loader.OMDBToMoviesLoader.fetch_one(title_contains=title)
        except movie_loader.LoaderError:
            raise LoadError("Can't load the movie details")

    @classmethod
    def create(cls, title: str, year: str, imdb_id: str, m_type: str):
        entity = cls(title=title, year=year, imdb_id=imdb_id, m_type=m_type)
        entity.put()
        return entity

    @classmethod
    def count(cls):
        return cls.query().count()

    @classmethod
    def search(
        cls,
        title_to_search: typing.Optional[str],
        offset: int,
        limit: int,
        order_by_title: bool = False,
    ):
        query = cls.query()
        if title_to_search is not None and len(title_to_search) >= 3:
            query = query.filter(
                cls.normalized_title >= title_to_search.lower(),
                cls.normalized_title < title_to_search.lower() + "\uFFFD",
            )
        if order_by_title:
            query = query.order(cls.title)
        return query.fetch(offset=offset, limit=limit)
