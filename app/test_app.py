import pytest
import psycopg2
from flask import Flask
from app import app as flask_app

# Sample database configuration for testing
db_user = 'postgres'
db_password = 'bse4105'
db_name = 'user'
db_host = 'db'
db_port = '5432'

@pytest.fixture
def app():
    """Create a test version of the Flask app."""
    flask_app.config['TESTING'] = True
    return flask_app

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

def test_hello_route(client):
    """Test the '/' route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Hello, World!" in response.data

def test_users_route(client):
    """Test the '/users' route."""
    # Ensure the '/users' route works and returns the data
    response = client.get('/users')
    assert response.status_code == 200
    assert isinstance(response.json, list)  # Should return a list of users

def test_db_connection():
    """Test if the app can connect to the PostgreSQL database."""
    conn = None
    try:
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,  # make sure matches POSTGRES_DB
            user=db_user,
            password=db_password,
            port=db_port
        )
        cursor = conn.cursor()
        cursor.execute('SELECT 1;')
        result = cursor.fetchone()
        assert result == (1,)
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")
    finally:
        if conn:
            conn.close()
