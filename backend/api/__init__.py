from pkgutil import walk_packages, extend_path

from backend import wsgi


class Application(wsgi.Application):
    pass


application = Application(base_path="api")
service = application.service
endpoint = application.service

for _, modname, _ in walk_packages(
    path=extend_path(__path__, __name__), prefix=__name__ + "."
):
    __import__(modname)
