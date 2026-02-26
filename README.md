# Worker Statistics Flask APP

## Overview

This project is a **Flask-based web application** designed to provide interactive visualizations of worker statistics. It includes features such as **disability status analysis, skill level distribution, skill trends over time, and gender distribution**. The application uses an **SQLite database** to store information about night workers. Users can leave feedback for each chart, while administrators have the ability to add or delete records, view logs, and manage feedback and logs effectively. For the admin user the username is admin and the password is 123456.

## Features

- **Disability Status Analysis**: Displays worker distribution by disability status using a pie chart.
- **Skill Level Distribution**: Presents worker counts based on skill levels for selected years.
- **Skill Level Trends Over Time**: Shows trends in skill levels over multiple years using a line chart.
- **Gender Distribution**: Represents gender distribution for different years using a pie chart.
- **Feedback System**: Allows users to leave feedback for each chart.
- **Administrative Tools**: Enables administrators to add or delete records, view logs, and manage feedback and logs effectively.
- **Database Management**: Utilizes an SQLite database to store and manage worker statistics.
- **Interactive Visualizations**: Provides dynamic and interactive charts for data exploration.

## Instructions for Using This Repository

1. **Clone the Repository**  
    Clone this repository and navigate into the project directory:
    ```bash
    git clone https://github.com/yaoqid/comp0034-jake.git
    cd comp0034-jake
    ```

2. **Set Up a Virtual Environment**  
    It is recommended to use a virtual environment for managing dependencies:
    ```bash
    python -m venv .venv
    source .venv/bin/activate    # For macOS/Linux
    .venv\Scripts\activate       # For Windows
    ```

3. **Install Dependencies**  
    Install the necessary packages:
    ```bash
    pip install -r requirements.txt
    pip install -e .
    ```

4. **Install Testing Tools**  
    Install the `pytest` and `selenium` Python packages:
    ```bash
    pip install selenium pytest
    ```

5. **Set Up the Database**  
    Initialize and migrate the database:
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```


## Activity Instructions for Running the Flask App

1. **Start the Flask Application**  
    Run the following command to start the Flask app:
    ```bash
    flask run
    ```

2. **Access the Application**  
    Open your browser and navigate to:
    [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

3. **Run Tests**  
    To ensure everything is working correctly, run the tests using:
    ```bash
    pytest
    ```

4. **Reset Migrations (if needed)**  
    If you need to reset migrations, use the following commands:
    ```bash
    Remove-Item -Recurse -Force migrations
    flask db init
    flask db migrate -m "Reinitializing migrations"
    flask db upgrade
    ```

5. **Set Environment Variable (if required)**  
    Ensure the `PYTHONPATH` environment variable is set correctly:
    ```bash
    $env:PYTHONPATH="C:\Users\35562\Desktop\comp0034-jake"
    ```

## AI use

    This project uses **Microsoft Copilot** for code suggestions and Flake8 code formatting. Additionally, **ChatGPT-4o** was utilised for advising HTML code snippets and some functions.
