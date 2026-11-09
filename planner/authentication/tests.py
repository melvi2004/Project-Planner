from io import StringIO

from django.contrib.auth.hashers import check_password
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from .models import Profile, RoleChoices, TechChoices


class SeedProfilesCommandTests(TestCase):
    def test_creates_expected_profiles_and_prints_credentials(self):
        output = StringIO()
        call_command("seed_profiles", stdout=output)

        profiles = Profile.objects.order_by("username")
        self.assertEqual(profiles.count(), 17)
        self.assertEqual(
            profiles.filter(role=RoleChoices.PROJECT_COORDINATOR).count(), 2
        )
        self.assertEqual(profiles.filter(role=RoleChoices.USER).count(), 15)

        for profile in profiles:
            self.assertTrue(profile.first_name)
            self.assertTrue(profile.last_name)
            self.assertRegex(
                profile.email,
                r"^[a-z]+[0-9]{4}@mailinator\.com$",
            )
            self.assertTrue(profile.has_usable_password())
            self.assertNotEqual(profile.password, "password")
            if profile.role == RoleChoices.USER:
                self.assertIn(profile.tech, TechChoices.values)
            else:
                self.assertIsNone(profile.tech)

        output_lines = output.getvalue().splitlines()
        self.assertEqual(len(output_lines), 19)
        self.assertEqual(
            "username,password,name,email,role,tech", output_lines[0]
        )
        for line in output_lines[1:18]:
            username, password, *_ = line.split(",")
            profile = Profile.objects.get(username=username)
            self.assertTrue(check_password(password, profile.password))
        self.assertIn("Created 17 profiles.", output_lines[-1])

    def test_existing_username_prevents_partial_duplicate_creation(self):
        Profile.objects.create_user(
            username="olivia.bennett",
            password="existing-password",
            role=RoleChoices.PROJECT_COORDINATOR,
        )

        with self.assertRaisesMessage(CommandError, "olivia.bennett"):
            call_command("seed_profiles", stdout=StringIO())

        self.assertEqual(Profile.objects.count(), 1)
