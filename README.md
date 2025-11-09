# Journal Help Support Buddy FastAPI Application

This is a FastAPI application for a journal help support buddy.

## Prerequisites

- Python 3.9+
- PostgreSQL
- `uv` (Ultra-fast Python package installer and resolver)

## Setup

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/supportbuddy.git
    cd supportbuddy/backend
    ```

2. **Install UV (if not already installed):**

    **Windows:**
    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

    **macOS/Linux:**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

3. **Create virtual environment and install dependencies:**

    ```sh
    uv venv
    uv pip install -e .
    ```

## Legacy Setup (pip)

<details>
<summary>Click to expand legacy pip instructions</summary>

1. **Create and activate a virtual environment:**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2. **Install the required packages:**

    ```sh
    pip install -r requirements.txt
    ```
</details>

## Environment Variables

Create a .env file in the root directory and add the following environment variables:

```env
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DATABASE_URL=your_database_url
MAILGUN_API_KEY=your_mailgun_key
MAILGUN_DOMAIN=your_mailgun_domain
GOOGLE_GENAI_API_KEY=your_google_ai_key
```

## Running the Application

### Development Server
```sh
# Using UV
uv run start-dev

# Or with make
make start-dev

# Legacy
uvicorn app:app --reload
```

### Production Server
```sh
# Using UV
uv run start-server

# Or with make
make start

# Legacy
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Serverless Functions
```sh
# Using UV
uv run run-serverless

# Or with make
make serverless

# Legacy
python serverless_runner.py
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