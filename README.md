# Wood Vehicle Management System (WVMS)

A web-based application for managing wood vehicles and their measurements.

## Features

- User authentication and authorization
- Vehicle management
- Measurement tracking
- Data export to Excel
- Dark/Light mode
- Responsive design

## Local Development Setup

1. Clone the repository
```bash
git clone <repository-url>
cd WVMS
```

2. Create a virtual environment and activate it
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Initialize the database
```bash
python init_db.py
```

5. Run the development server
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Deployment to Render.com

1. Create a [Render.com](https://render.com) account

2. Create a new Web Service:
   - Connect your GitHub repository
   - Select the Python environment
   - Use the following settings:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn app:app`

3. Add the following environment variables:
   - `FLASK_ENV`: production
   - `SECRET_KEY`: (generate a secure random string)
   - `DATABASE_URL`: (will be automatically added by Render)

4. Deploy the application:
   - Render will automatically deploy your application
   - Any new commits to the main branch will trigger automatic deployments

## Default Admin Account

- Username: admin
- Password: admin

**Important**: Change the admin password after first login!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
