# API Documentation

This document provides detailed information about the Face Recognition Attendance System's REST API endpoints.

## Authentication

Some endpoints require admin authentication. Use the login endpoint to obtain a session.

### Login
```
POST /login
```
Request body:
```json
{
    "password": "string"
}
```
Response:
```json
{
    "success": true
}
```

## User Management

### Register User
```
POST /register
```
Request body:
```json
{
    "name": "string",
    "image": "base64_encoded_image"
}
```
Response:
```json
{
    "success": true,
    "message": "string"
}
```

### List Users
```
GET /users
```
Response:
```json
{
    "users": [
        {
            "name": "string",
            "image": "string"
        }
    ]
}
```

### Delete User
```
DELETE /user/<name>
```
Response:
```json
{
    "success": true,
    "message": "string"
}
```

## Attendance Management

### Mark Attendance
```
POST /attendance
```
Request body:
```json
{
    "images": ["base64_encoded_image"]
}
```
Response:
```json
{
    "success": true,
    "names": ["string"],
    "details": [
        {
            "name": "string",
            "liveness": true,
            "box": [number, number, number, number]
        }
    ]
}
```

### Get Attendance Log
```
GET /attendance_log
```
Response:
```json
{
    "records": [
        {
            "name": "string",
            "date": "YYYY-MM-DD",
            "time": "HH:MM:SS",
            "status": "present|absent"
        }
    ]
}
```

### Get Attendance Status
```
GET /attendance_status?date=YYYY-MM-DD
```
Response:
```json
{
    "date": "YYYY-MM-DD",
    "status": {
        "user1": "present",
        "user2": "absent"
    }
}
```

### Manual Attendance (Admin only)
```
POST /manual_attendance
```
Request body:
```json
{
    "name": "string",
    "date": "YYYY-MM-DD",
    "status": "present|absent"
}
```
Response:
```json
{
    "success": true,
    "message": "string"
}
```

## Analytics

### Get Attendance Analytics
```
GET /attendance_analytics?date=YYYY-MM-DD
```
Response:
```json
{
    "date": "YYYY-MM-DD",
    "total": number,
    "present": number,
    "absent": number,
    "percent": number,
    "status": {
        "user1": "present",
        "user2": "absent"
    }
}
```

## Data Export

### Download Attendance Records
```
GET /download_attendance?date=YYYY-MM-DD
```
Returns a CSV file with attendance records.

## Error Responses

All endpoints may return error responses in the following format:
```json
{
    "success": false,
    "error": "error message"
}
```