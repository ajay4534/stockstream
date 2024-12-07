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
            let html = '';
            stocks.forEach(stock => {
                const changeColor = stock.change >= 0 ? 'green' : 'red';
                html += `
                    <div class="watchlist-item">
                        <div class="d-flex justify-content-between">
                            <strong>${stock.symbol}</strong>
                            <span>$${stock.price.toFixed(2)}</span>
                        </div>
                        <div class="price-info" style="color: ${changeColor}">
                            ${(stock.change * 100).toFixed(2)}%
                        </div>
                    </div>
                `;
            });
            watchlist.innerHTML = html;
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
            let html = '';
            cryptos.forEach(crypto => {
                const changeColor = crypto.change >= 0 ? 'green' : 'red';
                html += `
                    <div class="watchlist-item">
                        <div class="d-flex justify-content-between">
                            <strong>${crypto.symbol}</strong>
                            <span>$${crypto.price.toFixed(2)}</span>
                        </div>
                        <div class="price-info" style="color: ${changeColor}">
                            ${(crypto.change * 100).toFixed(2)}%
                        </div>
                    </div>
                `;
            });
            watchlist.innerHTML = html;
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
        if (response.ok) {
            const data = await response.json();
            const lotteryResults = document.getElementById('lottery-results');
            if (!lotteryResults) return;

            if (data.error) {
                lotteryResults.innerHTML = '<div class="error">Failed to load lottery results</div>';
            } else {
                lotteryResults.innerHTML = `
                    <div class="lottery-section">
                        <div class="lottery-card">
                            <h2>Powerball</h2>
                            <div class="lottery-info">
                                <div class="draw-section old-draw">
                                    <h4>Previous Draw (${data.powerball.old_draw_date})</h4>
                                    <div class="numbers">${data.powerball.old_numbers}</div>
                                    <div class="special-ball">Powerball: ${data.powerball.old_powerball}</div>
                                </div>
                                <div class="draw-section latest-draw">
                                    <h4>Latest Draw (${data.powerball.latest_draw_date})</h4>
                                    <div class="numbers">${data.powerball.latest_numbers}</div>
                                    <div class="special-ball">Powerball: ${data.powerball.latest_powerball}</div>
                                </div>
                                <div class="draw-section next-draw">
                                    <h4>Next Draw (${data.powerball.next_draw_date})</h4>
                                    <div class="estimated-jackpot">Estimated Jackpot: ${data.powerball.estimated_jackpot}</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="lottery-card">
                            <h2>Mega Millions</h2>
                            <div class="lottery-info">
                                <div class="draw-section old-draw">
                                    <h4>Previous Draw (${data.mega_millions.old_draw_date})</h4>
                                    <div class="numbers">${data.mega_millions.old_numbers}</div>
                                    <div class="special-ball">Mega Ball: ${data.mega_millions.old_mega_ball}</div>
                                </div>
                                <div class="draw-section latest-draw">
                                    <h4>Latest Draw (${data.mega_millions.latest_draw_date})</h4>
                                    <div class="numbers">${data.mega_millions.latest_numbers}</div>
                                    <div class="special-ball">Mega Ball: ${data.mega_millions.latest_mega_ball}</div>
                                </div>
                                <div class="draw-section next-draw">
                                    <h4>Next Draw (${data.mega_millions.next_draw_date})</h4>
                                    <div class="estimated-jackpot">Estimated Jackpot: ${data.mega_millions.estimated_jackpot}</div>
                                </div>
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
        
        // Stock performance graph
        const stocksGraphDiv = document.getElementById('stocks-graph');
        if (stocksGraphDiv) {
            const stockLayout = {
                title: '',
                showlegend: true,
                height: 240,  // Reduced height
                margin: { t: 10, l: 40, r: 10, b: 30 },  // Compact margins
                xaxis: {
                    showgrid: false,
                    zeroline: false
                },
                yaxis: {
                    showgrid: true,
                    zeroline: false,
                    tickformat: '.2%'  // Format as percentage
                },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: {
                    size: 10  // Smaller font size
                }
            };
            
            Plotly.newPlot('stocks-graph', graphs.stocks.data, stockLayout);
        }
        
        // Crypto performance graph
        const cryptoGraphDiv = document.getElementById('crypto-graph');
        if (cryptoGraphDiv) {
            const cryptoLayout = {
                title: '',
                showlegend: true,
                height: 240,  // Reduced height
                margin: { t: 10, l: 40, r: 10, b: 30 },  // Compact margins
                xaxis: {
                    showgrid: false,
                    zeroline: false
                },
                yaxis: {
                    showgrid: true,
                    zeroline: false,
                    tickformat: '.2%'  // Format as percentage
                },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: {
                    size: 10  // Smaller font size
                }
            };
            
            Plotly.newPlot('crypto-graph', graphs.crypto.data, cryptoLayout);
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
