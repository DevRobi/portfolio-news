import React, { useEffect, useState } from 'react';
import axios from 'axios';
import StockCard from './StockCard';
import { Loader2, LayoutDashboard, RefreshCw, Plus } from 'lucide-react';

const Dashboard = () => {
    const [portfolio, setPortfolio] = useState([]);
    const [stockData, setStockData] = useState({});
    const [loadingStocks, setLoadingStocks] = useState({});
    const [initialLoading, setInitialLoading] = useState(true);
    const [newTicker, setNewTicker] = useState('');
    const [adding, setAdding] = useState(false);

    const fetchStockNews = async (ticker) => {
        setLoadingStocks(prev => ({ ...prev, [ticker]: true }));
        try {
            const newsRes = await axios.get(`http://localhost:8000/api/news/${ticker}`);
            setStockData(prev => ({ ...prev, [ticker]: newsRes.data }));
        } catch (error) {
            console.error(`Error fetching news for ${ticker}:`, error);
        } finally {
            setLoadingStocks(prev => ({ ...prev, [ticker]: false }));
        }
    };

    const handleAddTicker = async (e) => {
        e.preventDefault();
        if (!newTicker) return;

        const tickerToAdd = newTicker.toUpperCase();
        setAdding(true);
        try {
            await axios.post('http://localhost:8000/api/portfolio', { ticker: tickerToAdd });
            setNewTicker('');

            // Optimistically add to portfolio list immediately
            if (!portfolio.includes(tickerToAdd)) {
                setPortfolio(prev => [...prev, tickerToAdd]);
            }

            // Fetch news in background
            fetchStockNews(tickerToAdd);
        } catch (error) {
            console.error("Error adding ticker:", error);
        } finally {
            setAdding(false);
        }
    };

    const handleRemoveTicker = async (ticker) => {
        if (!window.confirm(`Are you sure you want to remove ${ticker} from your portfolio?`)) return;

        try {
            await axios.delete(`http://localhost:8000/api/portfolio/${ticker}`);
            setPortfolio(prev => prev.filter(t => t !== ticker));
            setStockData(prev => {
                const newData = { ...prev };
                delete newData[ticker];
                return newData;
            });
        } catch (error) {
            console.error("Error removing ticker:", error);
        }
    };

    const fetchAllData = async () => {
        try {
            // 1. Get Portfolio
            const portfolioRes = await axios.get('http://localhost:8000/api/portfolio');
            const tickers = portfolioRes.data.portfolio;
            setPortfolio(tickers);

            // 2. Fetch news for all tickers with concurrency limit
            // Browser connection limit is usually 6. We limit to 3 to leave room for other actions (like adding tickers).
            const CONCURRENCY_LIMIT = 3;
            const queue = [...tickers];

            const processQueue = async () => {
                while (queue.length > 0) {
                    const ticker = queue.shift();
                    await fetchStockNews(ticker);
                }
            };

            const workers = Array(Math.min(tickers.length, CONCURRENCY_LIMIT))
                .fill(null)
                .map(() => processQueue());

            await Promise.all(workers);
        } catch (error) {
            console.error("Error fetching portfolio:", error);
        } finally {
            setInitialLoading(false);
        }
    };

    useEffect(() => {
        fetchAllData();
    }, []);

    const isGlobalLoading = Object.values(loadingStocks).some(Boolean);

    return (
        <div className="min-h-screen text-foreground p-4 md:p-8">
            <div className="max-w-4xl mx-auto space-y-12">
                {/* Header */}
                <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 pt-8">
                    <div className="flex items-center gap-4">
                        <div className="p-4 rounded-2xl bg-gradient-to-br from-yellow-500 to-amber-600 shadow-lg shadow-amber-500/20">
                            <LayoutDashboard className="w-8 h-8 text-black" />
                        </div>
                        <div>
                            <h1 className="text-4xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-yellow-400 to-amber-200">
                                Portfolio News
                            </h1>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <form onSubmit={handleAddTicker} className="flex items-center gap-2">
                            <input
                                type="text"
                                value={newTicker}
                                onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
                                placeholder="Add Ticker (e.g. AAPL)"
                                className="px-4 py-2.5 rounded-full bg-white/5 border border-white/10 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-yellow-500/50 focus:ring-1 focus:ring-yellow-500/50 transition-all w-48"
                                disabled={adding}
                            />
                            <button
                                type="submit"
                                disabled={adding || !newTicker}
                                className="p-2.5 rounded-full bg-yellow-500 text-black hover:bg-yellow-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                            >
                                {adding ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                            </button>
                        </form>

                        <button
                            onClick={fetchAllData}
                            disabled={isGlobalLoading}
                            className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-yellow-500/10 hover:bg-yellow-500/20 border border-yellow-500/20 transition-all text-sm font-medium text-yellow-400 hover:text-yellow-300 disabled:opacity-50"
                        >
                            <RefreshCw className={`w-4 h-4 ${isGlobalLoading ? 'animate-spin' : ''}`} />
                            Refresh All Data
                        </button>
                    </div>
                </header>

                {/* Content */}
                {initialLoading ? (
                    <div className="flex flex-col items-center justify-center py-32 gap-6 text-gray-500">
                        <div className="relative">
                            <div className="absolute inset-0 bg-blue-500/20 blur-xl rounded-full" />
                            <Loader2 className="w-12 h-12 animate-spin text-blue-400 relative z-10" />
                        </div>
                        <p className="text-lg font-light animate-pulse">Initializing portfolio...</p>
                    </div>
                ) : (
                    <div className="grid gap-8">
                        {portfolio.map((ticker) => (
                            <div key={ticker} className="relative">
                                {loadingStocks[ticker] && !stockData[ticker] ? (
                                    <div className="p-8 rounded-2xl glass border border-white/10 flex items-center justify-center min-h-[200px]">
                                        <div className="flex flex-col items-center gap-3">
                                            <Loader2 className="w-8 h-8 animate-spin text-yellow-500" />
                                            <span className="text-sm text-gray-400">Fetching news for {ticker}...</span>
                                        </div>
                                    </div>
                                ) : stockData[ticker] ? (
                                    <div className={loadingStocks[ticker] ? "opacity-50 pointer-events-none transition-opacity" : ""}>
                                        <StockCard
                                            stockData={stockData[ticker]}
                                            onRemove={handleRemoveTicker}
                                            onRefresh={() => fetchStockNews(ticker)}
                                            isLoading={loadingStocks[ticker]}
                                        />
                                    </div>
                                ) : (
                                    <div className="p-8 rounded-2xl glass border border-red-500/20 text-red-400 text-center">
                                        Failed to load data for {ticker}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Dashboard;
