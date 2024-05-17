from django.contrib.admin.sites import AdminSite
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from taxi.admin import DriverAdmin, CarAdmin
from taxi.models import Driver, Car, Manufacturer


class MockSuperUser:
    def has_perm(self, perm):
        return True


class AdminTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin", email="admin@admin.com", password="admin"
        )
        self.site = AdminSite()

        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.user = self.user

        self.driver = Driver.objects.create(
            username="driver1",
            email="driver1@example.com",
            password="password1",
            license_number="ABC12345",
        )
        self.car = Car.objects.create(
            model="Toyota Corolla",
            manufacturer=Manufacturer.objects.create(name="Toyota", country="Japan"),
        )

    def test_driver_admin_list_display(self):
        ma = DriverAdmin(Driver, self.site)
        self.assertTrue("license_number" in ma.list_display)

    def test_driver_admin_fieldsets(self):
        ma = DriverAdmin(Driver, self.site)
        form = ma.get_form(self.request, self.driver)
        # Create a form instance to check fields included in the form
        form_instance = form(instance=self.driver)
        self.assertIn("license_number", form_instance.fields)

    def test_car_admin_search_fields(self):
        ma = CarAdmin(Car, self.site)
        self.assertTrue("model" in ma.search_fields)

    def test_car_admin_list_filter(self):
        ma = CarAdmin(Car, self.site)
        self.assertTrue("manufacturer" in ma.list_filter)

    def test_manufacturer_registered(self):
        self.client.login(username="admin", email="admin@admin.com", password="admin")
        response = self.client.get("/admin/taxi/manufacturer/")
        self.assertEqual(response.status_code, 200)

    def test_admin_login_and_access_driver_page(self):
        # Test that admin can log in and access the driver admin page
        self.client.login(username="admin", password="admin")
        url = f"/admin/taxi/driver/{self.driver.id}/change/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
