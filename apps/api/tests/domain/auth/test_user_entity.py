from __future__ import annotations

from app.domain.auth.value_objects import Email, UserId
from app.domain.user.entities import User


class TestUserCreate:
    def test_create_sets_defaults(self):
        user = User.create(name="John", surname="Doe", email=Email("john@example.com"))

        assert user.name == "John"
        assert user.surname == "Doe"
        assert user.email.value == "john@example.com"
        assert user.email_verified is False
        assert user.is_active is True
        assert user.image is None

    def test_create_generates_unique_id(self):
        u1 = User.create(name="A", surname="B", email=Email("a@b.com"))
        u2 = User.create(name="A", surname="B", email=Email("a@b.com"))
        assert u1.id != u2.id


class TestUserFullName:
    def test_full_name(self):
        user = User.create(name="John", surname="Doe", email=Email("j@d.com"))
        assert user.full_name == "John Doe"

    def test_full_name_no_surname(self):
        user = User.create(name="John", surname="", email=Email("j@d.com"))
        assert user.full_name == "John"

    def test_full_name_no_name(self):
        user = User.create(name="", surname="Doe", email=Email("j@d.com"))
        assert user.full_name == "Doe"


class TestUserVerifyEmail:
    def test_verify_email(self):
        user = User.create(name="A", surname="B", email=Email("a@b.com"))
        assert user.email_verified is False

        user.verify_email()
        assert user.email_verified is True

    def test_verify_email_updates_timestamp(self):
        user = User.create(name="A", surname="B", email=Email("a@b.com"))
        original = user.updated_at

        user.verify_email()
        assert user.updated_at >= original


class TestUserDeactivate:
    def test_deactivate(self):
        user = User.create(name="A", surname="B", email=Email("a@b.com"))
        assert user.is_active is True

        user.deactivate()
        assert user.is_active is False

    def test_deactivate_updates_timestamp(self):
        user = User.create(name="A", surname="B", email=Email("a@b.com"))
        original = user.updated_at

        user.deactivate()
        assert user.updated_at >= original


class TestUserUpdateProfile:
    def test_update_name(self):
        user = User.create(name="Old", surname="Name", email=Email("a@b.com"))
        user.update_profile(name="New")
        assert user.name == "New"
        assert user.surname == "Name"

    def test_update_surname(self):
        user = User.create(name="A", surname="Old", email=Email("a@b.com"))
        user.update_profile(surname="New")
        assert user.surname == "New"

    def test_update_image(self):
        user = User.create(name="A", surname="B", email=Email("a@b.com"))
        user.update_profile(image="https://img.example.com/pic.jpg")
        assert user.image == "https://img.example.com/pic.jpg"

    def test_none_fields_are_not_changed(self):
        user = User.create(name="A", surname="B", email=Email("a@b.com"))
        user.update_profile()
        assert user.name == "A"
        assert user.surname == "B"


class TestUserEquality:
    def test_same_id_equal(self):
        uid = UserId.generate()
        u1 = User(id=uid, name="A", surname="B", email=Email("a@b.com"))
        u2 = User(id=uid, name="X", surname="Y", email=Email("x@y.com"))
        assert u1 == u2

    def test_different_id_not_equal(self):
        u1 = User.create(name="A", surname="B", email=Email("a@b.com"))
        u2 = User.create(name="A", surname="B", email=Email("a@b.com"))
        assert u1 != u2

    def test_not_equal_to_other_types(self):
        user = User.create(name="A", surname="B", email=Email("a@b.com"))
        assert user != "not a user"
