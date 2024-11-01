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
def test_create_meal(mock_cursor):
    """Test creating a new meal."""

    # Call the function to create a new meal
    create_meal(meal='Meal Name', cuisine='Cuisine Name', price=8.50, difficulty='LOW')

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal Name", "Cuisine Name", 8.50, "LOW")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

# test create duplicate meal
def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate meal name (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meal.name")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Meal with name 'Meal Name' already exists"):
        create_meal(meal='Meal Name', cuisine='Cuisine Name', price=8.50, difficulty='LOW')


# test invalid price, price must be positive
def test_create_meal_invalid_price():
    """Test error when trying to create a meal with an invalid price (e.g., negative price)"""

    # Attempt to create a meal with a negative price
    with pytest.raises(ValueError, match="Invalid meal price: -8.50 \(must be a positive float\)."):
        create_meal(meal='Meal Name', cuisine='Cuisine Name', price=-8.50, difficulty='LOW')

    # Attempt to create a meal with a non-float price
    with pytest.raises(ValueError, match="Invalid meal rpice: invalid \(must be a positive float\)."):
        create_meal(meal='Meal Name', cuisine='Cuisine Name', price='invalid', difficulty='LOW')



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