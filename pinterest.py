import requests
import json

# --- Configuration ---
# Replace with your actual Pinterest API Access Token
ACCESS_TOKEN = "YOUR_PINTEREST_ACCESS_TOKEN"
# API endpoint to test (e.g., get user account information)
API_ENDPOINT = "https://api.pinterest.com/v5/user_account"

# --- Basic API Test Function ---
def test_pinterest_api():
    if ACCESS_TOKEN == "YOUR_PINTEREST_ACCESS_TOKEN":
        print("ERROR: Please replace 'YOUR_PINTEREST_ACCESS_TOKEN' in the script with your actual access token.")
        print("You can get an access token by creating an app at https://developers.pinterest.com/apps/")
        return

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    print(f"Attempting to call Pinterest API endpoint: {API_ENDPOINT}")

    try:
        response = requests.get(API_ENDPOINT, headers=headers)

        print(f"Status Code: {response.status_code}")

        # Try to parse the JSON response
        try:
            response_data = response.json()
            print("Response JSON:")
            print(json.dumps(response_data, indent=2))
        except json.JSONDecodeError:
            print("Response content (not valid JSON):")
            print(response.text)

        if response.ok:
            print("\nAPI call successful!")
            # You can add more specific checks here based on the expected response
            # For example, check if a specific key exists in response_data
            if 'username' in response_data:
                print(f"Successfully fetched user: {response_data['username']}")
        else:
            print(f"\nAPI call failed. Error: {response.reason}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Run the test ---
if __name__ == "__main__":
    print("--- Pinterest API Test Script ---")
    test_pinterest_api()
    print("\n--- Test Complete ---")
