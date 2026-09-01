"""
Tests for the UserRepository.

These tests verify that the repository correctly handles user persistence
and retrieval operations.

Test naming convention: test_<what>_<scenario>_<expected_outcome>
"""

import pytest

from app.domain.user import User
from app.repositories.user_repository import InMemoryUserRepository


# ──────────────────────────────────────────────
#  Create User
# ──────────────────────────────────────────────


class TestCreateUser:
    """Tests for the create() method."""

    def test_create_user_stores_user(self):
        """Creating a user should store it in the repository."""
        repo = InMemoryUserRepository()
        user = User("USER-001", "Alice", "alice@example.com")

        created = repo.create(user)

        assert created is user
        assert repo.exists("USER-001")

    def test_create_multiple_users(self):
        """Repository should store multiple users."""
        repo = InMemoryUserRepository()
        user1 = User("USER-001", "Alice", "alice@example.com")
        user2 = User("USER-002", "Bob", "bob@example.com")

        repo.create(user1)
        repo.create(user2)

        assert repo.count() == 2

    def test_create_duplicate_user_raises_error(self):
        """Creating a user with duplicate ID should raise ValueError."""
        repo = InMemoryUserRepository()
        user1 = User("USER-001", "Alice", "alice@example.com")
        user2 = User("USER-001", "Bob", "bob@example.com")

        repo.create(user1)

        with pytest.raises(ValueError, match="already exists"):
            repo.create(user2)


# ──────────────────────────────────────────────
#  Find User by ID
# ──────────────────────────────────────────────


class TestFindUserById:
    """Tests for the find_by_id() method."""

    def test_find_by_id_returns_user(self):
        """Finding an existing user should return the user."""
        repo = InMemoryUserRepository()
        user = User("USER-001", "Alice", "alice@example.com")
        repo.create(user)

        found = repo.find_by_id("USER-001")

        assert found is user

    def test_find_by_id_returns_none_if_not_found(self):
        """Finding a non-existent user should return None."""
        repo = InMemoryUserRepository()

        found = repo.find_by_id("USER-999")

        assert found is None

    def test_find_by_id_after_multiple_creates(self):
        """Finding a specific user among multiple should work."""
        repo = InMemoryUserRepository()
        user1 = User("USER-001", "Alice", "alice@example.com")
        user2 = User("USER-002", "Bob", "bob@example.com")
        user3 = User("USER-003", "Carol", "carol@example.com")

        repo.create(user1)
        repo.create(user2)
        repo.create(user3)

        found = repo.find_by_id("USER-002")

        assert found is user2


# ──────────────────────────────────────────────
#  List All Users
# ──────────────────────────────────────────────


class TestListAllUsers:
    """Tests for the list_all() method."""

    def test_list_all_returns_all_users(self):
        """list_all() should return all stored users."""
        repo = InMemoryUserRepository()
        user1 = User("USER-001", "Alice", "alice@example.com")
        user2 = User("USER-002", "Bob", "bob@example.com")

        repo.create(user1)
        repo.create(user2)

        users = repo.list_all()

        assert len(users) == 2
        assert user1 in users
        assert user2 in users

    def test_list_all_empty_repository(self):
        """list_all() should return empty list for empty repository."""
        repo = InMemoryUserRepository()

        users = repo.list_all()

        assert users == []


# ──────────────────────────────────────────────
#  User Exists
# ──────────────────────────────────────────────


class TestUserExists:
    """Tests for the exists() method."""

    def test_exists_returns_true_for_existing_user(self):
        """exists() should return True for an existing user."""
        repo = InMemoryUserRepository()
        user = User("USER-001", "Alice", "alice@example.com")
        repo.create(user)

        assert repo.exists("USER-001") is True

    def test_exists_returns_false_for_nonexistent_user(self):
        """exists() should return False for a non-existent user."""
        repo = InMemoryUserRepository()

        assert repo.exists("USER-999") is False


# ──────────────────────────────────────────────
#  Delete User
# ──────────────────────────────────────────────


class TestDeleteUser:
    """Tests for the delete() method."""

    def test_delete_removes_user(self):
        """Deleting a user should remove it from the repository."""
        repo = InMemoryUserRepository()
        user = User("USER-001", "Alice", "alice@example.com")
        repo.create(user)

        result = repo.delete("USER-001")

        assert result is True
        assert not repo.exists("USER-001")
        assert repo.count() == 0

    def test_delete_nonexistent_user_returns_false(self):
        """Deleting a non-existent user should return False."""
        repo = InMemoryUserRepository()

        result = repo.delete("USER-999")

        assert result is False

    def test_delete_one_of_many(self):
        """Deleting one user should leave others intact."""
        repo = InMemoryUserRepository()
        user1 = User("USER-001", "Alice", "alice@example.com")
        user2 = User("USER-002", "Bob", "bob@example.com")
        user3 = User("USER-003", "Carol", "carol@example.com")

        repo.create(user1)
        repo.create(user2)
        repo.create(user3)

        repo.delete("USER-002")

        assert repo.count() == 2
        assert repo.exists("USER-001")
        assert not repo.exists("USER-002")
        assert repo.exists("USER-003")


# ──────────────────────────────────────────────
#  Helper Methods
# ──────────────────────────────────────────────


class TestHelperMethods:
    """Tests for helper methods (count, clear)."""

    def test_count_returns_number_of_users(self):
        """count() should return the number of users."""
        repo = InMemoryUserRepository()
        user1 = User("USER-001", "Alice", "alice@example.com")
        user2 = User("USER-002", "Bob", "bob@example.com")

        repo.create(user1)
        repo.create(user2)

        assert repo.count() == 2

    def test_count_empty_repository(self):
        """count() should return 0 for empty repository."""
        repo = InMemoryUserRepository()

        assert repo.count() == 0

    def test_clear_removes_all_users(self):
        """clear() should remove all users."""
        repo = InMemoryUserRepository()
        user1 = User("USER-001", "Alice", "alice@example.com")
        user2 = User("USER-002", "Bob", "bob@example.com")

        repo.create(user1)
        repo.create(user2)

        repo.clear()

        assert repo.count() == 0
        assert repo.list_all() == []
