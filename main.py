import os
import jinja2
import webapp2
from google.appengine.ext import ndb


class Movie(ndb.Model):
    title = ndb.StringProperty()
    director = ndb.StringProperty()
    actors = ndb.StringProperty()
    synopsis = ndb.TextProperty()
    rating = ndb.FloatProperty()
    ratings = ndb.IntegerProperty(repeated=True)
    picture = ndb.StringProperty()



template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        movies = Movie.query().fetch()
        params = {"movies": movies}
        return self.render_template("movie_list.html", params=params)


class RatingMovieHandler(BaseHandler):
    def post(self, movie_id):
        rating = self.request.get("rating")

        movie = Movie.get_by_id(int(movie_id))
        movie.ratings.append(int(rating))
        movie.rating = sum(movie.ratings) / float(len(movie.ratings))
        movie.put()
        return self.redirect_to("list")


class AddMovieHandler(BaseHandler):
    def get(self):
        return self.render_template("hello.html")

    def post(self):
        title = self.request.get("title")
        director = self.request.get("director")
        actors = self.request.get("actors")
        synopsis = self.request.get("synopsis")
        rating = float(self.request.get("rating"))
        picture = self.request.get("picture")

        movie = Movie(title=title, director=director, actors=actors, synopsis=synopsis, rating=rating, picture=picture)
        movie.put()
        movies = Movie.query().fetch()
        params = {"movies": movies}
        return self.render_template("movie_list.html", params=params)

app = webapp2.WSGIApplication([
    webapp2.Route('/movie_list', MainHandler, name="list"),
    webapp2.Route('/movie_list/add', AddMovieHandler),
    webapp2.Route("/movie_list/<movie_id:\d+>/rate", RatingMovieHandler)
], debug=True)
# movie_list
