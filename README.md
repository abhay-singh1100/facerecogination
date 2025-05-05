# Face Recognition Attendance System

A secure and efficient face recognition-based attendance management system built with Flask, OpenCV, and deep learning. The system supports live face detection, liveness detection, and attendance tracking with an administrative interface.

## Features

- Real-time face recognition
- Liveness detection to prevent spoofing
- User registration with face enrollment
- Attendance tracking and reporting
- Administrative dashboard
- CSV export functionality
- Attendance analytics and statistics
- Secure admin authentication

## Prerequisites

- Python 3.11 or higher
- Windows OS (for dlib wheel compatibility)
- Webcam for face detection

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   pip install dlib-19.24.1-cp311-cp311-win_amd64.whl
   ```

## Project Structure

```
├── app.py                 # Main Flask application
├── face_utils.py          # Face recognition and utility functions
├── requirements.txt       # Project dependencies
├── attendance.csv         # Attendance records
├── database.db            # SQLite database for user and attendance data
├── registered_faces/      # Stored face images
├── static/                # Frontend assets
│   ├── index.html         # Updated GUI with analytics section
│   ├── script.js          # JavaScript logic for analytics and Chart.js integration
│   ├── style.css          # Styling for the application
│   └── images/            # Static images
└── README.md              # Project documentation
```

## Usage

1. Start the server:
   ```bash
   python app.py
   ```
2. Access the application at `http://localhost:5000`

### User Registration
- Click "Register" to add a new user
- Enter name and capture face images
- System will enroll the face for future recognition

### Taking Attendance
- Click "Mark Attendance"
- System will verify face and liveness
- Attendance is automatically recorded with timestamp

### Admin Features
- Login with admin credentials
- View attendance reports
- Export attendance data
- Manage registered users
- Manual attendance correction

## Security Features

- Liveness detection to prevent photo/video spoofing
- Admin authentication for sensitive operations
- Session management
- Secure image handling

## New Features Added

### Attendance Analytics
- Added a dedicated endpoint `/attendance_analytics` to calculate and display attendance statistics.
- Displays total users, present count, absent count, and present percentage.
- Integrated **Chart.js** to visualize attendance data in a doughnut chart format.

### Enhanced GUI
- Updated the GUI to include a section for attendance analytics.
- Displays attendance statistics and a dynamic chart for better visualization.

### Liveness Detection
- Improved liveness detection using **Mediapipe's Face Mesh** to detect eye blinks.
- Prevents spoofing by ensuring the detected face is real.

### Export Attendance Data
- Enhanced the CSV export functionality to fetch data directly from the database.
- Ensures compatibility with tools like Excel by formatting the date column correctly.

### Security Enhancements
- Added admin authentication for sensitive operations.
- Improved session management and secure handling of user data.

## How to Use Attendance Analytics

1. Start the server:
   ```bash
   python app.py
   ```
2. Access the application at `http://localhost:5000`.
3. View attendance analytics on the dashboard:
   - Displays total users, present count, absent count, and present percentage.
   - Visualized using a dynamic doughnut chart.

## API Endpoints

- `/register` - Register new users
- `/attendance` - Mark attendance
- `/attendance_log` - View attendance records
- `/attendance_status` - Check daily attendance status
- `/attendance_analytics` - View attendance statistics and analytics.
- `/manual_attendance` - Admin manual attendance marking
- `/users` - Manage registered users
- `/download_attendance` - Export attendance data as CSV.

## Configuration

Default admin credentials (change in production):
- Password: admin123

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License.