
# Funding Rate App

This is a simple web application that displays funding rates from various cryptocurrency exchanges, including AEVO, HyperLiquid, Bybit, and Gate.io. The application uses Flask for the backend and integrates with the exchanges using the CCXT library.

## File Structure

The project is organized as follows:

```
funding_rate_app/
│
├── app.py
├── requirements.txt
├── config.py
├── .env
├── static/
│   ├── css/
│       └── styles.css
│   ├── js/
│       └── scripts.js
├── templates/
│   ├── index.html
│   └── login.html
├── services/
│   ├── __init__.py
│   ├── hyperliquid_service.py
│   ├── aevo_service.py
│   ├── bybit_service.py
│   └── gateio_service.py
├── tests/
│   ├── __init__.py
│   ├── test_app.py
│   └── test_services.py
└── instance/
    └── config.py
```

### Files and Directories

- `app.py`: The main application file where the Flask app is set up, routes are defined, and the server is run.
- `requirements.txt`: A file listing all the dependencies required for the project.
- `config.py`: Configuration file for setting up different configurations for the app, such as development, testing, and production.
- `.env`: Environment file where sensitive information like API keys, secret keys, and configuration variables are stored.
- `static/`: Directory for static files like CSS, JavaScript, and images.
  - `css/`: Contains CSS files for styling.
    - `styles.css`: Main stylesheet for the application.
  - `js/`: Contains JavaScript files for client-side logic.
    - `scripts.js`: Main JavaScript file for the application.
- `templates/`: Directory for HTML template files.
  - `index.html`: Main page template displaying funding rates.
  - `login.html`: Login page template.
- `services/`: Directory for service modules that handle API interactions.
  - `__init__.py`: Initialization file for the services package.
  - `hyperliquid_service.py`: Functions to interact with the HyperLiquid API.
  - `aevo_service.py`: Functions to interact with the AEVO API.
  - `bybit_service.py`: Functions to interact with the Bybit API.
  - `gateio_service.py`: Functions to interact with the Gate.io API.
- `tests/`: Directory for unit tests and integration tests.
  - `__init__.py`: Initialization file for the tests package.
  - `test_app.py`: Tests for the main app functionalities.
  - `test_services.py`: Tests for the service modules.
- `instance/`: Directory for instance-specific configurations.
  - `config.py`: Configuration specific to this instance of the app, such as API keys and secret keys.

## Setup and Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/funding_rate_app.git
   cd funding_rate_app
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory of your project and add your environment variables.
   ```plaintext
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   HYPERLIQUID_API_KEY=your_hyperliquid_api_key
   AEVO_API_KEY=your_aevo_api_key
   BYBIT_API_KEY=your_bybit_api_key
   GATEIO_API_KEY=your_gateio_api_key
   ```

5. **Run the application:**
   ```sh
   flask run
   ```

## Usage

- **Login:**
  - Open the application in your browser.
  - Enter the username and password to access the main page.
- **View Funding Rates:**
  - After logging in, you will see the funding rates from AEVO, HyperLiquid, Bybit, and Gate.io.
  - Press the "Update Data" button to manually refresh the funding rates.

## Testing

To run the tests, use the following command:
```sh
python -m unittest discover tests
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

```
