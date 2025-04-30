# EduFeeTrack

**EduFeeTrack** is an automated student fee tracking system designed to streamline fee management for educational institutions, with a focus on Kampala International University (KIU) in Uganda. It replaces error-prone manual processes (e.g., spreadsheets, paper records) with a digital solution that automates fee tracking, fine application, and notifications. The **EduFeeTrack** integration is the core feature, enabling automated fine enforcement and transparent financial reporting.

This codebase uses **Bootstrap 5.3.0** (via CDN) for the frontend, **Flask (Python)** for the backend, and **SQLite** for the database, reflecting the system before adopting Material-UI.

## Features
- **Fee Tracking**: Record and update student fees, payments, and balances.
- **Fine Automation (EduFeeTrack)**: Automatically apply fines for overdue payments based on configurable rules (amount, frequency, semester start).
- **Notifications**: Simulated via flash messages (email integration planned).
- **Reporting**: Generate PDF reports for payment and fine histories using ReportLab.
- **Security**: Role-based access with login authentication.
- **Responsive UI**: Bootstrap-based interface with cards, tables, and forms.

## Architecture
EduFeeTrack follows a **client-server**, layered architecture:

1. **Presentation Layer (Frontend)**:
   - **Tech**: Bootstrap 5.3.0 (CDN), Jinja2 templates, custom CSS/JS.
   - **Role**: Provides a responsive UI with pages for login, dashboard, student management, financial details, payment history, and EduFeeTrack configuration.
   - **EduFeeTrack**: The configuration page (`edufeetrack_config.html`) allows admins to set fine rules, driving automation.

2. **Application Layer (Backend)**:
   - **Tech**: Flask 2.0.1.
   - **Role**: Handles routes (`app.py`), session management, and business logic.
   - **EduFeeTrack**: The `/edufeetrack_config` route updates fine settings and applies fines, integrating with financial and reporting routes.

3. **Data Layer**:
   - **Tech**: SQLite (`edufeetrack.db`).
   - **Role**: Stores student, payment, fine, and configuration data.
   - **EduFeeTrack**: Uses `FeeFine` and `Config` tables for fine automation and settings persistence.

4. **Report Generation**:
   - **Tech**: ReportLab 3.6.12.
   - **Role**: Creates PDF reports in `reports/`.
   - **EduFeeTrack**: Includes fine data in reports for transparency


## What EduFeeTrack Does
The system automates fee management with the **EduFeeTrack** integration as its core:
- **Fee Tracking**: Admins add students and fees, track payments, and view balances.
- **Fine Automation**: Configures and applies fines (e.g., $50 monthly) for unpaid balances, stored in the `FeeFine` table.
- **Notifications**: Simulates reminders (future email integration planned).
- **Reporting**: Generates PDF reports listing payments and fines.
- **Example**: A student with a $1000 fee misses a payment; `EduFeeTrack` applies a $50 fine, updates the balance, and includes it in reports.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/EduFeeTrack.git
   cd EduFeeTrack





Create a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate



Install dependencies:

pip install -r requirements.txt



Run the application:

python app.py



Access at http://localhost:5000.

Usage





Login: Use admin/password (replace with secure credentials in production).



Dashboard: View students or navigate to actions.



Add Student: Enter student details and fees.



Financial Details: Record payments, view balances, and fines.



Payment History: List transactions and generate PDF reports.



EduFeeTrack Config: Set fine amount, frequency, and semester start to automate fines.

Dependencies





Flask==2.0.1



ReportLab==3.6.12



SQLite (built-in with Python)

Limitations





Hardcoded authentication (replace with Flask-Login).



Simulated notifications (no email yet).



Manual fine application (needs a scheduler).



SQLite limits scalability for large institutions.

Future Enhancements





Add a scheduler for automatic fines (e.g., APScheduler).



Implement email notifications (e.g., smtplib).



Enhance security with proper authentication.



Upgrade to PostgreSQL for larger deployments.

License

MIT License

Contact

For issues or contributions, open a GitHub issue or contact [mwiined@gmail.com].
