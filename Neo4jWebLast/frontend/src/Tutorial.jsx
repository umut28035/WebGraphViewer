import React from 'react';

const TutorialPage = () => {
    const buttons = [
        {
            src: "/1.png",
            alt: "Button 1",
            title: "Add City",
            description: "Enter city name to see relationships of websites in the given city"
        },
        {
            src: "/2.png",
            alt: "Button 2",
            title: "Add URL",
            description: "Enter URL to see the graph and link counts for the given URL"
        },
        {
            src: "/3.png",
            alt: "Button 3",
            title: "Add IP",
            description: "Enter IP too see relationships and link counts for the website(If there is any for the given IP)"
        },
        {
            src: "/4.png",
            alt: "Button 4",
            title: "Outgoing Link",
            description: "Click Outgoing Links to see outgoing link counts from all the main pages(root) from the graph"
        },
        {
            src: "/5.png",
            alt: "Button 5",
            title: "Get Graph",
            description: "Click Get Graph to see the graph visiualization of your selected function"
        },
        {
            src: "/6.png",
            alt: "Button 6",
            title: "Delete Data",
            description: "Click Delete Data to clean all inputs, graph and counts"
        },
        {
            src: "/7.png",
            alt: "Button 7",
            title: "Incoming Link",
            description: "Click Incoming Links to see total number of incoming links to all main pages(root) from the graph"
        },
        {
            src: "/8.png",
            alt: "Button 8",
            title: "Search IP Range",
            description: "Enter 2 IP's to see the relationships of the websites in that range(Note: End IP should never be smaller than Start IP)"
        },
    ];

    return (
        <div className="min-h-screen w-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-400 via-blue-300 to-blue-200 text-gray-800 overflow-x-hidden pt-16"> {/* Added pt-16 for padding */}
        <div className="w-11/12 max-w-5xl flex flex-col items-center justify-center bg-white bg-opacity-90 p-10 rounded-3xl shadow-2xl backdrop-blur-md animate-fadeIn">
          <div className="logo mb-10 text-center">
            <img src="/logo.png" alt="Logo" className="max-w-xs mx-auto" />
          </div>
          <h2 className="text-3xl font-bold mb-10">TUTORIAL</h2>
          <div className="button-container grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 w-full">
            {buttons.map((button, index) => (
              <div key={index} className="button flex flex-col items-center p-8 bg-[#001F40] text-white rounded-xl cursor-pointer transition-transform transform hover:scale-105 hover:bg-[#001F50] font-bold">
                <img src={button.src} alt={button.alt} className="w-48 h-32 mb-4" />
                <h3 className="text-xl font-semibold mb-2">{button.title}</h3>
                <div className="description text-center text-sm">{button.description}</div>
              </div>
            ))}
          </div>
          <button
            className="continue-btn mt-10 px-8 py-4 bg-blue-500 text-white rounded-xl transition-transform duration-300 hover:bg-blue-700 hover:translate-y-[-2px] hover:shadow-2xl"
            onClick={() => window.location.href='/graph-viewer'}
          >
            Continue
          </button>
        </div>
      </div>
      
    );
};

export default TutorialPage;
