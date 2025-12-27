// Navigation functions
function navigateToService(servicePath) {
    if (window.location.pathname.includes('pages')) {
        window.location.href = `${servicePath}.html`;
    } else {
        window.location.href = `pages/${servicePath}.html`;
    }
}

function handleSearch() {
    const service = document.getElementById('serviceSelect')?.value || '';
    const location = document.getElementById('locationInput')?.value || '';
    
    const basePath = window.location.pathname.includes('pages') ? 'services-near-me.html' : 'pages/services-near-me.html';
    if (service && location) {
        window.location.href = `${basePath}?service=${service}&location=${location}`;
    } else {
        window.location.href = basePath;
    }
}

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Service provider data
const mockProviders = [
    {
        id: 1,
        name: 'Amanda\'s Pet Care',
        service: 'boarding',
        location: 'Kandy, Central Province',
        rating: 4.8,
        reviews: 127,
        price: 1500,
        image: '/images/1.jpg',
        description: 'Experienced pet sitter with 5+ years of caring for dogs and cats.'
    },
    {
        id: 2,
        name: 'Happy Paws Grooming',
        service: 'grooming',
        location: 'Kandy, Central Province',
        rating: 4.9,
        reviews: 89,
        price: 2000,
        image: '/images/18.jpg',
        description: 'Professional grooming services for all breeds.'
    },
    {
        id: 3,
        name: 'Walk & Play',
        service: 'walking',
        location: 'Kandy, Central Province',
        rating: 4.7,
        reviews: 203,
        price: 800,
        image: '/images/6.jpg',
        description: 'Daily dog walking and exercise services.'
    },
    {
        id: 4,
        name: 'Home Pet Boarding',
        service: 'boarding',
        location: 'Kandy, Central Province',
        rating: 4.6,
        reviews: 156,
        price: 1800,
        image: '/images/4.jpg',
        description: 'Cage-free home boarding for your beloved pets.'
    },
    {
        id: 5,
        name: 'Pet Taxi Services',
        service: 'taxi',
        location: 'Kandy, Central Province',
        rating: 4.5,
        reviews: 67,
        price: 1200,
        image: '/images/3.jpg',
        description: 'Safe and reliable pet transportation.'
    },
    {
        id: 6,
        name: 'Daycare Delight',
        service: 'daycare',
        location: 'Kandy, Central Province',
        rating: 4.8,
        reviews: 94,
        price: 1300,
        image: '/images/10.jpg',
        description: 'Fun-filled daycare for your pets.'
    }
];

// Render stars
function renderStars(rating) {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < fullStars; i++) {
        stars.push('<span class="star filled">★</span>');
    }
    if (hasHalfStar) {
        stars.push('<span class="star half">★</span>');
    }
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
        stars.push('<span class="star">★</span>');
    }
    return stars.join('');
}

// Get service name
function getServiceName(serviceId) {
    const services = {
        boarding: 'Pet Boarding',
        sitting: 'House Sitting',
        walking: 'Dog Walking',
        daycare: 'Pet Daycare',
        grooming: 'Pet Grooming',
        taxi: 'Pet Taxi'
    };
    return services[serviceId] || serviceId;
}

// Render service card
function renderServiceCard(provider) {
    return `
        <div class="service-card-provider" onclick="viewServiceDetail(${provider.id})">
            <div class="card-image">
                <img src="${provider.image}" alt="${provider.name}" />
                <div class="service-badge">${getServiceName(provider.service)}</div>
            </div>
            <div class="card-content">
                <h3 class="provider-name">${provider.name}</h3>
                <div class="provider-location">📍 ${provider.location}</div>
                <div class="provider-rating">
                    <div class="stars">${renderStars(provider.rating)}</div>
                    <span class="rating-value">${provider.rating}</span>
                    <span class="reviews-count">(${provider.reviews} reviews)</span>
                </div>
                <p class="provider-description">${provider.description}</p>
                <div class="card-footer">
                    <div class="price">
                        <span class="price-amount">Rs. ${provider.price.toLocaleString()}</span>
                        <span class="price-period"> /day</span>
                    </div>
                    <button class="book-btn">View Details</button>
                </div>
            </div>
        </div>
    `;
}

// Filter providers
function filterProviders(service, location, sortBy = 'review') {
    let filtered = [...mockProviders];
    
    if (service) {
        filtered = filtered.filter(p => p.service === service);
    }
    
    if (location) {
        filtered = filtered.filter(p => 
            p.location.toLowerCase().includes(location.toLowerCase())
        );
    }
    
    if (sortBy === 'review') {
        filtered.sort((a, b) => b.rating - a.rating);
    } else if (sortBy === 'price') {
        filtered.sort((a, b) => a.price - b.price);
    }
    
    return filtered;
}

// View service detail
function viewServiceDetail(id) {
    const basePath = window.location.pathname.includes('pages') ? 'service-detail.html' : 'pages/service-detail.html';
    window.location.href = `${basePath}?id=${id}`;
}

// Get URL parameters
function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    return {
        service: params.get('service') || '',
        location: params.get('location') || '',
        id: params.get('id') || ''
    };
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Set search values from URL params
    const params = getUrlParams();
    
    if (params.service && document.getElementById('serviceSelect')) {
        document.getElementById('serviceSelect').value = params.service;
    }
    
    if (params.location && document.getElementById('locationInput')) {
        document.getElementById('locationInput').value = params.location;
    }
    
    // Render providers if on services-near-me page
    if (document.querySelector('.providers-grid')) {
        const providers = filterProviders(params.service, params.location);
        const grid = document.querySelector('.providers-grid');
        if (grid) {
            if (providers.length > 0) {
                grid.innerHTML = providers.map(p => renderServiceCard(p)).join('');
            } else {
                grid.innerHTML = `
                    <div class="no-results">
                        <p>No services found matching your criteria.</p>
                        <button onclick="clearFilters()">Clear Filters</button>
                    </div>
                `;
            }
        }
    }
    
    // Handle sort change
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const params = getUrlParams();
            const providers = filterProviders(params.service, params.location, this.value);
            const grid = document.querySelector('.providers-grid');
            if (grid) {
                grid.innerHTML = providers.map(p => renderServiceCard(p)).join('');
            }
        });
    }
});

// Clear filters
function clearFilters() {
    const basePath = window.location.pathname.includes('pages') ? 'services-near-me.html' : 'pages/services-near-me.html';
    window.location.href = basePath;
}

// Toggle filter panel
function toggleFilters() {
    const panel = document.getElementById('filterPanel');
    if (panel) {
        panel.style.display = panel.style.display === 'none' ? 'grid' : 'none';
    }
}

// Toggle view mode
function toggleViewMode() {
    const viewMode = localStorage.getItem('viewMode') || 'list';
    const newMode = viewMode === 'list' ? 'map' : 'list';
    localStorage.setItem('viewMode', newMode);
    
    const listView = document.querySelector('.providers-grid');
    const mapView = document.querySelector('.map-placeholder');
    
    if (newMode === 'list') {
        if (listView) listView.style.display = 'grid';
        if (mapView) mapView.style.display = 'none';
    } else {
        if (listView) listView.style.display = 'none';
        if (mapView) mapView.style.display = 'block';
    }
}

// Help center search
function handleHelpSearch() {
    const query = document.getElementById('helpSearchInput')?.value.toLowerCase() || '';
    const questions = document.querySelectorAll('.popular-question-item');
    
    questions.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(query) ? 'block' : 'none';
    });
}

// Select topic in help center
function selectTopic(topicId) {
    const selectedTopic = document.querySelector('.selected-topic-section');
    if (selectedTopic) {
        selectedTopic.style.display = selectedTopic.style.display === 'none' ? 'block' : 'none';
    }
}

