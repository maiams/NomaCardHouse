from django.test import TestCase
from rest_framework.test import APIClient


class ApiRootTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_root_returns_useful_links(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertTrue(payload.get("success"))

        data = payload.get("data", {})
        endpoints = data.get("endpoints", {})

        self.assertEqual(data.get("name"), "Noma Card House API")
        self.assertTrue(data.get("api_base", "").endswith("/api/v1/"))
        self.assertTrue(data.get("admin", "").endswith("/admin/"))

        self.assertIn("products", endpoints)
        self.assertTrue(endpoints["products"].endswith("/api/v1/products/"))
        self.assertIn("cart", endpoints)
        self.assertTrue(endpoints["cart"].endswith("/api/v1/cart/"))
        self.assertIn("orders", endpoints)
        self.assertIn("payments_webhook", endpoints)
