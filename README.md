# EngBoost Backend

A modern and efficient backend for the EngBoost language learning application, providing API services for flashcard management, user authentication, and other core features.

## Overview

EngBoost is a language learning platform designed to help users improve their English vocabulary through flashcards. This repository contains the backend code, built with Python, Flask, and MongoDB.

## Features

- 👤 **User Authentication System**

  - Registration, login, and account verification
  - JWT-based authentication
  - Role-based access control

- 📂 **Folder Management**

  - Create, update, and delete folders
  - View public/private folders
  - Organize flashcards into collections

- 📇 **Flashcard System**

  - Create and manage flashcards with English/Vietnamese translations
  - Support for images (stored via Cloudinary)
  - Bulk import functionality

- 🔒 **Security**
  - CORS support for cross-domain requests
  - Protected API endpoints
  - Input validation and error handling

## Tech Stack

- **Language**: Python
- **Framework**: Flask
- **Database**: MongoDB
- **Authentication**: JWT (JSON Web Tokens)
- **Image Storage**: Cloudinary
- **Validation**: Pydantic

## Project Structure

```
engboost-backend/
├── src/
│   ├── app.py                # Main application entry point
│   ├── config/               # Configuration files
│   ├── middleware/           # Authentication and error handlers
│   ├── models/               # Database models
│   ├── repositories/         # Business logic and data access
│   ├── resources/            # API endpoints and controllers
│   ├── routes/               # Route definitions
│   ├── utils/                # Helper functions and utilities
│   └── validation/           # Request validation schemas
```

## API Endpoints

### User Management

- `POST /api/register` - Register a new user
- `PUT /api/verify` - Verify user account
- `POST /api/login` - User login
- `DELETE /api/logout` - User logout
- `GET /api/refresh_token` - Refresh authentication token
- `PUT /api/users` - Update user information

### Folder Management

- `POST /api/folders` - Create a new folder
- `GET /api/folders` - Get all folders for current user
- `GET /api/folders/:folder_id` - Get folder by ID
- `PUT /api/folders/:folder_id` - Update folder
- `DELETE /api/folders/:folder_id` - Delete folder

### Flashcard Management

- `POST /api/flashcards/save-to-folder` - Save flashcards to a folder
- `GET /api/folders/:folder_id/flashcards` - Get flashcards by folder
- `GET /api/flashcards/:flashcard_id` - Get flashcard by ID
- `DELETE /api/flashcards/:flashcard_id` - Delete flashcard

## Getting Started

### Prerequisites

- Python 3.9+
- MongoDB
- Cloudinary account (for image storage)

### Installation

1. Clone the repository

   ```bash
   git clone https://github.com/your-username/engboost-backend.git
   cd engboost-backend
   ```

2. Create a virtual environment

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables
   Create a `.env` file with the following variables:

   ```
   MONGODB_URI=your_mongodb_uri
   ACCESS_TOKEN_SECRET=your_jwt_secret
   REFRESH_TOKEN_SECRET=your_refresh_token_secret
   CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
   CLOUDINARY_API_KEY=your_cloudinary_api_key
   CLOUDINARY_API_SECRET=your_cloudinary_api_secret
   ```

5. Run the application
   ```bash
   python src/app.py
   ```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [PyMongo](https://pymongo.readthedocs.io/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Cloudinary](https://cloudinary.com/)
- [JWT](https://jwt.io/)
