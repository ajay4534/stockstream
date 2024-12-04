# StockStream

A real-time stock and cryptocurrency price tracker with user authentication and personalized watchlists.

## Features

- **Real-time Price Tracking**
  - Live stock prices using yahoo_fin
  - Cryptocurrency prices from CoinGecko API
  - Automatic price updates
  
- **User Authentication**
  - Secure registration and login
  - Password hashing with bcrypt
  - Session management with Flask-Login
  
- **Personal Watchlists**
  - Add/remove stocks and cryptocurrencies
  - Persistent storage with MongoDB Atlas
  - User-specific tracking

- **Modern UI/UX**
  - Responsive design
  - Animated gradients and glassmorphism effects
  - Font Awesome icons
  - Real-time price updates
  - Loading animations

## Tech Stack

- **Backend**
  - Flask 3.0.0
  - Flask-Login for authentication
  - MongoDB Atlas for database
  - yahoo_fin for stock data
  - CoinGecko API for crypto data

- **Frontend**
  - HTML5/CSS3
  - JavaScript (Vanilla)
  - Font Awesome icons
  - Modern CSS features (Grid, Flexbox, Variables)

## Prerequisites

- Python 3.8+
- MongoDB Atlas account
- Internet connection for API access

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd stockstream
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```
   MONGO_URI=your_mongodb_atlas_connection_string
   MONGO_DB_NAME=stockstream
   SECRET_KEY=your_secret_key
   ```

4. Start the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## MongoDB Atlas Setup

1. Create a MongoDB Atlas account at [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. In the Security tab:
   - Create a database user
   - Add your IP address to the IP Access List
4. Click "Connect" and choose "Connect your application"
5. Copy the connection string and update your `.env` file

## Project Structure

```
stockstream/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── static/
│   ├── css/
│   │   └── style.css    # Stylesheets
│   └── js/
│       └── main.js      # Frontend JavaScript
└── templates/
    ├── base.html        # Base template
    ├── index.html       # Main dashboard
    ├── login.html       # Login page
    ├── register.html    # Registration page
    └── profile.html     # User profile page
```

## Usage

1. Register a new account
2. Log in with your credentials
3. Search for stocks or cryptocurrencies
4. Add assets to your watchlist
5. View real-time price updates
6. Manage your profile and settings

## Security Features

- Password hashing with bcrypt
- Secure session management
- CSRF protection
- Environment variable configuration
- MongoDB Atlas security features

## API Rate Limits

- yahoo_fin: No strict limit
- CoinGecko API: 50 calls/minute

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- yahoo_fin for stock data
- CoinGecko for cryptocurrency data
- MongoDB Atlas for database hosting
- Font Awesome for icons
