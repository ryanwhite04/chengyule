from .admin import Cli as Admin
from .languages import Cli as Languages

admin = Admin()
languages = Languages()

class Cli:

    def init_app(self, app, db):
        admin.init_app(app, db)
        languages.init_app(app, db)
