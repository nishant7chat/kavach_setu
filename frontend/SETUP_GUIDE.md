# Kavach Setu Frontend - Setup Guide

## 🎉 What's Been Built

A complete, working frontend for the Kavach Setu insurance claims platform with **real API integration**.

### ✅ Completed Pages

**Landing & Authentication:**
- ✅ `index.html` - Landing page with portal selection
- ✅ `customer/login.html` - Customer login (email/password)
- ✅ `insurer/login.html` - Employee login (employee_id/password)

**Customer Portal:**
- ✅ `customer/dashboard.html` - Dashboard with stats & claims list
- ✅ `customer/submit-claim.html` - Multi-step claim submission form
- ✅ `customer/claim-details.html` - View claim status & details

**Insurer Portal:**
- ✅ `insurer/dashboard.html` - Claims feed with filters

**Shared Assets:**
- ✅ `assets/css/styles.css` - Complete styling system
- ✅ `assets/js/config.js` - API configuration
- ✅ `assets/js/auth.js` - Authentication helpers
- ✅ `assets/js/api.js` - API utilities

## 🚀 Quick Start

### Step 1: Start Backend

```bash
cd d:\00_TEAM_HACKATHON\hackathon-project\backend
python -m uvicorn app.main:app --reload
```

Backend should be running on: `http://localhost:8000`

### Step 2: Open Frontend

Simply open in your browser:
```
d:\00_TEAM_HACKATHON\hackathon-project\frontend\index.html
```

Or right-click → Open with → Chrome/Firefox/Edge

### Step 3: Test the Flow

**Customer Journey:**
1. Click "Customer Portal"
2. Login with:
   - Email: `rajesh.sharma@gmail.com`
   - Password: `password123`
3. View dashboard → See your policies and claims
4. Click "File New Claim"
5. Fill out the 3-step form
6. Submit claim
7. View claim details

**Insurer Journey:**
1. Go back to home → Click "Insurer Portal"
2. Login with:
   - Employee ID: `EMP004`
   - Password: `Kavita@123`
3. View claims feed
4. Filter by status/risk level
5. Click on a claim to review (TODO)

## 📊 API Integration Status

### ✅ Fully Integrated APIs

**Authentication:**
- ✅ `POST /api/v1/auth/customer/login`
- ✅ `POST /api/v1/auth/employee/login`

**Customer APIs:**
- ✅ `GET /api/v1/customer/dashboard`
- ✅ `GET /api/v1/customer/policies`
- ✅ `GET /api/v1/customer/claims`
- ✅ `GET /api/v1/customer/claims/{claim_id}`
- ✅ `POST /api/v1/customer/claims/submit`

**Insurer APIs:**
- ✅ `GET /api/v1/claims/feed`

### 🚧 APIs Ready But Not UI'd Yet

- `POST /api/v1/documents/upload` (document upload)
- `GET /api/v1/documents/verification/{claim_id}` (verification results)
- `POST /api/v1/fraud/{claim_id}/analyze` (trigger AI analysis)
- `GET /api/v1/fraud/{claim_id}/result` (AI results)
- `POST /api/v1/claims/{claim_id}/decision` (approve/reject)
- `POST /api/v1/hospital/verify` (hospital verification)

## 🎨 Design Features

### Color Scheme
- **Primary**: Purple/Blue gradient (#667eea → #764ba2)
- **Success**: Green (#10b981)
- **Warning**: Orange (#f59e0b)
- **Danger**: Red (#ef4444)
- **Info**: Blue (#3b82f6)

### UI Components
- ✅ Responsive navbar with logout
- ✅ Dashboard stat cards
- ✅ Data tables with hover effects
- ✅ Color-coded risk badges (green/orange/red)
- ✅ Status badges with proper colors
- ✅ Toast notifications (success/error)
- ✅ Loading spinners
- ✅ Multi-step form with progress indicator
- ✅ Review page before submission
- ✅ Success animation after claim submit
- ✅ Status timeline visualization
- ✅ Filter system for claims feed

### Mobile Responsive
- ✅ Works on desktop (1920px+)
- ✅ Works on tablets (768px)
- ✅ Works on mobile (375px+)

## 🔐 Authentication Flow

1. User enters credentials
2. Frontend calls `/auth/customer/login` or `/auth/employee/login`
3. Backend returns JWT token
4. Token saved to `localStorage`
5. All subsequent API calls include `Authorization: Bearer {token}` header
6. If 401 response → Auto logout → Redirect to login
7. Logout button → Clear localStorage → Redirect to home

## 📂 File Structure

```
frontend/
├── index.html                      # ✅ Landing page
│
├── customer/
│   ├── login.html                  # ✅ Customer login
│   ├── dashboard.html              # ✅ Dashboard with stats
│   ├── submit-claim.html           # ✅ 3-step claim form
│   └── claim-details.html          # ✅ Claim status page
│
├── insurer/
│   ├── login.html                  # ✅ Employee login
│   ├── dashboard.html              # ✅ Claims feed
│   └── claim-review.html           # 🚧 TODO: Review page with AI
│
├── assets/
│   ├── css/
│   │   └── styles.css              # ✅ Complete CSS framework
│   └── js/
│       ├── config.js               # ✅ API endpoints
│       ├── auth.js                 # ✅ Auth helpers
│       └── api.js                  # ✅ Fetch utilities
│
├── README.md                        # ✅ General docs
└── SETUP_GUIDE.md                   # ✅ This file
```

## 🧪 Test Credentials

### Customer Accounts
| Email | Password | Name |
|-------|----------|------|
| rajesh.sharma@gmail.com | password123 | Rajesh Kumar Sharma |
| priya.patel@yahoo.com | password123 | Priya Patel |
| amit.singh@outlook.com | password123 | Amit Singh |
| sneha.reddy@gmail.com | password123 | Sneha Reddy |
| vikram.mehta@gmail.com | password123 | Vikram Mehta |

### Employee Accounts
| Employee ID | Password | Name | Role |
|-------------|----------|------|------|
| EMP001 | Nishant@123 | Nishant Chaturvedi | Senior Underwriter |
| EMP002 | Ritikesh@123 | Ritikesh Choube | Underwriter |
| EMP003 | Adhish@123 | Adhish Deshpande | Underwriter |
| EMP004 | Kavita@123 | Kavita Jain | Admin |

## 🎯 Next Steps (Optional Extensions)

### High Priority
1. **Claim Review Page** (`insurer/claim-review.html`)
   - Show all claim details
   - Display 4 AI agent analysis results
   - Hospital verification panel
   - Approve/Reject/Escalate buttons

2. **Document Upload UI** (add to `claim-details.html`)
   - File picker for each document type
   - Upload progress bars
   - Verification status indicators
   - Face/signature match results

### Medium Priority
3. **Real-time Updates**
   - Poll AI analysis status
   - Show progress indicators
   - Auto-refresh when complete

4. **Dashboard Enhancements**
   - Charts/graphs for stats
   - Recent activity feed
   - Quick actions panel

### Low Priority
5. **Advanced Features**
   - Notifications system
   - Search/filter claims
   - Export reports
   - Bulk operations

## 🐛 Troubleshooting

### Issue: CORS Error
**Solution**: Ensure backend has CORS configured:
```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    ...
)
```

### Issue: 401 Unauthorized
**Solution**:
1. Check if you're logged in
2. Try logging out and back in
3. Check browser console for token
4. Verify backend is running

### Issue: Cannot read property 'formatCurrency'
**Solution**: Ensure all JS files are loaded in correct order:
```html
<script src="../assets/js/config.js"></script>
<script src="../assets/js/auth.js"></script>
<script src="../assets/js/api.js"></script>
```

### Issue: API returns 404
**Solution**: Check API endpoint in `config.js` matches your backend routes

### Issue: Blank Page
**Solution**:
1. Open browser console (F12)
2. Check for JavaScript errors
3. Verify file paths are correct
4. Make sure backend is running

## 🔧 Configuration

### Change API Base URL

Edit `assets/js/config.js`:
```javascript
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000/api/v1',  // ← Change this
    ...
};
```

### Add New API Endpoint

1. Add to `config.js`:
```javascript
API_CONFIG.NEW_MODULE = {
    ENDPOINT_NAME: '/path/to/endpoint'
};
```

2. Use in your page:
```javascript
const data = await api.call(
    getApiUrl(API_CONFIG.NEW_MODULE.ENDPOINT_NAME),
    { method: 'GET' }
);
```

## 📝 Code Examples

### Making an API Call
```javascript
try {
    api.showLoading('Loading...');

    const data = await api.call(
        getApiUrl(API_CONFIG.CUSTOMER.CLAIMS) + '?limit=10',
        { method: 'GET' }
    );

    api.hideLoading();
    // Use data...

} catch (error) {
    api.hideLoading();
    api.showError('Failed to load data');
}
```

### Checking Authentication
```javascript
// Require auth (will redirect to login if not authenticated)
if (!auth.requireAuth()) {
    // User will be redirected
}

// Check manually
if (auth.isAuthenticated()) {
    // User is logged in
}
```

### Showing Notifications
```javascript
api.showSuccess('Claim submitted!');
api.showError('Something went wrong');
api.showToast('Info message', 'info');
```

### Formatting Data
```javascript
utils.formatCurrency(144000); // ₹1,44,000
utils.formatDate('2025-11-29'); // 29 Nov 2025
utils.getRiskBadge('high'); // <span class="badge badge-danger">High Risk</span>
utils.getStatusBadge('approved'); // <span class="badge badge-success">Approved</span>
```

## 🎓 Learning Resources

- **HTML/CSS/JS Basics**: [MDN Web Docs](https://developer.mozilla.org/)
- **Fetch API**: [MDN Fetch Guide](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- **LocalStorage**: [MDN Storage Guide](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)

## 📄 License

Built for Kavach Setu Hackathon Project

---

**Need Help?** Check the browser console (F12) for errors and debug information!
