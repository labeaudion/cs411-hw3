import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    return mocker.patch("meal_max.models.kitchen_model.update_meal_stats")

"""Fixtures providing sample meals for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(id=1, meal='Meal 1', cuisine='Pork', price='8.50', difficulty='LOW')

@pytest.fixture
def sample_meal2():
    return Meal(id=2, meal='Meal 2', cuisine='Beef', price='6.49', difficulty='MED')

@pytest.fixture
def sample_combatants(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]



# test battle
def test_battle(battle_model):
    """Test battle."""

# test battle, less than 2 combatants



# test clear combatants
def test_clear_combatants(battle_model, sample_meal1):
    """Test clearing the combatants list."""
    battle_model.prep_combatant(sample_meal1)

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after clearing"

# test clear combatants, empty list
def test_clear_combatants_empty_combatants(battle_model, caplog):
    """Test clearing the entire combatants list when it's empty."""
    battle_model.clear_combatants()
    assert len(battle_model.playlist) == 0, "Combatants list should be empty after clearing"
    assert "Clearing an empty combatants list" in caplog.text, "Expected warning message when clearing an empty combatants list"


# test get battle score

# test get combatants

# test prep combatants

# test prep combatants, adding more than 2 combatants






# unit tests for getting the combatants






# unit tests for adding the combatants to the combatants list