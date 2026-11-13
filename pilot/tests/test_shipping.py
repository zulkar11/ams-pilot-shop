import unittest

from shop.shipping import quote


class QuoteTest(unittest.TestCase):
    def test_a_us_order_pays_the_us_rate(self):
        self.assertEqual(quote({"country": "US", "weight_kg": 1, "subtotal": 20}), 5.00)

    def test_a_large_us_order_ships_free(self):
        self.assertEqual(quote({"country": "us", "weight_kg": 3, "subtotal": 150}), 0.0)

    def test_each_extra_kilogram_adds_to_the_rate(self):
        self.assertEqual(quote({"country": "GB", "weight_kg": 3, "subtotal": 20}), 12.00)

    def test_a_country_without_its_own_rate_pays_the_international_rate(self):
        self.assertEqual(quote({"country": "NZ", "weight_kg": 2, "subtotal": 40}), 16.50)
        self.assertEqual(quote({"country": "au", "weight_kg": 1, "subtotal": 40}), 15.00)


if __name__ == "__main__":
    unittest.main()
