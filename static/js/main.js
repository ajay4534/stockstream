// Global variables
let marketChart = null;
let currentTimeframe = '1d';
let priceChart = null;

// Initialize tabs
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and panes
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
            
            // Add active class to clicked button and corresponding pane
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');

            // Update content based on selected tab
            switch(tabId) {
                case 'stocks':
                    updateStocksWatchlist();
                    break;
                case 'crypto':
                    updateCryptoWatchlist();
                    break;
                case 'lottery':
                    updateLotteryData();
                    break;
                default:
                    updateWatchlists();
            }
        });
    });
}

// Update watchlists
async function updateWatchlists() {
    await updateStocksWatchlist();
    await updateCryptoWatchlist();
}

// Update stocks watchlist
async function updateStocksWatchlist() {
    try {
        const response = await fetch('/api/current_prices?type=stock');
        const stocks = await response.json();
        
        const watchlist = document.getElementById('stocks-watchlist');
        if (watchlist && stocks && !stocks.error) {
            watchlist.innerHTML = stocks.map(stock => `
                <div class="asset-item">
                    <div class="asset-info">
                        <div class="asset-symbol">${stock.symbol}</div>
                        <div class="asset-name">${stock.name || stock.symbol}</div>
                    </div>
                    <div class="asset-data">
                        <div class="asset-price">$${stock.price.toFixed(2)}</div>
                        <div class="asset-change ${stock.change >= 0 ? 'positive' : 'negative'}">
                            ${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}%
                        </div>
                    </div>
                </div>
            `).join('');
        } else if (stocks.error) {
            watchlist.innerHTML = '<div class="error">Failed to load stocks</div>';
        }
    } catch (error) {
        console.error('Error updating stocks watchlist:', error);
        const watchlist = document.getElementById('stocks-watchlist');
        if (watchlist) {
            watchlist.innerHTML = '<div class="error">Failed to load stocks</div>';
        }
    }
}

// Update crypto watchlist
async function updateCryptoWatchlist() {
    try {
        const response = await fetch('/api/current_prices?type=crypto');
        const cryptos = await response.json();
        
        const watchlist = document.getElementById('crypto-watchlist');
        if (watchlist && cryptos && !cryptos.error) {
            watchlist.innerHTML = cryptos.map(crypto => `
                <div class="asset-item">
                    <div class="asset-info">
                        <div class="asset-symbol">${crypto.symbol}</div>
                        <div class="asset-name">${crypto.name || crypto.symbol}</div>
                    </div>
                    <div class="asset-data">
                        <div class="asset-price">$${crypto.price.toFixed(2)}</div>
                        <div class="asset-change ${crypto.change >= 0 ? 'positive' : 'negative'}">
                            ${crypto.change >= 0 ? '+' : ''}${crypto.change.toFixed(2)}%
                        </div>
                    </div>
                </div>
            `).join('');
        } else if (cryptos.error) {
            watchlist.innerHTML = '<div class="error">Failed to load cryptocurrencies</div>';
        }
    } catch (error) {
        console.error('Error updating crypto watchlist:', error);
        const watchlist = document.getElementById('crypto-watchlist');
        if (watchlist) {
            watchlist.innerHTML = '<div class="error">Failed to load cryptocurrencies</div>';
        }
    }
}

// Update lottery data
async function updateLotteryData() {
    try {
        const response = await fetch('/api/lottery/latest');
        const data = await response.json();
        
        const lotteryResults = document.getElementById('lottery-results');
        
        if (lotteryResults) {
            if (data.error) {
                lotteryResults.innerHTML = '<div class="error">Failed to load lottery results</div>';
            } else {
                lotteryResults.innerHTML = `
                    <div class="lottery-section">
                        <div class="lottery-card">
                            <h2>Powerball</h2>
                            <div class="lottery-info">
                                <p><strong>Draw Date:</strong> ${data.powerball.drawDate}</p>
                                <p><strong>Winning Numbers:</strong></p>
                                <div class="lottery-numbers">
                                    ${data.powerball.numbers.map(num => `<span class="lottery-number">${num}</span>`).join('')}
                                    <span class="lottery-number powerball">${data.powerball.powerball}</span>
                                </div>
                                <p><strong>Next Draw:</strong> ${data.powerball.nextDraw}</p>
                                <p><strong>Estimated Jackpot:</strong> $${data.powerball.estimatedJackpot}</p>
                            </div>
                        </div>
                        
                        <div class="lottery-card">
                            <h2>Mega Millions</h2>
                            <div class="lottery-info">
                                <p><strong>Draw Date:</strong> ${data.megaMillions.drawDate}</p>
                                <p><strong>Winning Numbers:</strong></p>
                                <div class="lottery-numbers">
                                    ${data.megaMillions.numbers.map(num => `<span class="lottery-number">${num}</span>`).join('')}
                                    <span class="lottery-number mega-ball">${data.megaMillions.megaBall}</span>
                                </div>
                                <p><strong>Next Draw:</strong> ${data.megaMillions.nextDraw}</p>
                                <p><strong>Estimated Jackpot:</strong> $${data.megaMillions.estimatedJackpot}</p>
                            </div>
                        </div>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Error updating lottery data:', error);
        const lotteryResults = document.getElementById('lottery-results');
        if (lotteryResults) {
            lotteryResults.innerHTML = '<div class="error">Failed to load lottery results</div>';
        }
    }
}

// Update performance graphs
async function updateGraphs() {
    try {
        const response = await fetch('/api/dashboard/graphs');
        const graphs = await response.json();
        
        // Update stocks graph
        const stocksGraph = document.getElementById('stocks-graph');
        if (stocksGraph && graphs.stocks) {
            Plotly.newPlot('stocks-graph', graphs.stocks.data, graphs.stocks.layout);
        }
        
        // Update crypto graph
        const cryptoGraph = document.getElementById('crypto-graph');
        if (cryptoGraph && graphs.crypto) {
            Plotly.newPlot('crypto-graph', graphs.crypto.data, graphs.crypto.layout);
        }
    } catch (error) {
        console.error('Error updating graphs:', error);
        // Show error message in graph containers
        const stocksGraph = document.getElementById('stocks-graph');
        const cryptoGraph = document.getElementById('crypto-graph');
        if (stocksGraph) {
            stocksGraph.innerHTML = '<div class="error">Failed to load stock performance graph</div>';
        }
        if (cryptoGraph) {
            cryptoGraph.innerHTML = '<div class="error">Failed to load crypto performance graph</div>';
        }
    }
}

// Initialize everything when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Initialize tabs
    initializeTabs();

    // Initial updates
    updateWatchlists();
    updateGraphs();
    updateLotteryData();

    // Set up periodic updates
    setInterval(updateWatchlists, 60000); // Update watchlists every minute
    setInterval(updateGraphs, 3600000);   // Update graphs every hour
    setInterval(updateLotteryData, 3600000); // Update lottery every hour
});

// Show notification
function showNotification(message, type = 'info') {
    // You can implement a notification system here
    console.log(`${type.toUpperCase()}: ${message}`);
}

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

// Format percentage
function formatPercentage(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value / 100);
}
