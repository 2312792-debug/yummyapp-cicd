import unittest
from unittest.mock import patch

from yummy_app import YummyApp
import gps_service


# ================================================================
# CAP DO 1: Bo test co ban cho san (Moi chi dat ~35% Coverage)
# ================================================================
class TestEasyLevel(unittest.TestCase):
    """Kiem thu chuc nang co ban tinh tien don hang"""

    def setUp(self):
        self.app = YummyApp()

    def test_calculate_total_for_single_item(self):
        cart = {"pho": 2}
        self.assertEqual(self.app.calculate_order_total(cart), 100000)

    def test_calculate_total_for_multiple_items(self):
        cart = {"pho": 1, "bun": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 95000)

    def test_calculate_total_for_empty_cart(self):
        self.assertEqual(self.app.calculate_order_total({}), 0.0)

    def test_calculate_total_with_zero_quantity(self):
        cart = {"pho": 0}
        self.assertEqual(self.app.calculate_order_total(cart), 0.0)


# ================================================================
# CAP DO 2: Kiem thu apply_promo_code (mang, ma KM, phien ban OS)
# ================================================================
class TestMediumLevel(unittest.TestCase):
    """Kiem thu chuc nang ap dung ma khuyen mai"""

    def setUp(self):
        self.app = YummyApp(os_version=16)

    def test_apply_valid_promo_code_giam10(self):
        """Ma GIAM10 giam 10% tong don hang"""
        result = self.app.apply_promo_code(100000, "GIAM10")
        self.assertEqual(result, 90000.0)

    def test_apply_promo_code_offline_raises_connection_error(self):
        """Khong co mang phai raise ConnectionError"""
        app_offline = YummyApp(network_status="offline")
        with self.assertRaises(ConnectionError):
            app_offline.apply_promo_code(100000, "GIAM10")

    def test_apply_invalid_promo_code_raises_value_error(self):
        """Ma khong ton tai phai raise ValueError"""
        with self.assertRaises(ValueError):
            self.app.apply_promo_code(100000, "INVALID_CODE")

    def test_apply_promo_code_os_version_too_low(self):
        """Ma NEW_OS_ONLY yeu cau OS >= 15, OS=10 phai raise ValueError"""
        app_old_os = YummyApp(os_version=10)
        with self.assertRaises(ValueError):
            app_old_os.apply_promo_code(100000, "NEW_OS_ONLY")


# ================================================================
# CAP DO 3: Kiem thu GPS / mang voi Mock (kho nhat)
# ================================================================
class TestHardLevel(unittest.TestCase):
    """Kiem thu chuc nang lay danh sach nha hang voi GPS mock"""

    def setUp(self):
        self.app = YummyApp()

    @patch('gps_service.get_current_location')
    def test_get_nearby_restaurants_returns_list_on_known_location(self, mock_gps):
        """GPS tra ve toa do hop le - danh sach nha hang"""
        mock_gps.return_value = (10.0, 105.0)
        result = self.app.get_nearby_restaurants()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    @patch('gps_service.get_current_location')
    def test_get_nearby_restaurants_gps_signal_lost_returns_message(self, mock_gps):
        """GPS mat tin hieu - tra ve thong bao loi"""
        mock_gps.side_effect = gps_service.GPSSignalLostError("Mat tin hieu GPS")
        result = self.app.get_nearby_restaurants()
        self.assertEqual(result, "Khong the xac dinh vi tri.")

    @patch('gps_service.get_current_location')
    def test_get_nearby_restaurants_unknown_location_returns_empty_list(self, mock_gps):
        """GPS tra ve toa do khong co trong du lieu - danh sach rong"""
        mock_gps.return_value = (0.0, 0.0)
        result = self.app.get_nearby_restaurants()
        self.assertEqual(result, [])

    @patch('gps_service.get_current_location')
    def test_get_nearby_restaurants_correct_restaurant_names(self, mock_gps):
        """GPS tra ve toa do 10.0,105.0 - phai chua ten nha hang dung"""
        mock_gps.return_value = (10.0, 105.0)
        result = self.app.get_nearby_restaurants()
        self.assertIn("Nha hang Pho Ly Quoc Su", result)


if __name__ == '__main__':
    unittest.main()
