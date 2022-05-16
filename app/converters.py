from werkzeug.routing import BaseConverter

class ChineseListConverter(BaseConverter):

    regex = r"[\u4e00-\u9fff]+(?:,[\u4e00-\u9fff]+)*,?"

    def to_python(self, value):
        return value.split(",")

    def to_url(self, value):
        return ",".join(value)