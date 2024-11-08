from contextlib import contextmanager
import re
import os
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
    with pytest.raises(ValueError, match="Invalid price: -8.5. Price must be a positive number."):
        create_meal(meal='Meal Name', cuisine='Cuisine Name', price=-8.50, difficulty='LOW')

    # Attempt to create a meal with a non-float price
    with pytest.raises(ValueError, match="Invalid price: invalid. Price must be a positive number."):
        create_meal(meal='Meal Name', cuisine='Cuisine Name', price='invalid', difficulty='LOW')



# test invalid difficulty, must be low, med, or high
def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid difficulty (not low, med, or high)."""

    # Attempt to create a meal with a difficulty not low, med, or high
    with pytest.raises(ValueError, match="Invalid difficulty level: HI. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal='Meal Name', cuisine='Cuisine Name', price=8.50, difficulty='HI')



# test clear meals
def test_clear_meals(mock_cursor, mocker):
    """Test clearing all meals from the combatants list"""

    mocker.patch.dict(os.environ, {"SQL_CREATE_TABLE_PATH": "dummy_path.sql"})
    mock_create_table_script = "CREATE TABLE meals (id INTEGER PRIMARY KEY, name TEXT);"
    mocker.patch("builtins.open", mocker.mock_open(read_data=mock_create_table_script))
    
    clear_meals()
    
    mock_cursor.executescript.assert_called_once_with(mock_create_table_script)
    mock_cursor.connection.commit()

    assert mock_cursor.connection.commit.call_count == 1



# test delete meal
def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the combatants list by meal ID."""

    # Simulate that the song exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_song function
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."



# test delete meal with non-existent id
def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""

    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)



# test delete meal with meal that's already been deleted
def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""

    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)



# test get leaderboard
def test_get_leaderboard(mock_cursor):
    """Testing get_leaderboard, should return the correct leaderboard."""

    # Sample data to return from the mock cursor
    mock_cursor.fetchall.return_value = [
        (2, "Sushi", "Japanese", 15.0, "Medium", 10, 8, 0.8),
        (1, "Spaghetti", "Italian", 10.0, "Easy", 5, 3, 0.6),
        (3, "Tacos", "Mexican", 8.0, "Easy", 7, 4, 0.5714285714)
    ]  # Ensure this is sorted by wins for the test

    # Test sorting by 'wins'
    leaderboard_wins = get_leaderboard(sort_by="wins")

    expected_wins = [
        {'id': 2, 'meal': 'Sushi', 'cuisine': 'Japanese', 'price': 15.0, 'difficulty': 'Medium', 'battles': 10, 'wins': 8, 'win_pct': 80.0},
        {'id': 1, 'meal': 'Spaghetti', 'cuisine': 'Italian', 'price': 10.0, 'difficulty': 'Easy', 'battles': 5, 'wins': 3, 'win_pct': 60.0},
        {'id': 3, 'meal': 'Tacos', 'cuisine': 'Mexican', 'price': 8.0, 'difficulty': 'Easy', 'battles': 7, 'wins': 4, 'win_pct': 57.1},
    ]
    
    assert leaderboard_wins == expected_wins

    # Test sorting by 'win_pct'
    leaderboard_win_pct = get_leaderboard(sort_by="win_pct")

    expected_win_pct = [
        {'id': 2, 'meal': 'Sushi', 'cuisine': 'Japanese', 'price': 15.0, 'difficulty': 'Medium', 'battles': 10, 'wins': 8, 'win_pct': 80.0},
        {'id': 1, 'meal': 'Spaghetti', 'cuisine': 'Italian', 'price': 10.0, 'difficulty': 'Easy', 'battles': 5, 'wins': 3, 'win_pct': 60.0},
        {'id': 3, 'meal': 'Tacos', 'cuisine': 'Mexican', 'price': 8.0, 'difficulty': 'Easy', 'battles': 7, 'wins': 4, 'win_pct': 57.1},
    ]

    assert leaderboard_win_pct == expected_win_pct



# test get leaderboard, invalid sort_by parameter
def test_get_leaderboard_bad_sort_by(mock_cursor):
    '''Test get_leaderboard that passes an invalid sort_by parameter.'''

    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid"):
        get_leaderboard(sort_by="invalid")
    


# test get meal by id
def test_get_meal_by_id(mock_cursor):
    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Cuisine Name", 50.0, "MED", False)

    # Call the function and check the result
    result = get_meal_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Meal Name", "Cuisine Name", 50.0, "MED")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


# test get meal by id, non-existent id
def test_get_meal_by_id_bad_id(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

# test get meal by id, meal that's already been deleted
def test_get_meal_by_id_deleted_meal(mock_cursor):
    """Test error when getting a meal that is already deleted"""

    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = (999, "Meal Name", "Cuisine Name", 50.0, "MED", True)

    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        result = get_meal_by_id(999)

# test get meal by name
def test_get_meal_by_name(mock_cursor):
    # Simulate that the meal exists (meal = "Meal Name")
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Cuisine Name", 50.0, "MED", False)

    # Call the function and check the result
    result = get_meal_by_name("Meal Name")

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Meal Name", "Cuisine Name", 50.0, "MED")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal Name",)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

# test get meal by name, name doesn't exist
def test_get_meal_by_name_bad_name(mock_cursor):
    # Simulate that no meal exists for the given name
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with name Meal Name not found"):
        get_meal_by_name("Meal Name")

# test get meal by name, name was deleted
def test_get_meal_by_id_deleted_meal(mock_cursor):
    """Test error when getting a meal that is already deleted"""

    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = (999, "Meal Name", "Cuisine Name", 50.0, "MED", True)
    
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        get_meal_by_id(999)

# test update meal stats
def test_update_meal_stats_result_win(mock_cursor):

    mock_cursor.fetchone.return_value = [False]

    meal_id = 1
    result = "win"
    update_meal_stats(meal_id, result)

    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    expected_arguments = (meal_id,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_meal_stats_result_loss(mock_cursor):

    mock_cursor.fetchone.return_value = [False]

    meal_id = 1
    result = "loss"
    update_meal_stats(meal_id, result)

    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1 WHERE id = ?
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    expected_arguments = (meal_id,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


# test update meal stats, meal id doesn't exist
def test_update_meal_stats_deleted_id(mock_cursor):

    mock_cursor.fetchone.return_value = [True]

    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, 'win')

    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM meals WHERE id = ?", (1,))

# test update meal stats, meal id was deleted
def test_update_meal_stats_invalid_id(mock_cursor):

    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        update_meal_stats(999,"win")

    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM meals WHERE id = ?", (999,)) 

# test update meal stats, result is not win or loss
def test_update_meal_stats_invalid_result(mock_cursor):

    mock_cursor.fetchone.return_value = [False]

    with pytest.raises(ValueError, match="Invalid result: Invalid. Expected 'win' or 'loss'."):
        update_meal_stats(1, "Invalid")
