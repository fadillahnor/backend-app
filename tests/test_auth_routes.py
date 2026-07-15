import unittest

from app import create_app


class AuthRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()

    def test_me_options_returns_success_without_jwt(self):
        response = self.client.options('/me', headers={
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {})


if __name__ == '__main__':
    unittest.main()
