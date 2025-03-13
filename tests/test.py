import unittest
from unittest.mock import patch, MagicMock
from hubs.cloudant_client import CloudantClient
from hubs.app import App

class TestCloudantClient(unittest.TestCase):

    @patch('hubs.cloudant_client.CloudantV1')
    def setUp(self, MockCloudantV1):
        self.mock_client = MockCloudantV1.return_value
        self.cloudant_client = CloudantClient('https://fakeurl.com', 'fakedb')

    def test_get_full_response_post_search_no_rows(self):
        self.mock_client.post_search.return_value.get_result.return_value = {"rows": []}
        response = self.cloudant_client.get_full_response_post_search('fakedb', 'ddoc', 'index', 'query')
        self.assertEqual(response, {"rows": []})

    def test_get_full_response_post_search_with_rows(self):
        self.mock_client.post_search.return_value.get_result.side_effect = [
            {"rows": [{"id": "1"}], "bookmark": "bookmark1"},
            {"rows": [{"id": "2"}], "bookmark": "bookmark2"},
            {"rows": []}
        ]
        response = self.cloudant_client.get_full_response_post_search('fakedb', 'ddoc', 'index', 'query')
        self.assertEqual(len(response["rows"]), 2)

class TestApp(unittest.TestCase):

    @patch('hubs.app.CloudantClient')
    def setUp(self, MockCloudantClient):
        self.mock_client = MockCloudantClient.return_value
        self.app = App(self.mock_client, 40.7128, -74.0060, 10)

    @patch('hubs.app.Utils.calculate_bounding_box_from_inputs')
    def test_run_no_hubs_found(self, mock_calculate_bounding_box):
        mock_calculate_bounding_box.return_value = [40.0, 41.0, -75.0, -73.0]
        self.mock_client.get_full_response_post_search.return_value = {"rows": []}
        with patch('builtins.print') as mocked_print:
            self.app.run()
            mocked_print.assert_called_with("No hubs found in the given distance")

    @patch('hubs.app.Utils.calculate_bounding_box_from_inputs')
    @patch('hubs.app.Utils.calculate_distance_from_coordinates', return_value=5.0)
    def test_run_hubs_found(self, mock_calculate_distance, mock_calculate_bounding_box):
        mock_calculate_bounding_box.return_value = [40.0, 41.0, -75.0, -73.0]
        self.mock_client.get_full_response_post_search.return_value = {
            "rows": [
                {"fields": {"name": "Hub1", "lat": 40.5, "lon": -74.5}},
                {"fields": {"name": "Hub2", "lat": 40.6, "lon": -74.6}}
            ]
        }
        with patch('builtins.print') as mocked_print:
            self.app.run()
            mocked_print.assert_any_call(f'Hubs within {self.app.dist} km:')
            mocked_print.assert_any_call('"Hub1", distance: 5.0 km')
            mocked_print.assert_any_call('"Hub2", distance: 5.0 km')

if __name__ == '__main__':
    unittest.main()
