import React from 'react';

const WelcomePage = () => {
    return (
        <div className="min-h-screen w-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-400 via-blue-300 to-blue-200 text-white relative overflow-hidden">
            <div className="absolute inset-0 bg-black opacity-30 z-0"></div>
            <div className="relative z-10 text-center max-w-4xl mx-auto p-10">
                <div className="logo mb-5">
                    <img src="/logo.png" alt="Logo" className="mx-auto w-24" />
                </div>
                <h1 className="text-4xl font-bold mb-6 text-gray-900">WELCOME TO IP URL GRAPH</h1>
                <p className="text-lg mb-6 text-gray-800">
                    Search for Url,City or Ip Ranges to see graph or link counts of their relationships to other websites
                </p>
                <div className="mockup-container flex flex-wrap justify-center mb-8">
                    <div className="mockup flex-1 max-w-md m-2 rounded-xl overflow-hidden shadow-lg transition-transform duration-300 hover:translate-y-[-5px] hover:shadow-2xl">
                        <img src="/home.png" alt="Mockup Image" className="w-full rounded-t-xl" />
                        <div className="description p-4 bg-gradient-to-br from-blue-100 to-blue-200 rounded-b-xl text-left text-gray-800">
                            Internet Project for everyone who wishes to see website relations
                        </div>
                    </div>
                    {/* Add more mockups here if needed */}
                </div>
                <button
                    className="continue-btn mt-4 px-8 py-4 bg-blue-500 text-white rounded-xl transition-transform duration-300 hover:bg-blue-700 hover:translate-y-[-2px] hover:shadow-2xl"
                    onClick={() => window.location.href = '/tutorial'}
                >
                    Continue
                </button>
            </div>
        </div>
    );
};

export default WelcomePage;
