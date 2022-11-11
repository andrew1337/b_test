from backend import test, movie


class TestMovie(test.TestCase):
    def test_create(self):
        obj = movie.Movie.create(
            title="Matrix", year="1993", imdb_id="tt0106062", m_type="series"
        )
        self.assertEqual(obj, movie.Movie.get(obj.id))
        self.assertTrue(obj.title == "Matrix")
        self.assertTrue(obj.year == "1993")
        self.assertTrue(obj.imdb_id == "tt0106062")
        self.assertTrue(obj.m_type == "series")

    def test_get_by_title(self):
        obj = movie.Movie.create(
            title="Matrix", year="1993", imdb_id="tt0106062", m_type="series"
        )
        self.assertEqual(obj, movie.Movie.get_by_title(title="Matrix"))
        self.assertEqual(obj, movie.Movie.get_by_title(title="matr"))
        with self.assertRaises(movie.NotFound):
            movie.Movie.get_by_title(title="Star Wars")

    def test_delete_by_id(self):
        obj = movie.Movie.create(
            title="Matrix", year="1993", imdb_id="tt0106062", m_type="series"
        )
        obj.delete()
        with self.assertRaises(movie.NotFound):
            movie.Movie.get(id=obj.id)

    def test_search(self):
        movie.Movie.create(
            title="Matrix", year="1993", imdb_id="tt0106062", m_type="series"
        )
        self.assertEqual(1, len(movie.Movie.search("matr", offset=0, limit=1)))
        self.assertEqual(0, len(movie.Movie.search("Titanic", offset=0, limit=1)))

    def test_get_ordered_and_paginated(self):
        movie.Movie.create(
            title="Ddd", year="1997", imdb_id="tt0106065", m_type="series"
        )
        movie.Movie.create(
            title="Ccc", year="1999", imdb_id="tt0106064", m_type="series"
        )
        movie.Movie.create(
            title="Aaa", year="1993", imdb_id="tt0106062", m_type="series"
        )
        movie.Movie.create(
            title="Bbb", year="2020", imdb_id="tt0106063", m_type="series"
        )
        #
        all_movies = movie.Movie.get_ordered_and_paginated_list(offset=0, limit=10)
        self.assertEqual(4, len(all_movies))
        self.assertEqual("Aaa", all_movies[0].title)
        #
        paginated_movies = movie.Movie.get_ordered_and_paginated_list(offset=2, limit=2)
        self.assertEqual(2, len(paginated_movies))
        self.assertEqual("Ddd", paginated_movies[-1].title)


class TestMovieApi(test.TestCase):

    def test_create(self):
        resp = self.api_client.post(
            "movie.create",
            dict(title="Matrix", year="1993", imdb_id="tt0106062", m_type="series"),
        )
        self.assertEqual(None, resp.get("error"))
        self.assertEqual("Matrix", resp.get("title"))
        self.assertEqual("1993", resp.get("year"))
        self.assertEqual("tt0106062", resp.get("imdb_id"))
        self.assertEqual("series", resp.get("m_type"))

    def test_get(self):
        self.api_client.post(
            "movie.create",
            dict(title="Matrix", year="1993", imdb_id="tt0106062", m_type="series"),
        )
        resp = self.api_client.post("movie.get", dict(title="matr"))
        self.assertEqual(None, resp.get("error"))
        self.assertEqual("Matrix", resp.get("title"))
        #
        empty_title_resp = self.api_client.post("movie.get")
        self.assertEqual(None, empty_title_resp.get("error"))
        self.assertEqual("Matrix", empty_title_resp.get("title"))
        #
        not_found_resp = self.api_client.post("movie.get", dict(title="Titanic"))
        self.assertEqual(True, bool(not_found_resp.get("error")))
        self.assertEqual("NotFound", not_found_resp.get("error").get("error_name"))

    def test_list(self):
        empty_resp = self.api_client.post("movie.list")
        self.assertEqual(None, empty_resp.get("error"))
        self.assertEqual(None, empty_resp.get("items"))
        #
        self.api_client.post(
            "movie.create",
            dict(title="Ddd", year="1997", imdb_id="tt0106065", m_type="series"),
        )
        self.api_client.post(
            "movie.create",
            dict(title="Ccc", year="1999", imdb_id="tt0106064", m_type="series"),
        )
        self.api_client.post(
            "movie.create",
            dict(title="Aaa", year="1993", imdb_id="tt0106062", m_type="series"),
        )
        self.api_client.post(
            "movie.create",
            dict(title="Bbb", year="2020", imdb_id="tt0106063", m_type="series"),
        )
        resp = self.api_client.post("movie.list")
        self.assertEqual(None, resp.get("error"))
        self.assertEqual(4, len(resp.get("items")))
        self.assertEqual(4, resp.get("count"))
        self.assertEqual(10, resp.get("limit"))
        self.assertEqual(0, resp.get("offset"))
        #
        limit_and_offset_resp = self.api_client.post(
            "movie.list", dict(limit=2, offset=2)
        )
        self.assertEqual(None, limit_and_offset_resp.get("error"))
        self.assertEqual(2, len(limit_and_offset_resp.get("items")))
        self.assertEqual(4, limit_and_offset_resp.get("count"))
        self.assertEqual(2, limit_and_offset_resp.get("limit"))
        self.assertEqual(2, limit_and_offset_resp.get("offset"))
        self.assertEqual("Ddd", limit_and_offset_resp.get("items")[1].get("title"))
        #
        limit_and_offset_resp = self.api_client.post(
            "movie.list", dict(limit=1, offset=999)
        )
        self.assertEqual(None, limit_and_offset_resp.get("error"))
        self.assertEqual(None, limit_and_offset_resp.get("items"))

    def test_delete(self):
        new_movie = self.api_client.post(
            "movie.create",
            dict(title="Matrix", year="1993", imdb_id="tt0106062", m_type="series"),
        )
        resp_unauthorized = self.api_client.post(
            "movie.delete", dict(id=new_movie.get("id"))
        )
        self.assertEqual(True, bool(resp_unauthorized.get("error")))
        self.assertEqual(
            "Unauthorized", resp_unauthorized.get("error").get("error_name")
        )
        #
        user_response = self.api_client.post(
            "user.create", dict(email="test@gmail.com", password="test")
        )
        access_token = user_response.get("access_token")
        resp = self.api_client.post(
            "movie.delete",
            dict(id=new_movie.get("id")),
            headers=dict(authorization=access_token),
        )
        self.assertEqual(None, resp.get("error"))
