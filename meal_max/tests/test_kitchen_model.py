from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


# test create meal

# test create duplicate meal

# test invalid price, price must be positive

# test invalid difficulty, must be low, med, or high

# test clear meals

# test clear meals with database error

# test delete meal

# test delete meal with non-existent id

# test delete meal with meal that's already been deleted

# test get leaderboard

# test get leaderboard, invalid sort_by parameter

# test get meal by id

# test get meal by id, non-existent id

# test get meal by id, meal that's already been deleted

# test get meal by name

# test get meal by name, name doesn't exist

# test get meal by name, name was deleted

# test update meal stats

# test update meal stats, meal id doesn't exist

# test update meal stats, meal id was deleted

# test update meal stats, result is not win or loss