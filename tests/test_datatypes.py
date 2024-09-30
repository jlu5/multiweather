#!/usr/bin/env python3
"""Tests for data types"""
import unittest

from multiweather.data import (
    Direction,
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
        self.assertEqual(temp1.format(), "20.0C / 68.0F")
        self.assertEqual(temp1.format("${c}°C"), "20.0°C")

        temp2 = Temperature(f=80)
        self.assertEqual(temp2.f, 80)
        self.assertEqual(temp2.c, 26.666666666666667)
        self.assertTrue(temp2)
        self.assertEqual(temp2.format(decimal_places=2), "26.67C / 80.00F")

        temp_null = Temperature()
        self.assertFalse(temp_null)
        self.assertEqual(temp_null.format(), "<null>")

        # zero values should be accepted
        temp3 = Temperature(c=0)
        self.assertTrue(temp3)
        self.assertEqual(temp3.format(), "0.0C / 32.0F")
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
        self.assertEqual(dist1.format(), "100.0km / 62.2mi")

        dist2 = Distance(mi=200)
        self.assertEqual(dist2.km, 200*1.609)
        self.assertEqual(dist2.mi, 200)
        self.assertTrue(dist2)
        self.assertEqual(dist2.format(), "321.8km / 200.0mi")

        dist3 = Distance(km=0)
        dist4 = Distance(mi=0)
        self.assertTrue(dist3)
        self.assertTrue(dist4)
        self.assertEqual(dist3, dist4)
        self.assertEqual(dist3.format(), "0.0km / 0.0mi")

        dist_null = Distance()
        self.assertFalse(dist_null)
        self.assertEqual(dist_null.format(), "<null>")

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
        self.assertEqual(speed1.format(), "100.0kph / 62.2mph / 27.8m/s")

        speed2 = Speed(mph=200)
        self.assertEqual(speed2.kph, 200*1.609)
        self.assertEqual(speed2.mph, 200)
        self.assertEqual(speed2.ms, speed2.kph/3.6)
        self.assertTrue(speed2)
        self.assertEqual(speed2.format(), "321.8kph / 200.0mph / 89.4m/s")

        speed3 = Speed(ms=360)
        self.assertEqual(speed3.ms, 360)
        self.assertEqual(speed3.kph, 1296)
        self.assertEqual(speed3.mph, 1296/1.609)
        self.assertTrue(speed3)

        speed4 = Speed(kph=0)
        self.assertTrue(speed4)
        self.assertEqual(speed4.format(), "0.0kph / 0.0mph / 0.0m/s")

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
        self.assertEqual(speed_null.format(), "<null>")

    def test_precipitation(self):
        precip1 = Precipitation(80, mm=50.8)
        self.assertTrue(precip1)
        self.assertEqual(precip1.mm, 50.8)
        self.assertEqual(precip1.inches, 2)
        self.assertEqual(precip1, Precipitation(80, inches=2))
        self.assertEqual(precip1.format(), "50.8mm / 2.0in (80.0%)")

        precip2 = Precipitation(55.5, inches=1)
        self.assertTrue(precip2)
        self.assertEqual(precip2.mm, 25.4)
        self.assertEqual(precip2.inches, 1)
        self.assertEqual(precip2.format(), "25.4mm / 1.0in (55.5%)")

        precip3 = Precipitation(None, inches=1)
        self.assertTrue(precip3)
        self.assertNotEqual(precip2, precip3)
        self.assertEqual(precip3.format(), "25.4mm / 1.0in")

        precip_null = Precipitation()
        self.assertFalse(precip_null)
        self.assertEqual(precip_null.format(), "<null>")

    def test_direction(self):
        dir1 = Direction(0)
        self.assertTrue(dir1)
        self.assertEqual(dir1.direction, "N")
        self.assertEqual(dir1.format(), "N")
        self.assertEqual(dir1, Direction(0))
        self.assertEqual(dir1, Direction(360))
        self.assertEqual(dir1, Direction(-360))

        # Same display direction but different angle value
        dir2 = Direction(5)
        self.assertEqual(dir2.direction, "N")
        self.assertEqual(dir2.format(), "N")
        self.assertNotEqual(dir1, dir2)
        self.assertEqual(dir2, Direction(360*2+5))  # auto normalize

        # Default constructor points to north (0 deg)
        dir_null = Direction()
        self.assertEqual(dir_null.format(), "N")
        self.assertTrue(dir_null)

        # Test rounding to the nearest direction
        self.assertEqual(Direction(22.5).direction, "NNE")
        self.assertEqual(Direction(22.5+11.2).direction, "NNE")
        self.assertEqual(Direction(22.5+11.3).direction, "NE")

        self.assertEqual(Direction(45).direction, "NE")
        self.assertEqual(Direction(45+11.2).direction, "NE")
        self.assertEqual(Direction(45+11.3).direction, "ENE")

        self.assertEqual(Direction(67.5).direction, "ENE")
        self.assertEqual(Direction(67.5+11.2).direction, "ENE")
        self.assertEqual(Direction(67.5+11.3).direction, "E")

        self.assertEqual(Direction(90).direction, "E")
        self.assertEqual(Direction(90+11.2).direction, "E")
        self.assertEqual(Direction(90+11.3).direction, "ESE")

        self.assertEqual(Direction(180).direction, "S")
        self.assertEqual(Direction(180+11.2).direction, "S")
        self.assertEqual(Direction(180+11.3).direction, "SSW")

        self.assertEqual(Direction(225).direction, "SW")
        self.assertEqual(Direction(225+11.2).direction, "SW")
        self.assertEqual(Direction(225+11.3).direction, "WSW")

        self.assertEqual(Direction(270).direction, "W")
        self.assertEqual(Direction(270+11.2).direction, "W")
        self.assertEqual(Direction(270+11.3).direction, "WNW")

        self.assertEqual(Direction(359).direction, "N")

if __name__ == '__main__':
    unittest.main()
