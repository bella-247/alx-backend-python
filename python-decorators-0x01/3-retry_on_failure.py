import time
import sqlite3
import functools


def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result

    return wrapper


def retry_on_failure(retries=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    print(f"attempt {attempt} failed: {e}")
                    if attempt < retries:
                        print(f"Retrying in {delay} seconds..")
                        time.sleep(delay)
                    else:
                        print("All attempts failed")
                        raise

        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


#### attempt to fetch users with automatic retry on failure
if __name__ == "__main__":
    users = fetch_users_with_retry()
    print(users)
