#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

create_meal() {
    meal=$1
    cuisine=$2
    price=$3
    difficulty=$4

    echo "Creating meal: ($meal)"
    curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
        -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}" | grep -q '"status": "success"'
    
    if [ $? -eq 0 ]; then
        echo "Song added successfully."
    else
        echo "Failed to add meal."
        exit 1
    fi
}

clear_meals() {
  echo "Clearing meals..."
  response=$(curl -s -X POST "$BASE_URL/clear-meals")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meals cleared successfully."
  else
    echo "Failed to clear meals."
    exit 1
  fi
}

delete_meal() {
    meal_id=$1

    echo "Deleting meal by ID ($meal_id)..."
    response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Meal deleted successfully ($meal_id)."
    else
        echo "Failed to delete meal ($song_id)."
        exit 1
    fi
}

get_leaderboard() {
    $sort_by=$1

    echo "Getting meal leaderboard..."
    response=$(curl -s -X GET "$BASE_URL/get-leaderboard/$sort_by")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Meal leaderboard retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Leaderboard JSON:"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get meal leaderboard."
        exit 1
    fi
}

get_meal_by_id() {
    meal_id=$1

    echo "Getting meal by ID ($meal_id)..."
    response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Meal retrieved successfully by ID ($meal_id)."
        if [ "$ECHO_JSON" = true ]; then
            echo "Meal JSON (ID $meal_id):"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get meal by ID ($meal_id)."
        exit 1
    fi
}

get_meal_by_name() {
    meal_name=$1

    echo "Getting meal by name ($meal_name)"
    response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Meal retrieved successfully by name ($meal_name)."
        if [ "$ECHO_JSON" = true ]; then
            echo "Meal JSON (Name $meal_name):"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get meal by name ($meal_name)."
        exit 1
    fi
}

update_meal_stats() {
    meal_id=$1
    result=$2

    echo "Updating meal ($meal_id)"
    curl -s -X POST "$BASE_URL/update-meal-stats" -H "Content-Type: application/json" \
        -d "{\"meal_id\":\"$meal_id\", \"result\":\"$result\"}" | grep -q '"status": "success"'
    
    if [ $? -eq 0 ]; then
        echo "Meal updated successfully."
    else
        echo "Failed to update meal."
        exit 1
    fi
}

battle() {
    echo "Battling"
    response=$(curl -s -X GET "$BASE_URL/battle")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Battle occured successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Battle JSON:"
            echo "$response" | jq .
        fi
    else
        echo "Battle failed."
        exit 1
    fi
}

clear_combatants() {
    echo "Clearing all combatants..."
    response=$(curl -s -X GET "$BASE_URL/clear-combatants")

    if echo "$response" | grep -q '"status": "success"'; then
        echo "Combatants are cleared"
    else
        echo "Failed to clear combatants"
        exit 1
    fi
}

get_battle_score() {
    meal=$1

    echo "Getting the battle score"
    response=$(curl -s -X GET "$BASE_URL/get-battle-score/$meal")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Successfully retrieved the battle score."
        if [ "$ECHO_JSON" = true ]; then
            echo "Battle Score JSON (Name $meal):"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get battle score."
        exit 1
    fi
}

get_combatants() {
  echo "Getting all songs in the playlist..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All combatants retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Combatants JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get combatants."
    exit 1
  fi
}

prep_combatant() {
    meal=$1

    echo "Preparing combatant: $meal ..."
    response=$(curl -s -X GET "$BASE_URL/prep-combatant/$meal")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Combatant prepared successfully."
        if [ "$ECHO_JSON" = true ]; then
        echo "Combatant JSON:"
        echo "$response" | jq .
        fi
    else
        echo "Failed to prepare combatant."
        exit 1
    fi
}