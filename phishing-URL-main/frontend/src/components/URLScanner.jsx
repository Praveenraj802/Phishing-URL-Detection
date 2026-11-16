import { useState } from 'react';
import { scanURL } from '../services/api';

const URLScanner = () => {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleScan = async (e) => {
        e.preventDefault();

        if (!url.trim()) {
            setError('Please enter a URL');
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await scanURL(url);
            setResult(response);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const resetScan = () => {
        setUrl('');
        setResult(null);
        setError(null);
    };

    const getRiskColor = (prediction) => {
        switch (prediction) {
            case 'phishing':
                return 'danger';
            case 'legitimate':
                return 'success';
            default:
                return 'gray';
        }
    };

    const getRiskBadge = (prediction, risk_level) => {
        if (prediction === 'phishing') {
            return (
                <div className="inline-flex items-center px-4 py-2 rounded-full bg-danger-500 text-white font-bold text-lg shadow-lg">
                    <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    🔴 PHISHING DETECTED
                </div>
            );
        } else {
            return (
                <div className="inline-flex items-center px-4 py-2 rounded-full bg-success-500 text-white font-bold text-lg shadow-lg">
                    <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    🟢 SAFE
                </div>
            );
        }
    };

    return (
        <div className="card p-8">
            {/* Input Section */}
            <form onSubmit={handleScan} className="mb-8">
                <div className="flex flex-col md:flex-row gap-4">
                    <input
                        type="text"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="Enter URL to scan (e.g., https://example.com)"
                        className="input-field flex-1 text-lg"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <>
                                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                <span>Scanning...</span>
                            </>
                        ) : (
                            <>
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                </svg>
                                <span>Scan URL</span>
                            </>
                        )}
                    </button>
                </div>
            </form>

            {/* Error Message */}
            {error && (
                <div className="mb-6 p-4 bg-danger-500/20 border border-danger-500 rounded-lg text-danger-100">
                    <div className="flex items-start">
                        <svg className="w-5 h-5 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <p className="font-medium">{error}</p>
                    </div>
                </div>
            )}

            {/* Results Section */}
            {result && (
                <div className="space-y-6 animate-fadeIn">
                    {/* Result Badge */}
                    <div className="text-center py-4">
                        {getRiskBadge(result.prediction, result.risk_level)}
                    </div>

                    {/* Scanned URL */}
                    <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                        <p className="text-sm text-gray-400 mb-1">Scanned URL:</p>
                        <p className="text-white font-mono text-sm break-all">{result.url}</p>
                    </div>

                    {/* Confidence Score */}
                    <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                        <div className="flex justify-between items-center mb-2">
                            <span className="text-gray-300 font-medium">Confidence Score</span>
                            <span className="text-white font-bold text-lg">{(result.confidence * 100).toFixed(2)}%</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
                            <div
                                className={`h-full transition-all duration-500 ${result.prediction === 'phishing' ? 'bg-danger-500' : 'bg-success-500'
                                    }`}
                                style={{ width: `${result.confidence * 100}%` }}
                            ></div>
                        </div>
                    </div>

                    {/* Explanations */}
                    <div className="bg-white/5 rounded-lg p-6 border border-white/10">
                        <h3 className="text-xl font-bold text-white mb-4 flex items-center">
                            <svg className="w-6 h-6 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Why this result?
                        </h3>
                        <div className="space-y-3">
                            {result.reasons.map((reason, index) => (
                                <div key={index} className="flex items-start">
                                    <span className={`inline-block w-6 h-6 rounded-full flex-shrink-0 mt-0.5 mr-3 flex items-center justify-center ${result.prediction === 'phishing' ? 'bg-danger-500' : 'bg-success-500'
                                        }`}>
                                        {result.prediction === 'phishing' ? (
                                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                            </svg>
                                        ) : (
                                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                            </svg>
                                        )}
                                    </span>
                                    <p className="text-gray-200 leading-relaxed">{reason}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Scan Metadata */}
                    <div className="flex justify-between items-center text-sm text-gray-400">
                        <div>
                            <span className="font-medium">Scan Time:</span> {result.scan_time_ms.toFixed(2)}ms
                        </div>
                        <div>
                            <span className="font-medium">Risk Level:</span>{' '}
                            <span className={`font-bold uppercase ${result.risk_level === 'high' ? 'text-danger-400' :
                                    result.risk_level === 'medium' ? 'text-yellow-400' :
                                        'text-success-400'
                                }`}>
                                {result.risk_level}
                            </span>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex justify-center pt-4">
                        <button
                            onClick={resetScan}
                            className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all duration-200 border border-white/20"
                        >
                            Scan Another URL
                        </button>
                    </div>
                </div>
            )}

            {/* Example URLs */}
            {!result && !loading && (
                <div className="mt-8 p-4 bg-white/5 rounded-lg border border-white/10">
                    <h4 className="text-sm font-semibold text-gray-300 mb-3">Try these examples:</h4>
                    <div className="space-y-2 text-sm">
                        <button
                            onClick={() => setUrl('https://www.google.com')}
                            className="block w-full text-left px-3 py-2 text-gray-300 hover:bg-white/10 rounded transition-colors duration-150"
                        >
                            <span className="text-success-400">✓</span> https://www.google.com (Safe)
                        </button>
                        <button
                            onClick={() => setUrl('http://paypal-security-alert.com/update-account')}
                            className="block w-full text-left px-3 py-2 text-gray-300 hover:bg-white/10 rounded transition-colors duration-150"
                        >
                            <span className="text-danger-400">✗</span> http://paypal-security-alert.com/update-account (Phishing)
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default URLScanner;
