from backend import api, movie
from backend.oauth2 import oauth2
from backend.swagger import swagger
from backend.wsgi import remote, messages, message_types


class AddMovieRequest(messages.Message):
    title = messages.StringField(1, required=True)
    year = messages.StringField(2)
    imdb_id = messages.StringField(3)
    m_type = messages.StringField(4)


class GetMovieRequest(messages.Message):
    title = messages.StringField(1)


class MovieResponse(messages.Message):
    id = messages.StringField(1)
    title = messages.StringField(2)
    year = messages.StringField(3)
    imdb_id = messages.StringField(4)
    m_type = messages.StringField(5)


class ListMovieRequest(messages.Message):
    limit = messages.IntegerField(1, default=10)
    offset = messages.IntegerField(2, default=0)


class ListMovieResponse(messages.Message):
    limit = messages.IntegerField(1, required=True)
    offset = messages.IntegerField(2, required=True)
    count = messages.IntegerField(3, required=True)
    items = messages.MessageField(MovieResponse, 4, repeated=True, required=False)


class DeleteMovieRequest(messages.Message):
    id = messages.StringField(1, required=True)


@api.endpoint(path="movie", title="Movie API")
class Movie(remote.Service):
    @staticmethod
    def _get_response_by_model(m: movie.Movie) -> MovieResponse:
        return MovieResponse(
            id=m.id,
            title=m.title,
            year=m.year,
            imdb_id=m.imdb_id,
            m_type=m.m_type,
        )

    @swagger("Add movie")
    @remote.method(AddMovieRequest, MovieResponse)
    def create(self, request):
        if all((request.title, request.year, request.imdb_id, request.m_type)):
            new_movie = movie.Movie.create(
                title=request.title,
                year=request.year,
                imdb_id=request.imdb_id,
                m_type=request.m_type,
            )
        else:
            new_movie = movie.Movie.add(request.title)
        return self._get_response_by_model(new_movie)

    @swagger("Get movie by title")
    @remote.method(GetMovieRequest, MovieResponse)
    def get(self, request):
        movie_found = movie.Movie.get_by_title(title=request.title)
        return self._get_response_by_model(movie_found)

    @swagger("Paginated list of movies ordered by title")
    @remote.method(ListMovieRequest, ListMovieResponse)
    def list(self, request):
        movies = movie.Movie.get_ordered_and_paginated_list(
            offset=request.offset, limit=request.limit
        )
        return ListMovieResponse(
            offset=request.offset,
            limit=request.limit,
            count=movie.Movie.count(),
            items=[self._get_response_by_model(m) for m in movies if m is not None],
        )

    @swagger("Delete movie")
    @oauth2.required()
    @remote.method(DeleteMovieRequest, message_types.VoidMessage)
    def delete(self, request):
        movie.Movie.get(id=request.id).delete()
        return message_types.VoidMessage()
