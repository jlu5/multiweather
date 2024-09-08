#!/usr/bin/env python3
"""Tests for data types"""
import unittest

from multiweather.data import (
    make_distance,
    make_temperature,
    Temperature,
    Distance,
    Speed
)

# pylint: disable=missing-function-docstring

class TestDataTypes(unittest.TestCase):
    """Test that data types with builtin unit conversions behave correctly"""
    def test_temperature(self):
        temp1 = Temperature(c=20)
        self.assertEqual(temp1.c, 20)
        self.assertEqual(temp1.f, 68)

        temp2 = Temperature(f=80)
        self.assertEqual(temp2.f, 80)
        self.assertEqual(temp2.c, 26.666666666666667)

        # zero values should be accepted
        Temperature(c=0)
        Temperature(f=0)

        with self.assertRaises(ValueError):
            Temperature(c=10, f=10)

        # Test comparison and convenience funcs
        self.assertEqual(temp1, make_temperature(c=20))
        self.assertEqual(temp1, make_temperature(f=68))
        self.assertEqual(temp2, make_temperature(f=80))
        self.assertIsNone(make_temperature())

    def test_distance(self):
        dist1 = Distance(km=100)
        self.assertEqual(dist1.km, 100)
        self.assertEqual(dist1.mi, 100/1.609)

        dist2 = Distance(mi=200)
        self.assertEqual(dist2.km, 200*1.609)
        self.assertEqual(dist2.mi, 200)

        Distance(km=0)
        Distance(mi=0)

        with self.assertRaises(ValueError):
            Distance(km=1, mi=1)

        # Test comparison and convenience funcs
        self.assertEqual(dist1, make_distance(km=100))
        self.assertEqual(dist2, make_distance(mi=200))
        self.assertIsNone(make_distance())

    def test_speed(self):
        speed1 = Speed(kph=100)
        self.assertEqual(speed1.kph, 100)
        self.assertEqual(speed1.mph, 100/1.609)
        self.assertEqual(speed1.ms, 100/3.6)

        speed2 = Speed(mph=200)
        self.assertEqual(speed2.kph, 200*1.609)
        self.assertEqual(speed2.mph, 200)
        self.assertEqual(speed2.ms, speed2.kph/3.6)

        speed3 = Speed(ms=360)
        self.assertEqual(speed3.ms, 360)
        self.assertEqual(speed3.kph, 1296)
        self.assertEqual(speed3.mph, 1296/1.609)

        Speed(kph=0)
        Speed(mph=0)
        Speed(ms=0)

        with self.assertRaises(ValueError):
            Speed(kph=1, mph=2)
        with self.assertRaises(ValueError):
            Speed(kph=1, ms=2)
        with self.assertRaises(ValueError):
            Speed(mph=1, ms=2)
        with self.assertRaises(ValueError):
            Speed(kph=1, mph=2, ms=3)

        self.assertEqual(speed1, Speed(kph=100))

if __name__ == '__main__':
    unittest.main()
