from test import Case, db, main, skipUnless, skipIf, TestConfig
from app.views import url_for, translate

class ViewCase(Case):

    def setUp(self):
        super().setUp()
        self.app_context = self.app.test_request_context()                      
        self.app_context.push() 
        self.client = self.app.test_client()

    @skipUnless(TestConfig.TRANSLATION_KEY, "Only works when key provided")
    def test_translate_actual(self):
        words = ["你好", "一"]
        self.assertEqual(
            self.client.get(url_for("translation", words=words)).json,
            ["Hello", "one"],
        )

    @skipIf(TestConfig.TRANSLATION_KEY, "If key provided, will run actual test")
    def test_translat_dummy(self):
        self.assertSequenceEqual(
            translate(["你好", "一"], None, "en"),
            ["en_你好", "en_一"]
        )

if __name__ == "__main__": main()

