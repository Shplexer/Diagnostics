import requests

API_URL = 'https://diagnostics-server.vercel.app/api/'


def auth(username, password):
    # data to be sent to api
    data = {
        'password': password,
        'username': username
    }
    r = requests.post(API_URL + 'auth', json=data)
    result = r.json()
    print(result)

    return result['role'], result['userId']
def delete(url, data):
    try:
        r = requests.delete(API_URL + url, json=data)
        r.raise_for_status()  # Raise exception for HTTP errors
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error deleting data: {e}")
        return False

def post(url, data):
    try:
        r = requests.post(API_URL + url, json=data)
        r.raise_for_status()  # Raise exception for HTTP errors
        # result = r.json()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error posting data: {e}")
        return False
        # return None
    # print(result)

# In API.py, modify get_table_data function:
def get_table_data(tableName, id):
    print(f"sending request to {API_URL}full-tables?tableName={tableName}&id={id}")
    try:
        r = requests.get(url=API_URL + "full-tables", params={"tableName": tableName, "id": id})
        r.raise_for_status()  # Raise exception for HTTP errors
        # print(r.json())
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def get_row_data(tableName, id):
    print(f"sending request to {API_URL}row?tableName={tableName}&id={id}")
    try:
        r = requests.get(url=API_URL + "row", params={"tableName": tableName, "id": id})
        r.raise_for_status()  # Raise exception for HTTP errors
        print(r.json())
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None