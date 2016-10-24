# coding=utf-8

import unittest
from util.tool.url_tool import make_url, url_subtract_query
from urllib.parse import urlparse, parse_qs


class TestUrlTool(unittest.TestCase):
    PATH = "http://path/to/test"

    def test_base_case(self):
        out = make_url(self.PATH, {"arg1": "v1", "arg2": "v2"})
        parsed_qs = parse_qs(urlparse(out).query)
        self.assertDictEqual(parsed_qs, {"arg1": ["v1"], "arg2": ["v2"]})

    def test_escape(self):
        out = make_url(self.PATH, {'_xsrf': 'abcs'}, escape=['arg2'])
        self.assertNotIn('arg2', out)
        self.assertNotIn('_xsrf', out)

    def test_default_escape(self):
        out = make_url(self.PATH, {"code": "123"})
        self.assertNotIn('code=123', out)

    def test_tail_question_mark(self):
        out = make_url(self.PATH, {})
        self.assertNotIn('?', out)

    def test_path_format(self):
        try:
            make_url(self.PATH + "?abc=def", {})
        except ValueError as e:
            self.assertEqual(str(e), "Path should not contain '?'")

    def test_urlencod(self):
        out = make_url(self.PATH, {"chinese": "我是中文"})
        self.assertEqual(out, "http://path/to/test?chinese=%E6%88%91%E6%98%AF%E4%B8%AD%E6%96%87")

    def test_kwargs(self):
        out = make_url(self.PATH, {"arg1": "v1", "arg2": "v2"}, arg3="v3")
        parsed_qs = parse_qs(urlparse(out).query)
        self.assertDictEqual(parsed_qs, {"arg1": ["v1"], "arg2": ["v2"], "arg3": ["v3"]})

    def test_url_subtract_query(self):
        origin = "http://path/to/test?arg1=v1&arg2=v2&code=code123&status=st"
        out = url_subtract_query(origin, ['code', 'status'])
        parsed_qs = parse_qs(urlparse(out).query)
        self.assertNotIn('code', parsed_qs)
        self.assertNotIn('status', parsed_qs)

if __name__ == "__main__":
    unittest.TestLoader().loadTestsFromTestCase(TestUrlTool).run()
