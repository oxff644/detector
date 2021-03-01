import unittest

from task import feishu, mail_to


class test_normal(unittest.TestCase):
    def test_feishu(self):
        assert feishu.delay("test msg")

    def test_mail_to(self):
        assert mail_to.delay("test msg")
