// Icons as functions that return SVG strings
function getIconSVG(iconName, className = "") {
  const icons = {
    'pet-boarding': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 20V14H14V20H19V12H22L12 3L2 12H5V20H10Z" fill="#8B4513"/>
      <path d="M12 3L2 12H5V20H10V14H14V20H19V12H22L12 3Z" fill="#228B22"/>
      <rect x="9" y="14" width="6" height="2" fill="#8B4513"/>
      <rect x="9" y="17" width="6" height="2" fill="#8B4513"/>
    </svg>`,
    'house-sitting': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 20V14H14V20H19V12H22L12 3L2 12H5V20H10Z" fill="#8B4513"/>
      <path d="M12 3L2 12H5V20H10V14H14V20H19V12H22L12 3Z" fill="#228B22"/>
      <circle cx="12" cy="10" r="2" fill="#FFD700"/>
    </svg>`,
    'dog-walking': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z" fill="#333"/>
      <path d="M9 7L8 22H10L11 12L13 12L14 22H16L15 7H9Z" fill="#333"/>
      <path d="M7 10L5 12L7 14L9 12L7 10Z" fill="#4CAF50"/>
      <path d="M17 10L15 12L17 14L19 12L17 10Z" fill="#4CAF50"/>
    </svg>`,
    'pet-daycare': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" fill="#FFD700"/>
      <path d="M12 6V12L16 14" stroke="#333" stroke-width="2" stroke-linecap="round"/>
      <circle cx="12" cy="12" r="2" fill="#333"/>
    </svg>`,
    'pet-grooming': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M9 2L7 6H17L15 2H9Z" fill="#FF69B4"/>
      <path d="M6 8H18V10H6V8Z" fill="#FF69B4"/>
      <path d="M8 10V18H10V10H8Z" fill="#FF69B4"/>
      <path d="M14 10V18H16V10H14Z" fill="#FF69B4"/>
      <path d="M10 12H14V14H10V12Z" fill="#FF1493"/>
    </svg>`,
    'pet-taxi': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M5 11L6.5 6.5H17.5L19 11M5 11H3V13H5V11ZM19 11H21V13H19V11ZM5 13H19V18H5V13Z" fill="#DC143C"/>
      <circle cx="7" cy="18" r="2" fill="#333"/>
      <circle cx="17" cy="18" r="2" fill="#333"/>
      <rect x="6" y="4" width="12" height="3" fill="#333"/>
    </svg>`,
    'facebook': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="24" height="24" rx="4" fill="#1877F2"/>
      <path d="M13.5 8H11.5C10.67 8 10 8.67 10 9.5V11.5H8V14H10V20H13V14H15.5L16 11.5H13V9.5C13 9.22 13.22 9 13.5 9H16V6H13.5C12.12 6 11 7.12 11 8.5V11.5H11Z" fill="white"/>
    </svg>`,
    'google': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="24" height="24" rx="4" fill="white"/>
      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
    </svg>`,
    'x': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="24" height="24" rx="4" fill="#000000"/>
      <path d="M18 6L6 18M6 6L18 18" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    'apple': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="24" height="24" rx="4" fill="#000000"/>
      <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.17 2.08-1.65 3.99-3.74 4.25z" fill="white"/>
    </svg>`,
    'envelope': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="5" width="18" height="14" rx="2" fill="#666"/>
      <path d="M3 7L12 13L21 7" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    'instagram': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="24" height="24" rx="4" fill="url(#instagram-gradient)"/>
      <defs>
        <linearGradient id="instagram-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#833AB4"/>
          <stop offset="50%" stop-color="#FD1D1D"/>
          <stop offset="100%" stop-color="#FCAF45"/>
        </linearGradient>
      </defs>
      <circle cx="12" cy="12" r="4" fill="white"/>
      <circle cx="17" cy="7" r="1" fill="white"/>
    </svg>`,
    'twitter': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="24" height="24" rx="4" fill="#000000"/>
      <path d="M18 8L14 12L18 16M6 8L10 12L6 16" stroke="white" stroke-width="2" stroke-linecap="round"/>
    </svg>`,
    'tiktok': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="24" height="24" rx="4" fill="#000000"/>
      <path d="M12 6C13 6 14 6.5 14.5 7.5M14.5 7.5C15 8.5 15.5 9.5 15.5 11V13C15.5 15.5 13.5 17.5 11 17.5C8.5 17.5 6.5 15.5 6.5 13V11C6.5 8.5 8.5 6.5 11 6.5H12.5" stroke="white" stroke-width="1.5" stroke-linecap="round" fill="none"/>
      <circle cx="17" cy="7" r="1" fill="white"/>
    </svg>`,
    'globe': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" stroke="#666" stroke-width="2" fill="none"/>
      <path d="M2 12H22M12 2C14.5 4.5 16 8 16 12C16 16 14.5 19.5 12 22C9.5 19.5 8 16 8 12C8 8 9.5 4.5 12 2" stroke="#666" stroke-width="1.5" fill="none"/>
    </svg>`,
    'arrow-up': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 19V5M5 12L12 5L19 12" stroke="#667eea" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    'search': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="11" cy="11" r="7" stroke="#81D4FA" stroke-width="2" fill="none"/>
      <path d="M16 16L20 20" stroke="#8B4513" stroke-width="2" stroke-linecap="round"/>
    </svg>`,
    'shield': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L4 5V11C4 16.55 7.16 21.74 12 23C16.84 21.74 20 16.55 20 11V5L12 2Z" fill="#2196F3" stroke="#1976D2" stroke-width="1"/>
      <path d="M9 12L11 14L15 10" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    'credit-card': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="5" width="20" height="14" rx="2" fill="#2196F3"/>
      <rect x="2" y="8" width="20" height="3" fill="#1976D2"/>
      <rect x="4" y="13" width="4" height="2" rx="1" fill="white"/>
      <rect x="4" y="16" width="6" height="2" rx="1" fill="white"/>
    </svg>`,
    'checkmark': `<svg class="${className}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="2" width="20" height="20" rx="4" fill="#4CAF50"/>
      <path d="M7 12L10 15L17 8" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`
  };
  return icons[iconName] || '';
}

// Helper function to insert icon into element
function insertIcon(elementId, iconName, className = "") {
  const element = document.getElementById(elementId);
  if (element) {
    element.innerHTML = getIconSVG(iconName, className);
  }
}


