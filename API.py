# API.py
import requests
import threading

#API_URL = 'http://localhost:3000/api/'
#API_URL = 'https://diagnostics-server.vercel.app/api/'
API_URL = 'https://diagnosticsserver-danaran319-q6k5.onreza.app/api/'
def auth(username, password, callback=None):
    """Non-blocking authentication with proper error handling"""

    def _do_auth():
        try:
            data = {
                'password': password,
                'username': username
            }

            # Send request
            r = requests.post(API_URL + 'auth', json=data)
            print(f"sending request to {API_URL}auth?password={password}&username={username}")

            print(r)
            # Check HTTP status code FIRST
            if r.status_code == 401:
                # Invalid credentials - this is NOT an exception
                if callback:

                    callback(False, None, None, "Неверный логин или пароль")
                return

            elif r.status_code == 500:
                # Server error
                if callback:
                    callback(False, None, None, "Ошибка сервера. попробуйте позже")
                return

            elif r.status_code != 200:
                # Other unexpected status codes
                if callback:
                    callback(False, None, None, f"Неизвеизвестная ошибка (код {r.status_code})")
                return

            # If we get here, status is 200 - parse JSON
            result = r.json()
            print(f"Auth successful: {result}")

            role = result.get('role')
            user_id = result.get('userId')

            if role and user_id:
                if callback:
                    callback(True, role, user_id, None)
            else:
                if callback:
                    callback(False, None, None, "Некорректный ответ от сервера")

        except requests.exceptions.ConnectionError:
            if callback:
                callback(False, None, None, "Нет соединения с сервером. проверьте интернет")
            else:
                return None, None

        except requests.exceptions.Timeout:
            if callback:
                callback(False, None, None, "Превышено время ожидания ответа от cервера")
            else:
                return None, None

        except requests.exceptions.RequestException as e:
            if callback:
                callback(False, None, None, f"Ошибка сети: {str(e)}")
            else:
                return None, None

        except Exception as e:
            if callback:
                callback(False, None, None, f"Неожиданная ошибка: {str(e)}")
            else:
                return None, None

    # If callback provided, run in thread
    if callback:
        thread = threading.Thread(target=_do_auth, daemon=True)
        thread.start()
        return True  # Return immediately
    else:
        # Synchronous mode (for backward compatibility)
        return _do_auth()

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