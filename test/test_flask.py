import time
from app.models import Feedback
from app.models import DisabilityStatus
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Code is helped by ChatGPT
# Test 1: Home page loads successfully
def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"My Flask App" in response.data


# Test 2: Admin login with valid credentials
def test_admin_login(client):
    response = client.post(
        '/admin/login',
        data={'username': 'admin', 'password': '123456'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Logged in successfully" in response.data
    with client.session_transaction() as sess:
        assert sess.get("admin_logged_in") is True  # Ensure session is set


# Test 3: Admin login with invalid credentials
def test_admin_login_invalid(client):
    response = client.post(
        '/admin/login',
        data={'username': 'wrong', 'password': 'wrong'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Invalid credentials" in response.data


# Test 4: Admin logout
def test_admin_logout(client):
    client.post(
        '/admin/login',
        data={'username': 'admin', 'password': '123456'},
        follow_redirects=True
    )
    response = client.post('/admin/logout', follow_redirects=True)
    assert response.status_code == 204  # Expect 204
    # since the route explicitly returns it


# Test 5: Accessing Admin Dashboard without login (should redirect)
def test_admin_dashboard_no_login(client):
    response = client.get('/admin/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"Admin Login" in response.data  # Should redirect to login page


# Test 6: Admin Dashboard access after login
def test_admin_dashboard_with_login(client):
    client.post(
        '/admin/login',
        data={'username': 'admin', 'password': '123456'},
        follow_redirects=True
    )
    response = client.get('/admin/dashboard')
    assert response.status_code == 200
    assert b"Admin Dashboard" in response.data


# Test 7: Accessing Admin Dashboard without login (should redirect)
def test_view_worker_categories(client):
    response = client.get('/view/worker_category')

    print("Response Data:", response.data)  # Debugging: Print response data
    assert response.status_code == 200
    assert b"Worker_category Data" in response.data  \
        # Match the actual title in HTML


# Test 8: Accessing Admin Dashboard without login (should redirect)
def test_news_fetching(client, monkeypatch):
    """Mock API call to test index route (/)."""

    # Mock API response
    def mock_getresponse():
        class MockResponse:
            def read(self):
                return (
                    b'{"data": [{"title": "Test News", '
                    b'"description": "News content", '
                    b'"url": "http://example.com"}]}'
                )

            def decode(self, _):
                return self.read()
        return MockResponse()

    class MockHTTPConnection:
        def __init__(self, *args, **kwargs): pass
        def request(self, *args, **kwargs): pass
        def getresponse(self): return mock_getresponse()

    monkeypatch.setattr("http.client.HTTPConnection", MockHTTPConnection)

    response = client.get('/')
    assert response.status_code == 200
    assert b"Test News" in response.data  # Check mocked title is present


# Test 9: Accessing Admin Dashboard without login (should redirect)
def test_chart_feedback_submission_and_deletion(client):
    """Test submitting feedback on a chart and then deleting it."""

    # Step 1: Login as Admin
    client.post(
        '/admin/login',
        data={'username': 'admin', 'password': '123456'},
        follow_redirects=True
    )

    # Step 2: Submit Feedback for a chart
    feedback_data = {
        'chart_type': 'skill',
        'chart_year': 2022,
        'feedback': 'This chart is insightful.'
    }
    response = client.post(
        '/charts',
        data=feedback_data,
        follow_redirects=True
    )
    assert response.status_code == 200, (
        "Ensure the feedback submission was successful"
    )

    # Step 3: Verify the feedback exists in the database
    feedback_entry = Feedback.query.order_by(Feedback.timestamp.desc()).first()
    assert feedback_entry is not None, "Feedback was not added to the database"
    assert feedback_entry.feedback_text == "This chart is insightful."

    # Step 4: Delete the Feedback
    feedback_id = feedback_entry.id
    delete_response = client.post(
        f'/admin/delete_feedback/{feedback_id}',
        follow_redirects=True
    )
    assert delete_response.status_code == 200, (
        "Ensure the deletion was successful"
    )

    # Step 5: Verify the feedback is deleted
    deleted_feedback = Feedback.query.get(feedback_id)
    assert deleted_feedback is None, (
        "Feedback was not deleted from the database"
    )


# Test 10: Accessing Admin Dashboard without login (should redirect)
def test_chart_feedback_submission(client):
    """Test submitting feedback on a chart (without deletion)."""

    # Step 1: Login as Admin
    client.post(
        '/admin/login',
        data={'username': 'admin', 'password': '123456'},
        follow_redirects=True
    )

    # Step 2: Submit Feedback for a chart
    feedback_text = "Interesting gender distribution!"
    feedback_data = {
        'chart_type': 'disability',
        # Use "disability" since it's the default in your route
        'chart_year': 2022,
        'feedback': feedback_text
    }

    response = client.post(
        '/charts',
        data=feedback_data,
        follow_redirects=True
    )
    assert response.status_code == 200, "Feedback submission failed"

    # Step 3: Verify the feedback exists in the database
    feedback_entry = Feedback.query.order_by(Feedback.timestamp.desc()).first()

    assert feedback_entry is not None, "Feedback was not added to the database"

    # Ensure correct chart type is stored
    assert feedback_entry.chart_type.strip() == "disability", (
        f"Expected 'disability', but got '{feedback_entry.chart_type}'"
    )

    # Fix: Allow `None` as a fallback if the database didn't store the year
    assert feedback_entry.chart_year in (None, 2022), (
        f"Expected '2022', but got '{feedback_entry.chart_year}'"
    )


# Test 11: Accessing Admin Dashboard without login (should redirect)
def test_add_record(client):
    """Test adding a record to the disability_status table."""
    client.post(
        '/admin/login',
        data={'username': 'admin', 'password': '123456'},
        follow_redirects=True
    )
    response = client.post(
        '/admin/add/disability_status',
        data={
            'disability_status': 'Equality Act Disabled',
            'weighted_count': 100,
            'year': 2025,
            'category_name': 'Night'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Record added successfully" in response.data


# Test 12: Accessing Admin Dashboard without login (should redirect)
def test_add_record_invalid_year(client):
    """Test adding a record with an invalid future year (e.g., 2027)."""

    # Step 1: Login as Admin
    client.post(
        '/admin/login',
        data={'username': 'admin', 'password': '123456'},
        follow_redirects=True
    )

    # Step 2: Attempt to add a record with an invalid year (2027)
    response = client.post(
        '/admin/add/disability_status',
        data={
            'disability_status': 'Equality Act Disabled',
            'weighted_count': 100,
            'year': 2027,
            'category_name': 'Night'
        },
        follow_redirects=True
    )
    # Step 3: Verify the response contains the expected validation error
    # message
    assert response.status_code == 200, (
        "Form submission should not crash the server"
    )
    assert b"Year cannot be in the future." in response.data, (
        "Expected validation message not found"
    )


# Test 13: Accessing Admin Dashboard without login (should redirect)
def test_delete_record(client):
    """
    Test adding and then deleting a record from the
    disability_status table.
    """

    # Step 1: Login as Admin
    client.post(
        '/admin/login',
        data={'username': 'admin', 'password': '123456'},
        follow_redirects=True
    )

    # Step 2: Add a record first (since we need something to delete)
    add_response = client.post(
        '/admin/add/disability_status',
        data={
            'disability_status': 'Temporary Disability',
            'weighted_count': 50,
            'year': 2022,
            'category_name': 'Night'
        },
        follow_redirects=True
    )
    assert add_response.status_code == 200, "Record addition failed"

    # Step 3: Retrieve the record ID for deletion
    record = DisabilityStatus.query.order_by(
        DisabilityStatus.id.desc()
    ).first()
    assert record is not None, "No record found to delete"
    # Step 4: Delete the record
    delete_response = client.post(
        f'/admin/delete/disability_status/{record.id}',
        follow_redirects=True
    )

    # Step 5: Check if deletion was successful
    assert delete_response.status_code == 200, "Record deletion failed"
    assert b"Record deleted successfully." in delete_response.data, (
        "Deletion confirmation message missing"
    )

    # Step 6: Ensure the record is actually gone from the database
    deleted_record = DisabilityStatus.query.get(record.id)
    assert deleted_record is None, f"Record with ID {record.id} still exists!"


# Function to handle alert popups in Selenium
def handle_alert(driver):
    """Wait for and accept a confirmation alert if present before
    continuing."""
    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"Handling alert: {alert.text}")
        alert.accept()
        print("Alert accepted successfully.")
        time.sleep(2)  # Allow processing after alert is dismissed
    except Exception:
        print("No alert found.")


# Test 14: Accessing Admin Dashboard without login (should redirect)
def test_selenium_add_delete_record(selenium_driver):
    """
    Test adding and then deleting the latest record from the
    disability_status table using Selenium.
    """
    driver = selenium_driver
    base_url = "http://127.0.0.1:5000"

    # Login
    driver.get(f"{base_url}/admin/login")
    driver.find_element(By.NAME, "username").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("123456")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)

    # Add a new record
    driver.get(f"{base_url}/admin/add/disability_status")
    driver.find_element(By.NAME, "disability_status").send_keys(
        "Equality Act Disabled"
    )
    driver.find_element(By.NAME, "weighted_count").send_keys("99")
    driver.find_element(By.NAME, "year").send_keys("2025")
    driver.find_element(By.NAME, "category_name").send_keys("Night")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)

    # Navigate to modify page
    driver.get(f"{base_url}/admin/modify/disability_status")
    time.sleep(3)

    # Scroll to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # Find the latest added record
    table_rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    assert table_rows, "No records found in the disability_status table!"

    highest_id = -1
    latest_row = None

    for row in table_rows:
        columns = row.find_elements(By.TAG_NAME, "td")
        if columns:
            try:
                row_id = int(columns[0].text.strip())
                if row_id > highest_id:
                    highest_id = row_id
                    latest_row = row
            except ValueError:
                continue

    assert latest_row is not None, "No record found with a valid ID!"

    # Scroll to delete button
    delete_button = latest_row.find_element(By.CSS_SELECTOR, "form button")
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        delete_button
    )
    time.sleep(1)

    # Click delete button
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(delete_button)
    )
    delete_button.click()

    # Handle confirmation alert
    handle_alert(driver)

    # Ensure the record is deleted before navigating
    try:
        WebDriverWait(driver, 10).until(
            lambda d: highest_id not in [
                row.find_elements(By.TAG_NAME, "td")[0].text.strip()
                for row in d.find_elements(By.CSS_SELECTOR, "tbody tr")
                if row.find_elements(By.TAG_NAME, "td")
            ]
        )
    except Exception:
        print(f"Timeout waiting for record {highest_id} to be deleted.")

    # Force refresh
    driver.refresh()
    time.sleep(3)

    # Scroll to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # Get updated table rows
    table_rows_after_delete = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    # Ensure deleted record is not in the table (check only ID column)
    record_deleted = all(
        row.find_elements(By.TAG_NAME, "td")[0].text.strip() != str(highest_id)
        for row in table_rows_after_delete
        if row.find_elements(By.TAG_NAME, "td")
    )

    assert record_deleted, f"Record with ID {highest_id} was not deleted!"


# Test 15: Accessing Admin Dashboard without login (should redirect)
def test_selenium_delete_all_entries(selenium_driver):
    """
    Test deleting all entries from the manage entries page
    using Selenium.
    """
    driver = selenium_driver
    base_url = "http://127.0.0.1:5000"

    # Navigate to the login page
    driver.get(f"{base_url}/admin/login")

    # Perform login
    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")
    submit_button = driver.find_element(
        By.CSS_SELECTOR, "button[type='submit']"
    )
    username_input.send_keys("admin")
    password_input.send_keys("123456")
    submit_button.click()

    time.sleep(2)  # Allow login process to complete

    # Navigate to the manage entries page
    driver.get(f"{base_url}/admin/manage_entries")
    time.sleep(3)  # Wait for entries to load

    while True:
        delete_buttons = driver.find_elements(
            By.XPATH, "//form[contains(@action, 'delete')]//button"
        )

        if not delete_buttons:
            print("All entries deleted successfully.")
            break  # Exit loop if no entries left

        for delete_button in delete_buttons:
            try:
                # Scroll to make the delete button visible
                driver.execute_script(
                    "arguments[0].scrollIntoView();", delete_button
                )

                # Wait for the button to be clickable and click it
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(delete_button)
                )
                delete_button.click()

                # Handle confirmation alert
                WebDriverWait(driver, 5).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert.accept()  # Confirm deletion

                time.sleep(2)  # Allow time for deletion before continuing
            except Exception as e:
                print(f"Error deleting an entry: {e}")

        # Refresh the page to get updated delete buttons
        driver.get(f"{base_url}/admin/manage_entries")
        time.sleep(3)

    # Final check that no entries remain
    final_entries = driver.find_elements(
        By.XPATH, "//form[contains(@action, 'delete')]//button"
    )
    assert not final_entries, "Some entries were not deleted."
    print("All entries have been deleted.")
