#!/usr/bin/env python3
"""Tests for data types"""
import unittest

from multiweather.data import (
    Distance,
    Precipitation,
    Speed,
    Temperature,
)

# pylint: disable=missing-function-docstring

class TestDataTypes(unittest.TestCase):
    """Test that data types with builtin unit conversions behave correctly"""
    def test_temperature(self):
        temp1 = Temperature(c=20)
        self.assertEqual(temp1.c, 20)
        self.assertEqual(temp1.f, 68)
        self.assertTrue(temp1)

        temp2 = Temperature(f=80)
        self.assertEqual(temp2.f, 80)
        self.assertEqual(temp2.c, 26.666666666666667)
        self.assertTrue(temp2)

        temp_null = Temperature()
        self.assertFalse(temp_null)

        # zero values should be accepted
        temp3 = Temperature(c=0)
        self.assertTrue(temp3)
        temp4 = Temperature(f=0)
        self.assertTrue(temp4)

        with self.assertRaises(ValueError):
            Temperature(c=10, f=10)

        # Test comparison
        self.assertEqual(temp1, Temperature(c=20))
        self.assertEqual(temp1, Temperature(f=68))
        self.assertEqual(temp2, Temperature(f=80))

    def test_distance(self):
        dist1 = Distance(km=100)
        self.assertEqual(dist1.km, 100)
        self.assertEqual(dist1.mi, 100/1.609)
        self.assertTrue(dist1)

        dist2 = Distance(mi=200)
        self.assertEqual(dist2.km, 200*1.609)
        self.assertEqual(dist2.mi, 200)
        self.assertTrue(dist2)

        dist3 = Distance(km=0)
        dist4 = Distance(mi=0)
        self.assertTrue(dist3)
        self.assertTrue(dist4)

        dist_null = Distance()
        self.assertFalse(dist_null)

        with self.assertRaises(ValueError):
            Distance(km=1, mi=1)

        # Test comparison and convenience funcs
        self.assertEqual(dist1, Distance(km=100))
        self.assertEqual(dist2, Distance(mi=200))

    def test_speed(self):
        speed1 = Speed(kph=100)
        self.assertEqual(speed1.kph, 100)
        self.assertEqual(speed1.mph, 100/1.609)
        self.assertEqual(speed1.ms, 100/3.6)
        self.assertTrue(speed1)

        speed2 = Speed(mph=200)
        self.assertEqual(speed2.kph, 200*1.609)
        self.assertEqual(speed2.mph, 200)
        self.assertEqual(speed2.ms, speed2.kph/3.6)
        self.assertTrue(speed2)

        speed3 = Speed(ms=360)
        self.assertEqual(speed3.ms, 360)
        self.assertEqual(speed3.kph, 1296)
        self.assertEqual(speed3.mph, 1296/1.609)
        self.assertTrue(speed3)

        speed4 = Speed(kph=0)
        self.assertTrue(speed4)

        with self.assertRaises(ValueError):
            Speed(kph=1, mph=2)
        with self.assertRaises(ValueError):
            Speed(kph=1, ms=2)
        with self.assertRaises(ValueError):
            Speed(mph=1, ms=2)
        with self.assertRaises(ValueError):
            Speed(kph=1, mph=2, ms=3)

        # Test comparisons
        self.assertEqual(speed1, Speed(kph=100))
        self.assertNotEqual(speed1, Speed(mph=100))

        speed_null = Speed()
        self.assertFalse(speed_null)

    def test_precipitation(self):
        precip1 = Precipitation(0.8, mm=50.8)
        self.assertTrue(precip1)
        self.assertEqual(precip1.mm, 50.8)
        self.assertEqual(precip1.inches, 2)
        self.assertEqual(precip1, Precipitation(0.8, inches=2))

        precip2 = Precipitation(0.5, inches=1)
        self.assertTrue(precip2)
        self.assertEqual(precip2.mm, 25.4)
        self.assertEqual(precip2.inches, 1)

        precip3 = Precipitation(None, inches=1)
        self.assertTrue(precip2)
        self.assertNotEqual(precip2, precip3)

        precip_null = Precipitation()
        self.assertFalse(precip_null)

if __name__ == '__main__':
    unittest.main()
