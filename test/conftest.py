import sys
import os
import pytest
from sqlalchemy.orm import scoped_session, sessionmaker
from app import create_app, db
from selenium import webdriver

# Code is helped by ChatGPT
# Ensure `app/` directory is correctly recognized as a module
BASE_DIR = os.path.abspath(
    os.path.dirname(os.path.dirname(__file__))
)  # Get project root directory
sys.path.insert(0, BASE_DIR)  # Add project root to `sys.path`


# Ensure `app/` directory is correctly recognized as a module
@pytest.fixture(scope="session")
def app():
    """Create a test app using the real database but without deleting
    schema or data."""
    app = create_app()

    # Use the real database (DO NOT DELETE SCHEMA OR DATA)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for testing

    with app.app_context():
        yield app  # Keep database unchanged
        db.session.remove()


# Test client fixture
@pytest.fixture(scope="session")
def client(app):
    """Flask test client fixture."""
    return app.test_client()


# Test database fixture
@pytest.fixture(scope="function", autouse=True)
def test_transaction(app):
    """Use transactions so tests do not modify the real database."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()  # Start a new transaction
        session_factory = sessionmaker(bind=connection)
        # Correct way to create a scoped session
        test_session = scoped_session(session_factory)

        # Override Flask's session with test session
        db.session = test_session

        yield test_session  # Run the test

        test_session.rollback()  # Undo all changes made in the test
        test_session.remove()  # Remove session before rolling back
        # transaction
        if transaction.is_active:
            # Ensure rollback only if transaction is still active
            transaction.rollback()
        connection.close()  # Close connection


# Selenium WebDriver fixture
@pytest.fixture(scope="session")
def selenium_driver():
    """Set up and tear down the Selenium WebDriver for the test session."""
    driver = webdriver.Chrome()  # Ensure you have ChromeDriver installed
    driver.implicitly_wait(5)  # Wait for elements to load
    # before throwing errors
    yield driver
    driver.quit()  # Close the browser after all tests are done
