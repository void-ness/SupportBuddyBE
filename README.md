# HikeCalc FastAPI Application

This is a FastAPI application for predicting promotions and salary hikes.

## Prerequisites

- Python 3.7+
- PostgreSQL
- `pip` (Python package installer)

## Setup

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/hikecalc.git
    cd hikecalc/server
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

    Create a [.env](http://_vscodecontentref_/0) file in the root directory and add the following environment variables:

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

- **Endpoint to predict promotions and salary hikes:**

    ```http
    POST /predict
    ```

    **Request Body:**

    ```json
    {
        "company": "tata1mg",
        "designation": "sde-1",
        "currentCTC": 10,
        "totalYoE": 5,
        "designationYoE": 3,
        "performanceRating": "4"
    }
    ```

    **Response:**

    ```json
    {
        "promotion_likelihood": true,
        "min_hike": 15.0,
        "max_hike": 25.0,
        "confidence_score": 0.6
    }
    ```

## Custom Exception Handling

The application includes custom exception handling for validation errors. If the request body does not match the expected schema, a detailed error message will be returned.

## Security

The application uses parameterized queries to prevent SQL injection attacks. Always ensure that user inputs are properly sanitized and validated.

## License

This project is licensed under the MIT License.