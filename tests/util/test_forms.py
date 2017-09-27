# coding=utf-8

from schematics.exceptions import ValidationError, DataError
from model.user import InterestCurrentInfoForm

from unittest import TestCase


class FormTestCases(TestCase):

    def test_interest_current_info_form(self):
        form = InterestCurrentInfoForm({
            'name':     '1',
            'company':  '2',
            'position': '3',
            'start':    '4'
        })
        with self.assertRaises(DataError):
            form.validate()

        form = InterestCurrentInfoForm({
            'name':     '1',
            'company':  '2',
            'position': '3',
            'start':    '2017-01-01'
        })

        assert form.validate() is None
