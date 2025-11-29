# Kavach Setu - Frontend

Enterprise-grade insurance claims processing portal with clean, professional UI.

## 🚀 Quick Start

### Prerequisites
- Backend API running on `http://localhost:8000`
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Running the Frontend

1. **Open the landing page:**
   ```
   frontend/index.html
   ```
   Simply double-click or open in your browser.

2. **Choose your portal:**
   - **Customer Portal**: For policyholders to file and track claims
   - **Insurer Portal**: For underwriters to review and approve claims

### Test Credentials

**Customer Portal:**
- Email: `rajesh.sharma@gmail.com`
- Password: `password123`

**Insurer Portal:**
- Employee ID: `EMP004`
- Password: `Kavita@123`

## 📁 Project Structure

```
frontend/
├── index.html                  # Landing page
├── customer/
│   ├── login.html             # Customer login
│   ├── dashboard.html         # Customer dashboard
│   ├── submit-claim.html      # File new claim
│   └── claim-details.html     # View claim status
├── insurer/
│   ├── login.html             # Employee login
│   ├── dashboard.html         # Claims feed
│   └── claim-review.html      # Review claim + AI analysis
├── assets/
│   ├── css/
│   │   └── styles.css         # Global styles
│   └── js/
│       ├── config.js          # API endpoints configuration
│       ├── auth.js            # Authentication helpers
│       └── api.js             # API call utilities
└── README.md
```

## 🎨 Design System

### Color Palette
- **Primary**: Purple/Blue gradient (#667eea → #764ba2)
- **Success**: Green (#10b981)
- **Warning**: Orange (#f59e0b)
- **Danger**: Red (#ef4444)
- **Info**: Blue (#3b82f6)

### Components
- Clean card-based layouts
- Responsive grid system
- Toast notifications
- Loading spinners
- Status badges
- Form controls

## 🔌 API Integration

All API calls are configured in `assets/js/config.js`:

### Customer APIs
- `POST /auth/customer/login` - Login
- `GET /customer/dashboard` - Dashboard stats
- `GET /customer/policies` - List policies
- `POST /customer/claims/submit` - Submit claim
- `POST /documents/upload` - Upload documents
- `GET /customer/claims/{claim_id}` - Claim details

### Insurer APIs
- `POST /auth/employee/login` - Employee login
- `GET /claims/feed` - All claims feed
- `GET /claims/{claim_id}` - Claim details
- `POST /fraud/{claim_id}/analyze` - Trigger AI analysis
- `GET /fraud/{claim_id}/result` - Get AI results
- `POST /claims/{claim_id}/decision` - Submit decision

## 🛠️ Development

### No Build Required!
This frontend uses vanilla HTML/CSS/JavaScript - no webpack, npm, or build tools needed.

### Making Changes

1. **Update API Base URL** (if needed):
   ```javascript
   // assets/js/config.js
   const API_CONFIG = {
       BASE_URL: 'http://localhost:8000/api/v1',  // Change this
       ...
   };
   ```

2. **Add New API Endpoint**:
   ```javascript
   // assets/js/config.js
   API_CONFIG.NEW_MODULE = {
       ENDPOINT_NAME: '/path/to/endpoint'
   };
   ```

3. **Make API Call**:
   ```javascript
   const data = await api.call(
       getApiUrl(API_CONFIG.MODULE.ENDPOINT, { param: value }),
       {
           method: 'POST',
           body: JSON.stringify({ ... })
       }
   );
   ```

### Authentication Flow

1. User logs in → Token saved to `localStorage`
2. All subsequent API calls include `Authorization: Bearer {token}` header
3. 401 responses → Auto logout and redirect to login
4. Logout → Clear localStorage and redirect to home

## 📱 Features

### Customer Portal
- ✅ Login with email/password
- ✅ Dashboard with stats
- 🚧 Submit new claim (multi-step form)
- 🚧 Upload documents (Aadhaar, PAN, Photo, etc.)
- 🚧 View claim status and AI analysis results
- 🚧 Track verification status

### Insurer Portal
- ✅ Login with employee ID/password
- 🚧 Claims feed with risk-based color coding
- 🚧 Detailed claim review page
- 🚧 View 4 AI agent analysis results
- 🚧 Hospital verification integration
- 🚧 Approve/Reject/Escalate decisions

Legend: ✅ Completed | 🚧 In Progress

## 🎯 Next Steps

1. Complete customer dashboard page
2. Build claim submission form
3. Implement document upload UI
4. Create insurer dashboard with claims feed
5. Build claim review page with AI analysis display

## 🐛 Troubleshooting

**Issue**: API calls fail with CORS error
**Solution**: Ensure backend has CORS middleware configured for `http://localhost:*`

**Issue**: 401 Unauthorized errors
**Solution**: Check if token is valid. Try logging out and logging in again.

**Issue**: "Cannot read property of undefined"
**Solution**: Check browser console for errors. Ensure API is running.

## 📄 License

Built for Kavach Setu Hackathon Project
