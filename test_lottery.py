import unittest
import requests
import json
from app import app, process_lottery_data, format_lottery_number

class TestLotteryFunctionality(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
    def test_powerball_api(self):
        """Test if Powerball API is accessible and returns valid data"""
        url = "https://data.ny.gov/resource/d6yy-54nr.json"
        params = {"$limit": 1, "$order": "draw_date DESC"}
        
        response = requests.get(url, params=params)
        self.assertEqual(response.status_code, 200, "Powerball API should be accessible")
        
        data = response.json()
        self.assertTrue(len(data) > 0, "Powerball API should return data")
        self.assertTrue('winning_numbers' in data[0], "Data should contain winning numbers")
        
        # Test data format
        winning_numbers = data[0].get('winning_numbers', '').split()
        self.assertEqual(len(winning_numbers), 6, "Should have 6 numbers (5 main + 1 powerball)")
        
    def test_mega_millions_api(self):
        """Test if Mega Millions API is accessible and returns valid data"""
        url = "https://data.ny.gov/resource/5xaw-6ayf.json"
        params = {"$limit": 1, "$order": "draw_date DESC"}
        
        response = requests.get(url, params=params)
        self.assertEqual(response.status_code, 200, "Mega Millions API should be accessible")
        
        data = response.json()
        self.assertTrue(len(data) > 0, "Mega Millions API should return data")
        self.assertTrue('winning_numbers' in data[0], "Data should contain winning numbers")
        self.assertTrue('mega_ball' in data[0], "Data should contain mega ball")
        
        # Test data format
        winning_numbers = data[0].get('winning_numbers', '').split()
        mega_ball = data[0].get('mega_ball')
        self.assertEqual(len(winning_numbers), 5, "Should have 5 main numbers")
        self.assertIsNotNone(mega_ball, "Should have a mega ball number")

    def test_latest_lottery_endpoint(self):
        """Test our /api/lottery/latest endpoint"""
        response = self.app.get('/api/lottery/latest')
        self.assertEqual(response.status_code, 200, "Endpoint should be accessible")
        
        data = json.loads(response.data)
        self.assertTrue('powerball' in data, "Response should contain powerball data")
        self.assertTrue('mega_millions' in data, "Response should contain mega millions data")
        
        # Test Powerball data structure
        pb_data = data['powerball']
        self.assertTrue('winning_numbers' in pb_data, "Powerball data should contain winning numbers")
        self.assertTrue('powerball' in pb_data, "Powerball data should contain powerball number")
        self.assertTrue('draw_date' in pb_data, "Powerball data should contain draw date")
        
        # Test Mega Millions data structure
        mm_data = data['mega_millions']
        self.assertTrue('winning_numbers' in mm_data, "Mega Millions data should contain winning numbers")
        self.assertTrue('mega_ball' in mm_data, "Mega Millions data should contain mega ball")
        self.assertTrue('draw_date' in mm_data, "Mega Millions data should contain draw date")

    def test_process_lottery_data(self):
        """Test lottery data processing function"""
        # Test Powerball processing
        test_pb_data = [{
            'winning_numbers': '1 2 3 4 5 6',
            'draw_date': '2024-01-01T00:00:00',
            'multiplier': '2'
        }]
        
        processed_pb = process_lottery_data(test_pb_data, 'powerball')
        self.assertEqual(len(processed_pb), 1, "Should process one record")
        self.assertEqual(len(processed_pb[0]['winning_numbers']), 5, "Should have 5 main numbers")
        self.assertEqual(processed_pb[0]['powerball'], '06', "Should format powerball number")
        
        # Test Mega Millions processing
        test_mm_data = [{
            'winning_numbers': '10 20 30 40 50',
            'mega_ball': '15',
            'draw_date': '2024-01-01T00:00:00',
            'multiplier': '3'
        }]
        
        processed_mm = process_lottery_data(test_mm_data, 'mega_millions')
        self.assertEqual(len(processed_mm), 1, "Should process one record")
        self.assertEqual(len(processed_mm[0]['winning_numbers']), 5, "Should have 5 main numbers")
        self.assertEqual(processed_mm[0]['mega_ball'], '15', "Should format mega ball number")

    def test_number_formatting(self):
        """Test lottery number formatting function"""
        self.assertEqual(format_lottery_number('1'), '01', "Should pad single digit with zero")
        self.assertEqual(format_lottery_number('10'), '10', "Should not pad double digits")
        self.assertEqual(format_lottery_number(None), None, "Should handle None value")
        self.assertEqual(format_lottery_number(''), '', "Should handle empty string")

if __name__ == '__main__':
    unittest.main()
