# Face Matching Gateway - Complete Website

A modern, responsive web interface for the Face Matching Gateway API, built with FastAPI backend and vanilla JavaScript frontend.

## 🚀 Features

- **Modern UI/UX**: Clean, responsive design with smooth animations
- **Selective Authentication**: API key required only for registration and user management
- **Public Verification**: Face verification available without authentication
- **Face Registration**: Upload and register new faces (requires auth)
- **Face Verification**: Verify faces against registered users (public)
- **User Management**: View, search, and delete registered users (requires auth)
- **Search Functionality**: Search users by name or ID in real-time
- **Real-time Feedback**: Toast notifications and response modals
- **Drag & Drop**: Easy file upload with drag and drop support
- **Mobile Friendly**: Fully responsive design

## 📋 Prerequisites

- Python 3.8+
- FastAPI
- ONNX Runtime
- Supabase account (for database)
- Triton Inference Server (optional, for GPU inference)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd scalable_face_matching_gateway
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file with your configuration:
   ```env
   SUPABASE_URL=your-supabase-url
   SUPABASE_KEY=your-supabase-key
   ADMIN_API_KEY=your-admin-api-key
   TRITON_SERVER_URL=localhost:8001
   ```

4. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🌐 Accessing the Website

Once the server is running, access the website at:
```
http://localhost:8000/web
```

## 🔐 Authentication

The website requires API key authentication to access protected endpoints:

### Available API Keys (from .env):
- **Frontend Key**: `secret-frontend-key` (for web interface)
- **Camera Key**: `secret-camera-key` (for edge cameras)

### How to Authenticate:
1. Click the **"Authenticate"** button in the top navigation
2. Enter your API key or use the preset buttons
3. Click **"Authenticate"**
4. The button will turn green when authenticated

## 📖 Usage Guide

### 1. Home Page
- Overview of the face matching system
- Quick access to main features
- Feature highlights and call-to-action buttons

### 2. Register New Face (Requires Authentication)
1. Navigate to the **"Register"** section
2. Ensure you're authenticated (green button in top nav)
3. Enter the person's name
4. Upload a clear face image (JPG, PNG, JPEG)
5. Click **"Register Face"**
6. View the response in the modal

### 3. Verify Face (Public - No Authentication Required)
1. Navigate to the **"Verify"** section
2. Upload a face image to verify
3. Optionally specify a Person ID to verify against a specific user
4. Click **"Verify Face"**
5. View verification results with similarity scores

### 4. Manage Users (Requires Authentication)
1. Navigate to the **"Manage"** section
2. Ensure you're authenticated (green button in top nav)
3. Click **"Refresh Users"** to load the current user list
4. **Search users** by typing in the search box (searches by name or ID)
5. View all registered users with their details
6. Click **"Delete"** to remove a user (confirmation required)

## 🎨 Website Structure

```
static/
├── index.html          # Main HTML file
├── css/
│   └── style.css       # Complete styling
└── js/
    └── app.js          # Frontend application logic
```

## 🔧 API Endpoints Used

The website interacts with these FastAPI endpoints:

- `GET /users` - List all registered users
- `POST /register` - Register a new face
- `POST /verify` - Verify a face
- `DELETE /person/{id}` - Delete a user

All endpoints require the `X-API-Key` header for authentication.

## 📱 Responsive Design

The website is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

## 🛡️ Security Features

- API key authentication required for all operations
- Input validation on frontend
- Secure file upload handling
- CSRF protection through API keys
- Error handling with user-friendly messages

## � Data Handling

- **Pagination Support**: Automatically handles large datasets (>1000 users)
- **Memory Efficient**: Loads all user data into memory for fast verification
- **Sorted Data**: Users are sorted by ID for consistent ordering
- **Error Recovery**: Graceful handling of missing or corrupted data

## �🚀 Production Deployment

For production deployment:

1. **Use HTTPS** for secure communication
2. **Change API keys** to strong, random values
3. **Set up proper CORS** if needed
4. **Configure rate limiting** on the API
5. **Use environment-specific configurations**

## 🐛 Troubleshooting

### Common Issues:

1. **401 Unauthorized**: Check your API key in the authentication modal
2. **Network Error**: Ensure the FastAPI server is running
3. **File Upload Issues**: Check file size (max 10MB) and format
4. **Face Detection Failed**: Ensure clear, well-lit face images

### Debug Mode:
- Open browser developer tools (F12)
- Check the Console tab for JavaScript errors
- Check the Network tab for API request/response details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Check the API documentation at `http://localhost:8000/docs`
- Review the FastAPI logs for backend errors
- Check browser console for frontend errors

---

**Happy face matching! 🎭**