from test import Case, db, main
from app.views import url_for

class ViewCase(Case):

    def setUp(self):
        super().setUp()
        self.app_context = self.app.test_request_context()                      
        self.app_context.push() 
        self.client = self.app.test_client()

    def test_translation(self):
        words = ["你好", "一"]
        self.assertEqual(
            self.client.get(url_for("translation", words=words)).json,
            ["Hello", "one"],
        )

if __name__ == "__main__": main()
