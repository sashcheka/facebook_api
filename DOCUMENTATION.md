# Facebook Page Access Token Retrieval

This code retrieves the access token for a Facebook Page using the Facebook Graph API.

## Prerequisites

Before running the code, ensure that you have the following:

- A valid Facebook Page ID
- An access token with the required permissions to access the Page's information

## Usage

1. Replace `'page_id'` with your actual Facebook Page ID.
2. Replace `'access_token'` with your valid access token.

```python
import requests

# Specify the Facebook Page ID and access token
page_id = 'page_id'
access_token = 'access_token'

# Construct the API URL
url = f'https://graph.facebook.com/{page_id}?fields=access_token'

# Prepare the parameters
params = {
    'access_token': access_token
}

# Send a GET request to retrieve the access token
response = requests.get(url, params=params).json()

# Print the response containing the access token
print(response)
```

## Output

The code will print the response JSON object, which includes the access token for the specified Facebook Page.

## Notes

- Ensure that the access token used has the necessary permissions to access the Page's information.
- This code utilizes the `requests` library to send HTTP requests to the Facebook Graph API.
