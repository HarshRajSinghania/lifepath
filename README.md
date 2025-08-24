# LifePath - Financial Future Visualization

LifePath is a web-based financial visualization tool that bridges the gap between aspirational dreams and financial reality for young adults. Unlike standard budgeting apps, LifePath tells a story through a three-act process: defining your ideal future, documenting your current state, and revealing the gap between dreams and reality.

## Features

- **Dream Builder**: Define your ideal lifestyle and location with detailed cost breakdowns
- **Reality Check**: Document current income and expenses 
- **Path Planning**: Choose between college/trade school or workforce entry with loan calculations
- **Visual Dashboard**: Interactive charts showing dream vs reality comparison
- **Subscription Audit**: Tool to review and manage recurring expenses
- **Financial Gap Analysis**: Clear visualization of what it takes to achieve your dreams

## Technology Stack

- **Backend**: Python Flask with RESTful API endpoints
- **Database**: MongoDB Atlas (document-based storage)
- **Frontend**: Jinja2 templating with Bootstrap 5 and Chart.js
- **Authentication**: Flask sessions with password hashing
- **Styling**: Modern responsive design with gradient backgrounds

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LifePath
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MongoDB**
   - Create a free MongoDB Atlas cluster
   - Get your connection string
   - Copy `.env.example` to `.env` and update with your MongoDB URI

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB connection string and secret key
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## Project Structure

```
LifePath/
├── app.py                 # Main Flask application
├── calculations.py        # Financial calculation functions
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
└── templates/            # Jinja2 templates
    ├── base.html         # Base template with navigation
    ├── home.html         # Landing page
    ├── login.html        # User login
    ├── register.html     # User registration
    ├── dashboard.html    # Main dashboard with charts
    ├── onboarding/       # Three-step onboarding wizard
    │   ├── dream.html    # Step 1: Dream builder
    │   ├── reality.html  # Step 2: Current reality
    │   └── path.html     # Step 3: Path selection
    └── tools/
        └── subscriptions.html # Subscription audit tool
```

## Key Components

### Financial Calculations (`calculations.py`)
- Loan payment calculations using standard amortization formulas
- Annual dream cost aggregation
- Financial gap analysis between dreams and projected income
- Savings timeline calculations with compound interest

### User Data Model
Each user document in MongoDB contains:
```javascript
{
  "username": "string",
  "password_hash": "string", 
  "profile": {
    "dream": {
      "target_city": "string",
      "housing_cost": "number",
      "transportation_cost": "number",
      // ... other lifestyle costs
      "annual_dream_cost": "number" // calculated
    },
    "reality": {
      "monthly_income": "number",
      "expenses": [
        {"category": "string", "amount": "number"}
      ]
    },
    "path": {
      "plan": "college|workforce",
      "college_name": "string", // if college
      "annual_tuition": "number", // if college
      "total_debt": "number", // calculated
      "estimated_loan_payment": "number", // calculated
      "projected_starting_salary": "number"
    }
  }
}
```

### Dashboard Visualizations
- **Master Chart**: Bar chart comparing annual dream cost vs projected salary
- **Monthly Breakdown**: Pie chart showing expense allocation
- **Cash Flow Table**: Detailed monthly income vs expenses analysis
- **Recommendations**: Dynamic suggestions based on financial gap

## Environment Variables

Create a `.env` file with:
```
MONGODB_URI=your_mongodb_connection_string
SECRET_KEY=your_flask_secret_key
FLASK_ENV=development
```

## API Endpoints

- `GET /` - Home page
- `POST /register` - User registration
- `POST /login` - User authentication
- `GET /logout` - User logout
- `GET|POST /onboarding/dream` - Dream builder step
- `GET|POST /onboarding/reality` - Reality check step  
- `GET|POST /onboarding/path` - Path selection step
- `GET /dashboard` - Main dashboard
- `GET /tools/subscriptions` - Subscription audit tool
- `POST /api/expense` - Add expense/subscription
- `DELETE /api/expense/<index>` - Remove expense

## Deployment

The application is designed for easy deployment on platforms like:
- Heroku
- Railway
- Render
- DigitalOcean App Platform

Simply connect your MongoDB Atlas cluster and set the environment variables.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This is a submission to a hackathon. You may read the code but you are not allowed to use it or modify it for any purpose.

## Support

For questions or issues, please open a GitHub issue or contact the development team.
