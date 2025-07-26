# Journal Help Support Buddy FastAPI Application

This is a FastAPI application for a journal help support buddy.

## Prerequisites

- Python 3.7+
- PostgreSQL
- `pip` (Python package installer)

## Setup

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/supportbuddy.git
    cd supportbuddy/backend
    ```

2. **Create and activate a virtual environment:**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    Create a .env file in the root directory and add the following environment variables:

    ```env
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=your_db_host
    ```

5. **Run the FastAPI application:**

    ```sh
    uvicorn app:app --reload
    ```

    The application will be available at `http://127.0.0.1:8000`.

## Usage

- **Endpoint to create a journal entry:**

    ```http
    POST /journal/
    ```

    **Request Body:**

    ```json
    {
        "content": "Today I had a great day!"
    }
    ```

- **Endpoint to generate a motivational message:**

    ```http
    POST /generate-message/
    ```

    **Request Body:**

    ```json
    {
        "content": "Today I had a great day!"
    }
    ```

    **Response:**

    ```json
    {
        "message": "That's wonderful to hear! Keep up the positive energy."
    }
    ```

## Custom Exception Handling

The application includes custom exception handling for validation errors. If the request body does not match the expected schema, a detailed error message will be returned.

## Security

The application uses parameterized queries to prevent SQL injection attacks. Always ensure that user inputs are properly sanitized and validated.

## License

This project is licensed under the MIT License.