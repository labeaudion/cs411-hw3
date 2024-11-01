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
def test_battle(battle_model, sample_combatants):
    """Test battle."""
    battle_model.combatants.extend(sample_combatants)

    winner = battle_model.battle()
    assert len(sample_combatants) == 1
    assert winner == winner.meal

# test battle, less than 2 combatants
def test_battle_less_2_combatants(battle_model, sample_meal1):
    battle_model.combatants.extend(sample_meal1)

    assert len(battle_model.combatants) < 2, "Expected 1 combatant"


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
def test_get_battle_score(battle_model, sample_meal1):
    """Test getting the battle score of a combatant"""
    battle_model.prep_combatant(sample_meal1)

    score = battle_model.get_battle_score(sample_meal1)
    assert score == 31


# test get combatants
def test_get_combatants(battle_model, sample_combatants):
    '''Test getting combatants'''
    battle_model.combatants.extend(sample_combatants)

    all_combatants = battle_model.get_combatants()
    assert len(all_combatants) == 2
    assert all_combatants[0].id == 1
    assert all_combatants[1].id == 2


# test prep combatants
def test_prep_combatants(battle_model, sample_meal1):
    """Test adding a combatant to the combatants list"""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Meal 1'


# test prep combatants, adding more than 2 combatants
def test_prep_combatants_more_2_combatants(battle_model, sample_combatants, sample_meal1):
    """Test adding a combatant to an already full combatants list"""
    battle_model.combatants.extend(sample_combatants)
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal1)