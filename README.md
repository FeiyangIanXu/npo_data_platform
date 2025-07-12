# WRDS-Style Nonprofit Organization Data Query System

## 🎯 Project Overview

This is a professional nonprofit organization data query platform, designed with a step-by-step query process similar to WRDS (Wharton Research Data Services), providing intuitive and efficient data filtering and export functions.

## ✨ Core Features

### 🔄 Five-Step Query Process

1. **Year Selection** - Choose the data year to query (2022-2024)
2. **Scope Filtering** - Filter by location, financial scale, and operational scale
3. **Precise Targeting** - Select all or search for specific organizations
4. **Variable Selection** - 164 fields categorized for selection
5. **Data Export** - Export in Excel, CSV, or JSON format

### 🌍 Filtering Functions

- **Location**: 33 states, 172 cities
- **Financial Scale**: Filter by total revenue and total assets
- **Operational Scale**: Independent Living Units (ILU), Assisted Living Units (ALU)
- **Precise Search**: Search by organization name or EIN number

### 📊 Data Scale

- **Number of Organizations**: 201 nonprofits
- **Data Fields**: 164 fields
- **Coverage**: 33 states, 172 cities
- **Time Span**: 2022-2024

## 🚀 Quick Start

### One-Click Start (Recommended)

```bash
# Double-click start.bat
```
Or run manually:
```bash
start.bat
```

### Manual Start

If auto start fails, you can start manually:

1. **Start Backend**
   ```bash
   cd backend
   .venv\Scripts\python.exe main.py
   ```

2. **Start Frontend**
   ```bash
   cd frontend/vite-project
   npm run dev
   ```

## 🌐 Access URLs

- **Frontend App**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLite** - Lightweight database
- **SQLAlchemy** - ORM framework
- **Pandas** - Data processing

### Frontend
- **React 18** - UI framework
- **Ant Design** - UI component library
- **Vite** - Build tool
- **Axios** - HTTP client

## 📋 API Endpoints

### Core Query APIs
- `GET /api/available-years` - Get available years
- `GET /api/available-states` - Get available states
- `GET /api/available-cities` - Get available cities
- `GET /api/field-info` - Get field info
- `POST /api/step1-filter` - Scope filtering
- `POST /api/step2-filter` - Precise targeting
- `POST /api/final-query` - Final query

### Data Export API
- `POST /api/export` - Data export (XLSX/CSV/JSON)

## 🎨 User Experience Highlights

### WRDS-Style Design
- **Professional Interface** - Academic database look
- **Step-by-Step Guidance** - Clear step indicators and instructions
- **Smart Tips** - Rich help info and data stats
- **Flexible Filtering** - Multi-level, multi-dimensional filters

### Usability Optimization
- **Bilingual UI** - Friendly translation of professional terms
- **Real-Time Feedback** - Instant result stats
- **Error Tolerance** - Smart handling of user input errors
- **Reset Function** - One-click restart query

## 📁 Project Structure

```
npo_data_platform/
├── backend/                 # Backend service
│   ├── main.py             # FastAPI main program
│   ├── requirements.txt    # Python dependencies
│   ├── irs.db             # SQLite database
│   └── .venv/             # Virtual environment
├── frontend/               # Frontend app
│   └── vite-project/
│       ├── src/
│       │   └── pages/
│       │       └── QueryForm.jsx  # WRDS query UI
│       └── package.json
├── start.bat               # One-click start script
├── test_system.py          # System test script
└── README.md              # Project documentation
```

## 🔧 Development Guide

### Requirements
- Python 3.8+
- Node.js 16+
- Modern browser

### Install Dependencies

**Backend**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend**
```bash
cd frontend/vite-project
npm install
```

### Development Mode
```bash
# Backend development
cd backend
.venv\Scripts\python.exe main.py

# Frontend development
cd frontend/vite-project
npm run dev
```

## 🧪 Testing

Run system test:
```bash
python test_system.py
```

Test includes:
- Backend health check
- Frontend connection test
- API endpoint function test
- Port occupation check

## 🐛 Troubleshooting

### Common Issues

**Q: Frontend shows blank page?**
A: Check if backend is running and API connection is normal

**Q: Backend fails to start?**
A: Check Python version and dependencies

**Q: Port is occupied?**
A: Use `netstat -ano | findstr :8000` to check port occupation

### Get Help

1. Run `test_system.py` to check system status
2. Check console error messages
3. Check network and firewall settings

## 📈 Future Plans

### Feature Enhancements
- [ ] Advanced filter conditions
- [ ] Query template saving
- [ ] Data visualization charts
- [ ] Peer comparison analysis

### Technical Optimization
- [ ] Big data query optimization
- [ ] Caching system
- [ ] User permission management
- [ ] API performance monitoring

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

Welcome to submit Issues and Pull Requests!

---

## Data Requirement

Please note: The source data files (First100.xlsx, nonprofits_100.csv) and the generated database (irs.db) are proprietary and are not included in this repository. To run the data pipeline (data_pipeline.py), you must provide your own source data and place it in the backend/data/ directory. The pipeline is designed to process a file with a specific multi-line header structure as detailed in the script.

---

**🎉 Enjoy the WRDS-style data query experience!** 