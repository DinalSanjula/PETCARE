# Pet Care Frontend

A modern, responsive frontend for pet care services similar to PetBacker. This is a testing frontend built with React.

## Features

- 🏠 Service selection (Pet Boarding, House Sitting, Dog Walking, Pet Daycare, Pet Grooming, Pet Taxi)
- 🔍 Location-based search
- 📋 Service provider listings with ratings and reviews
- 🎨 Modern, responsive design
- 🔧 Filter and sort functionality
- 💳 Price display and booking interface
- 📱 Login and Sign Up pages
- 📄 Service-specific landing pages

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation & Running

1. **Install dependencies** (if not already installed):
```bash
npm install
```

2. **Start the development server**:
```bash
npm start
```

3. **Open your browser**:
   - The app will automatically open at [http://localhost:3000](http://localhost:3000)
   - If it doesn't open automatically, manually navigate to `http://localhost:3000`

## Available Pages

- **Homepage** (`/`) - Main landing page with service selection
- **Services Near Me** (`/services-near-me`) - Browse and filter service providers
- **Pet Sitter Jobs** (`/pet-sitter-jobs`) - Information for pet sitters
- **Help Center** (`/help-center`) - FAQ and help section
- **Login** (`/login`) - User login page
- **Sign Up** (`/signup`) - User registration page

### Service Landing Pages

- **Pet Boarding** (`/pet-boarding`)
- **House Sitting** (`/house-sitting`)
- **Dog Walking** (`/dog-walking`)
- **Pet Daycare** (`/pet-daycare`)
- **Pet Grooming** (`/pet-grooming`)
- **Pet Taxi** (`/pet-taxi`)
- **Cat Boarding** (`/cat-boarding`)

## Project Structure

```
src/
├── components/          # Reusable components
│   ├── Header.js       # Navigation header
│   ├── Footer.js       # Footer with links
│   ├── ServiceCard.js  # Service provider card
│   ├── FilterPanel.js  # Filter component
│   └── Icons.js        # SVG icon components
├── pages/              # Page components
│   ├── HomePage.js
│   ├── ServiceProviders.js
│   ├── PetSitterJobs.js
│   ├── ServicesNearMe.js
│   ├── HelpCenter.js
│   ├── Login.js
│   ├── SignUp.js
│   └── ServiceLanding.js  # Service-specific landing pages
├── App.js              # Main app component with routing
└── index.js            # Entry point
```

## Available Scripts

- `npm start` - Runs the app in development mode (opens at http://localhost:3000)
- `npm build` - Builds the app for production
- `npm test` - Launches the test runner

## Technologies Used

- React 18
- React Router DOM v6
- CSS3 (Custom styling)

## Quick Start Guide

### Step 1: Navigate to project directory
```bash
cd "c:\Users\kdile\OneDrive\Desktop\Pet care frantend"
```

### Step 2: Install dependencies (first time only)
```bash
npm install
```

### Step 3: Start the development server
```bash
npm start
```

### Step 4: Open in browser
- The app will automatically open at `http://localhost:3000`
- Or manually visit: `http://localhost:3000`

## Notes

This is a testing frontend with mock data. For production use, you'll need to:
- Connect to a backend API
- Implement authentication
- Add real payment processing
- Integrate with a database

## Troubleshooting

- **Port 3000 already in use**: The app will automatically try the next available port (3001, 3002, etc.)
- **Dependencies not found**: Run `npm install` again
- **Build errors**: Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
