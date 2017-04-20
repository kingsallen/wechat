# coding=utf-8

import unittest
import weakref
from datetime import datetime, timedelta


class Bucket(object):
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self.max_quota = 0
        self.quota_consumed = 0

    def __repr__(self):
        return "Bucket(max_quota=%d,quota_sonsumed=%d)" % (
            self.max_quota, self.quota_consumed)

    @property
    def quota(self):
        return self.max_quota - self.quota_consumed

    @quota.setter
    def quota(self, amount):
        delta = self.max_quota - amount
        if amount == 0:
            self.quota_consumed = 0
            self.max_quota = 0
        elif delta < 0:
            assert self.quota_consumed == 0
            self.max_quota = amount
        else:
            assert self.max_quota >= self.quota_consumed
            self.quota_consumed += delta


def fill(bucket, amount):
    now = datetime.now()
    if now - bucket.reset_time > bucket.period_delta:
        bucket.quota = 0
        bucket.reset_time = now
    bucket.quota += amount


def deduct(bucket, amount):
    now = datetime.now()
    if now - bucket.reset_time > bucket.period_delta:
        return False
    if bucket.quota - amount < 0:
        return False
    bucket.quota -= amount
    return True


class Grade(object):
    def __init__(self):
        self._values = weakref.WeakKeyDictionary()

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return self._values.get(instance, 0)

    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError('Grade must be between 0 and 100')
        self._values[instance] = value


class Exam(object):
    math_grade = Grade()
    writing_grade = Grade()
    science_grade = Grade()


class LazyDB(object):
    def __init__(self):
        self.exists = 5

    def __getattr__(self, name):
        value = 'Value for %s' % name
        setattr(self, name, value)
        return value


class ValidatingDB(object):
    def __init__(self):
        self.exists = 5

    def __getattribute__(self, name):
        print('Called __get_attribute__(%s)' % name)
        try:
            return super().__getattribute__(name)
        except AttributeError:
            value = 'Value for %s' % name
            setattr(self, name, value)
            return value


class LoggingLazyDB(LazyDB):
    def __getattr__(self, name):
        print('Called __getattr__(%s)' % name)
        return super().__getattr__(name)


class BrokenDictionaryDB(object):
    def __init__(self, data):
        self._data = data

    def __getattribute__(self, item):
        print('Called __getattribute__(%s)' % item)
        data_dict = super().__getattribute__('_data')
        return data_dict[item]


class Meta(type):
    def __new__(meta, name, bases, class_dict):
        print((meta, name, bases, class_dict))
        return type.__new__(meta, name, bases, class_dict)


class MyClass(object, metaclass=Meta):
    stuff = 123

    def foo(self):
        pass


class ValidatePolygon(type):
    def __new__(cls, name, bases, class_dict):
        if bases != (object,):
            if class_dict['sides'] < 3:
                raise ValueError('Polygons need 3+ sides')
        return type.__new__(cls, name, bases, class_dict)


class Polygon(object, metaclass=ValidatePolygon):
    sides = None

    @classmethod
    def interior_angles(cls):
        return (cls.sides - 2) * 180


class Triangle(Polygon):
    sides = 3


class PlayGroundTestCase(unittest.TestCase):
    def test_descriptor(self):
        first_exam = Exam()
        first_exam.writing_grade = 82
        first_exam.science_grade = 99
        self.assertEqual(first_exam.writing_grade, 82)
        self.assertEqual(first_exam.science_grade, 99)

        second_exam = Exam()
        second_exam.writing_grade = 75
        self.assertEqual(second_exam.writing_grade, 75)
        self.assertEqual(first_exam.writing_grade, 82)

    def test_getattr(self):
        data = LoggingLazyDB()
        print('exists:', data.exists)
        print('foo:   ', data.foo)
        print('foo:   ', data.foo)

        data = LoggingLazyDB()
        print('Before:     ', data.__dict__)
        print('foo exists: ', hasattr(data, 'foo'))
        print('After:      ', data.__dict__)
        print('foo exists: ', hasattr(data, 'foo'))

    def test_getattribute(self):
        data = ValidatingDB()
        print('exists:', data.exists)
        print('foo: ', data.foo)
        print('foo: ', data.foo)

        data = BrokenDictionaryDB({'foo': 3})
        data.foo


if __name__ == '__main__':
    unittest.main()
