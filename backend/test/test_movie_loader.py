from backend import test, movie
from backend import movie_loader


class TestMovie(test.TestCase):
    def test_fetch_many(self):
        def _correct_api_request(_):
            return {
                "Search": [
                    {
                        "Title": "Night at the Museum",
                        "Year": "2006",
                        "imdbID": "tt0477347",
                        "Type": "movie",
                    },
                    {
                        "Title": "Game Night",
                        "Year": "2018",
                        "imdbID": "tt2704998",
                        "Type": "movie",
                    },
                    {
                        "Title": "Night at the Museum: Battle of the Smithsonian",
                        "Year": "2009",
                        "imdbID": "tt1078912",
                        "Type": "movie",
                    },
                    {
                        "Title": "30 Days of Night",
                        "Year": "2007",
                        "imdbID": "tt0389722",
                        "Type": "movie",
                    },
                    {
                        "Title": "Date Night",
                        "Year": "2010",
                        "imdbID": "tt1279935",
                        "Type": "movie",
                    },
                    {
                        "Title": "The Night Of",
                        "Year": "2016",
                        "imdbID": "tt2401256",
                        "Type": "series",
                    },
                    {
                        "Title": "Last Night in Soho",
                        "Year": "2021",
                        "imdbID": "tt9639470",
                        "Type": "movie",
                    },
                    {
                        "Title": "Night of the Living Dead",
                        "Year": "1968",
                        "imdbID": "tt0063350",
                        "Type": "movie",
                    },
                    {
                        "Title": "Night at the Museum: Secret of the Tomb",
                        "Year": "2014",
                        "imdbID": "tt2692250",
                        "Type": "movie",
                    },
                    {
                        "Title": "Run All Night",
                        "Year": "2015",
                        "imdbID": "tt2199571",
                        "Type": "movie",
                    },
                ],
                "totalResults": "12345",
                "Response": "True",
            }

        movie_loader.OMDBToMoviesLoader._make_api_request = _correct_api_request
        movie_loader.OMDBToMoviesLoader.fetch_many("Search pattern", 8)
        self.assertEqual(
            8, len(movie.Movie.get_ordered_and_paginated_list(offset=0, limit=10))
        )

    def test_fetch_one(self):
        def _single_movie_response(_):
            return {
                "Title": "Matrix",
                "Year": "1993",
                "Rated": "N/A",
                "Released": "01 Mar 1993",
                "Runtime": "60 min",
                "Genre": "Action, Drama, Fantasy",
                "Director": "N/A",
                "Writer": "Grenville Case",
                "Actors": "Nick Mancuso, Phillip Jarrett, Carrie-Anne Moss",
                "Plot": 'Steven Matrix is one of the underworld\'s foremost hitmen until his luck runs out, and someone puts a contract out on him. Shot in the forehead by a .22 pistol, Matrix "dies" and finds himself in "The City In Between", where he is ...',
                "Language": "English",
                "Country": "Canada",
                "Awards": "1 win",
                "Poster": "https://m.media-amazon.com/images/M/MV5BYzUzOTA5ZTMtMTdlZS00MmQ5LWFmNjEtMjE5MTczN2RjNjE3XkEyXkFqcGdeQXVyNTc2ODIyMzY@._V1_SX300.jpg",
                "Ratings": [{"Source": "Internet Movie Database", "Value": "7.7/10"}],
                "Metascore": "N/A",
                "imdbRating": "7.7",
                "imdbVotes": "194",
                "imdbID": "tt0106062",
                "Type": "series",
                "totalSeasons": "N/A",
                "Response": "True",
            }

        movie_loader.OMDBToMoviesLoader._make_api_request = _single_movie_response
        obj = movie_loader.OMDBToMoviesLoader.fetch_one("Search pattern")
        self.assertEqual("Matrix", obj.title)

    def test_fetch_search_error(self):
        def _err_api_request(_):
            return {"Response": "False", "Error": "Movie not found!"}

        movie_loader.OMDBToMoviesLoader._make_api_request = _err_api_request
        with self.assertRaises(movie_loader.LoaderError):
            movie_loader.OMDBToMoviesLoader.fetch_many(
                title_contains="Search pattern", quantity=123
            )
