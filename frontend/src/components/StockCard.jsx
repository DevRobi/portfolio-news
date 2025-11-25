import { ExternalLink, Clock, Newspaper, Sparkles, Trash2, RefreshCw } from 'lucide-react';

const StockCard = ({ stockData, onRemove, onRefresh, isLoading }) => {
    const { ticker, summary, articles } = stockData;

    return (
        <div className="glass-card rounded-2xl overflow-hidden transition-all duration-300 hover:scale-[1.01] hover:shadow-primary/10 hover:border-primary/20 group">
            {/* Header with Gradient */}
            <div className="relative p-6 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-yellow-600/10 to-amber-600/10 opacity-50" />
                <div className="relative flex justify-between items-center z-10">
                    <h2 className="text-3xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-yellow-400 to-amber-200">
                        {ticker}
                    </h2>
                    <div className="flex items-center gap-3">
                        <div className="px-3 py-1 rounded-full bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-xs font-medium">
                            {new Date().toLocaleDateString()}
                        </div>
                        <button
                            onClick={onRefresh}
                            disabled={isLoading}
                            className="p-2 rounded-full hover:bg-yellow-500/20 text-gray-400 hover:text-yellow-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            title="Refresh this stock"
                        >
                            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                        </button>
                        <button
                            onClick={() => onRemove(ticker)}
                            className="p-2 rounded-full hover:bg-red-500/20 text-gray-400 hover:text-red-400 transition-colors"
                            title="Remove from portfolio"
                        >
                            <Trash2 className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>

            <div className="p-6 pt-2 space-y-6">
                {/* Main Summary */}
                <div className="max-h-96 overflow-y-auto pr-2 custom-scrollbar">
                    <div className="prose prose-invert max-w-none">
                        <p className="text-lg text-gray-300 leading-relaxed font-light whitespace-pre-wrap">
                            {summary}
                        </p>
                    </div>
                </div>

                {/* Sources Section */}
                <div className="space-y-3 pt-4 border-t border-white/5">
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 flex items-center gap-2">
                        <Newspaper className="w-3 h-3" />
                        Sources ({articles.length} articles)
                    </h3>
                    <div className="max-h-96 overflow-y-auto pr-2 space-y-2 custom-scrollbar">
                        {articles.slice(0, 50).map((article, index) => (
                            <a
                                key={index}
                                href={article.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors group/link border border-transparent hover:border-white/10"
                            >
                                <div className="flex-1 min-w-0 mr-4">
                                    <h4 className="font-medium text-sm text-gray-200 truncate group-hover/link:text-blue-300 transition-colors">
                                        {article.title}
                                    </h4>
                                    <div className="flex items-center gap-2 mt-0.5 text-xs text-gray-500">
                                        <span>{article.source}</span>
                                        <span>•</span>
                                        <span className="flex items-center gap-1">
                                            <Clock className="w-3 h-3" />
                                            {new Date(article.published).toLocaleDateString()}
                                        </span>
                                    </div>
                                </div>
                                <ExternalLink className="w-4 h-4 text-gray-500 group-hover/link:text-blue-300 transition-colors" />
                            </a>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StockCard;
