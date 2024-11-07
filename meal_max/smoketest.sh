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
check_health() { #Works
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
check_db() { #Works
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

create_meal() { #Works
    id=$1
    meal=$2
    cuisine=$3
    price=$4
    difficulty=$5

    echo "Adding meal ($id - $meal, $cuisine) to the meal list..."
    response=$(curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
        -d "{\"id\":\"$id\", \"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}")    
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Meal added successfully."
    else
        echo "Failed to add meal."
        exit 1
    fi
}

clear_meals() { #Works
  echo "Clearing the meals..."
  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
}

delete_meal() { #Works
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

get_leaderboard() { #Works

    echo "Getting meal leaderboard..."
    response=$(curl -s -X GET "$BASE_URL/leaderboard")
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

get_meal_by_id() { #Works
    meal_id=$1

    echo "Getting meal by ID ($meal_id)..."
    response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
    echo "$response"
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

get_meal_by_name() { #Works
    meal_name=$1

    echo "Getting meal by name (Meal Name: $meal_name)"
    response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
    echo $response
    if echo "$response" | grep -q '"status": "success"' ; then
        echo "Meal retrieved successfully by name ($meal_name)."
        if [ "$ECHO_JSON" = true ]; then
            echo "Meal JSON (Name $meal_name)"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get meal by Name ($meal_name)."
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

battle() { #Works
    echo "Battling"
    response=$(curl -s -X GET "$BASE_URL/battle")
    echo "$response"
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

clear_combatants() { # Works
    echo "Clearing combatants..."
    response=$(curl -s -X POST "$BASE_URL/clear-combatants")

    if echo "$response" | grep -q '"status": "success"'; then
        echo "Combatants cleared successfully."
    else
        echo "Failed to clear combatants."
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

get_combatants() { #Works
  echo "Getting all songs in the combatants..."
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

prep_combatant() { #Works
    meal=$1
    echo "Preparing combatant... $meal"
    response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" \
    -d "{\"meal\": \"$meal\"}") 
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Combatant prepared."
        if [ "$ECHO_JSON" = true ]; then
            echo "Combatants JSON:"
            echo "$response" | jq
        fi
    else
        echo "Failed to prepare combatant: $meal"
        exit 1
    fi
}

check_health
check_db

clear_meals
clear_combatants

create_meal 1 'MealName' 'Cuisine Name' 50.0 'LOW'
create_meal 2 'MealName2' 'Cuisine Name 2' 75.5 'MED'
create_meal 3 'MealName3' 'Cuisine Name 3' 100.0 'HIGH'
create_meal 4 'MealName4' 'Cuisine Name 4' 150.0 'HIGH'
prep_combatant "MealName4"
prep_combatant "MealName3"

get_combatants

get_meal_by_name "MealName"
delete_meal 1
get_leaderboard
get_meal_by_id 2

battle


