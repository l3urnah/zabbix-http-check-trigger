import requests
import json

# Replace with your Zabbix server URL and API endpoint
ZABBIX_SERVER = 'http://192.168.50.106/zabbix'
API_ENDPOINT = '/api_jsonrpc.php'

# The JSON payload for the API request
payload = {
    "jsonrpc": "2.0",
    "method": "apiinfo.version",
    "params": [],
    "id": 1,
    "auth": None
}

# Headers for the request
headers = {
    'Content-Type': 'application/json-rpc',
    'User-Agent': 'MyScript/1.0'
}

# The full URL to the Zabbix API endpoint
url = ZABBIX_SERVER + API_ENDPOINT

# Send the POST request to the Zabbix API
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    result = response.json()
    print(result)
else:
    print(f"Failed to get API version: {response.status_code}")