let trackedCrypto = new Set();
let trackedStocks = new Set();
let isUpdating = false;
let lastUpdateTime = new Date();

// Initialize with default values
try {
    console.log('Default crypto data:', defaultCrypto);
    console.log('Default stocks data:', defaultStocks);
    trackedCrypto = new Set(JSON.parse(defaultCrypto));
    trackedStocks = new Set(JSON.parse(defaultStocks));
    console.log('Initialized sets:', {
        crypto: Array.from(trackedCrypto),
        stocks: Array.from(trackedStocks)
    });

    // Create initial cards for default values
    trackedCrypto.forEach(symbol => {
        createAssetCard(symbol, symbol, 'crypto');
    });
    trackedStocks.forEach(symbol => {
        createAssetCard(symbol, symbol, 'stock');
    });

    // Start price updates
    updatePrices();
    setInterval(updatePrices, 30000); // Update every 30 seconds
} catch (error) {
    console.error('Error initializing tracked assets:', error);
    trackedCrypto = new Set();
    trackedStocks = new Set();
}

function createAssetCard(symbol, name, type) {
    const card = document.createElement('div');
    card.className = `asset-card ${type}`;
    card.id = `card-${symbol}`;
    
    const icon = type === 'crypto' ? 
        '<i class="fab fa-bitcoin"></i>' : 
        '<i class="fas fa-chart-line"></i>';
    
    card.innerHTML = `
        <div class="card-header">
            ${icon}
            <div class="symbol">${name}</div>
            <button class="remove-btn" onclick="removeSymbol('${symbol}', '${type}')">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="price loading" id="price-${symbol}">
            <i class="fas fa-sync-alt fa-spin"></i> Loading...
        </div>
        <div class="update-time" id="update-${symbol}">
            <i class="far fa-clock"></i>
        </div>
    `;
    return card;
}

function removeSymbol(symbol, type) {
    const card = document.getElementById(`card-${symbol}`);
    if (card) {
        card.remove();
    }
    
    if (type === 'crypto') {
        trackedCrypto.delete(symbol);
    } else if (type === 'stock') {
        trackedStocks.delete(symbol);
    }
    
    updatePrices();
}

async function updatePrices() {
    if (isUpdating) {
        console.log('Update already in progress, skipping...');
        return;
    }
    isUpdating = true;

    const cryptoSymbols = Array.from(trackedCrypto).join(',');
    const stockSymbols = Array.from(trackedStocks).join(',');
    
    if (!cryptoSymbols && !stockSymbols) {
        isUpdating = false;
        return;
    }

    console.log('Fetching prices for:', { crypto: cryptoSymbols, stocks: stockSymbols });
    
    try {
        const response = await fetch(`/get_prices?crypto=${encodeURIComponent(cryptoSymbols)}&stocks=${encodeURIComponent(stockSymbols)}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Received price data:', data);
        
        if (Object.keys(data).length === 0) {
            console.warn('No price data received');
            return;
        }

        lastUpdateTime = new Date();
        
        // Update all price elements to show they're refreshing
        document.querySelectorAll('.price').forEach(el => {
            if (!el.classList.contains('loading')) {
                el.classList.add('loading');
                el.textContent = 'Refreshing...';
            }
        });

        // Process received data
        for (const [symbol, info] of Object.entries(data)) {
            const priceElement = document.getElementById(`price-${symbol}`);
            const updateElement = document.getElementById(`update-${symbol}`);
            
            if (priceElement && info && typeof info.price === 'number') {
                priceElement.textContent = `$${info.price.toFixed(2)}`;
                priceElement.classList.remove('loading');
                if (updateElement) {
                    updateElement.textContent = `Last updated: ${lastUpdateTime.toLocaleTimeString()}`;
                }
            } else {
                console.warn(`Invalid price data for ${symbol}:`, info);
                if (priceElement) {
                    priceElement.textContent = 'Price unavailable';
                    priceElement.classList.remove('loading');
                }
            }
        }
    } catch (error) {
        console.error('Error fetching prices:', error);
        // Show error state for all loading prices
        document.querySelectorAll('.price.loading').forEach(el => {
            el.textContent = 'Error loading price';
            el.classList.remove('loading');
        });
    } finally {
        isUpdating = false;
    }
}

let searchTimeout;
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
const cryptoGrid = document.getElementById('cryptoGrid');
const stockGrid = document.getElementById('stockGrid');

searchInput.addEventListener('input', (e) => {
    const query = e.target.value.trim();
    
    clearTimeout(searchTimeout);
    
    if (!query) {
        searchResults.style.display = 'none';
        return;
    }
    
    searchTimeout = setTimeout(() => {
        // Search for both crypto and stocks
        Promise.all([
            fetch(`/search_coins?q=${query}`).then(res => res.json()),
            fetch(`/search_stocks?q=${query}`).then(res => res.json())
        ]).then(([cryptoResults, stockResults]) => {
            searchResults.innerHTML = '';
            
            // Add crypto results
            cryptoResults.forEach(coin => {
                const div = document.createElement('div');
                div.className = 'search-result-item';
                div.textContent = `${coin.name} (Crypto)`;
                div.onclick = () => {
                    if (!trackedCrypto.has(coin.id)) {
                        trackedCrypto.add(coin.id);
                        cryptoGrid.appendChild(createAssetCard(coin.id, coin.name, 'crypto'));
                        updatePrices();
                    }
                    searchInput.value = '';
                    searchResults.style.display = 'none';
                };
                searchResults.appendChild(div);
            });
            
            // Add stock results
            stockResults.forEach(stock => {
                const div = document.createElement('div');
                div.className = 'search-result-item';
                div.textContent = `${stock.name} (Stock)`;
                div.onclick = () => {
                    if (!trackedStocks.has(stock.symbol)) {
                        trackedStocks.add(stock.symbol);
                        stockGrid.appendChild(createAssetCard(stock.symbol, stock.name, 'stock'));
                        updatePrices();
                    }
                    searchInput.value = '';
                    searchResults.style.display = 'none';
                };
                searchResults.appendChild(div);
            });
            
            searchResults.style.display = 
                (cryptoResults.length + stockResults.length) ? 'block' : 'none';
        });
    }, 300);
});

document.addEventListener('click', (e) => {
    if (!searchResults.contains(e.target) && e.target !== searchInput) {
        searchResults.style.display = 'none';
    }
});

document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing grids with default assets');
    const cryptoGrid = document.getElementById('cryptoGrid');
    const stockGrid = document.getElementById('stockGrid');

    trackedCrypto.forEach(symbol => {
        console.log('Adding crypto card:', symbol);
        cryptoGrid.appendChild(createAssetCard(symbol, symbol, 'crypto'));
    });

    trackedStocks.forEach(symbol => {
        console.log('Adding stock card:', symbol);
        stockGrid.appendChild(createAssetCard(symbol, symbol, 'stock'));
    });
});
