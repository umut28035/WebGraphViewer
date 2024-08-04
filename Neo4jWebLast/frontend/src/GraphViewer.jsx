import React, { useEffect, useRef } from 'react';
import { Network } from 'vis-network/standalone/esm/vis-network';
import { DataSet } from 'vis-data/standalone/esm/vis-data';

function GraphViewer() {
    const graphRef = useRef(null);
    const selectRef = useRef(null);
    const fetchCityButtonRef = useRef(null);
    const fetchUrlButtonRef = useRef(null);
    const fetchIpButtonRef = useRef(null);
    const fetchGraphButtonRef = useRef(null);
    const relationshipCountButtonRef = useRef(null);
    const relationshipIncomingButtonRef = useRef(null);
    const deleteDataButtonRef = useRef(null);
    const iprangeButtonRef = useRef(null);

    useEffect(() => {
        function shortenUrl(url) {
            return url.length > 30 ? url.slice(0, 27) + '...' : url;
        }

        function fetchGraph() {
            const serverUrl = 'http://localhost:3000';

            fetch(serverUrl + '/neo4j-api')
                .then(response => response.json())
                .then(data => {
                    const nodes = new DataSet();
                    const edges = new DataSet();

                    data.nodes.forEach(node => {
                        const nodeId = node.id;

                        nodes.add({
                            id: nodeId,
                            label: shortenUrl(node.properties.url),
                            title: node.properties.url,
                            shape: 'dot',
                            size: node.properties.is_root ? 30 : 15,
                            color: node.properties.is_root ? '#A600FF' : '#89F4F5'
                        });
                    });

                    data.edges.forEach(edge => {
                        edges.add({
                            from: edge.from,
                            to: edge.to,
                            label: edge.label,
                            arrows: {
                                to: { enabled: true, scaleFactor: 1, color: '#000000' }
                            },
                            font: { size: 7, color: '#000000' }
                        });
                    });

                    const container = graphRef.current;
                    const dataForGraph = {
                        nodes: nodes,
                        edges: edges
                    };
                    const options = {
                        nodes: {
                            font: {
                                size: 14,
                                multi: 'html',
                                bold: {
                                    color: '#0077aa'
                                }
                            }
                        },
                        edges: {
                            color: { color: '#000000' },
                            arrows: {
                                to: { enabled: true, scaleFactor: 1, color: '#000000' }
                            },
                            font: { size: 7, color: '#000000' }
                        },
                        physics: {
                            enabled: true,
                            stabilization: {
                                enabled: true,
                                iterations: 1000,
                                updateInterval: 25,
                                onlyDynamicEdges: false,
                                fit: true
                            },
                            barnesHut: {
                                gravitationalConstant: -2000,
                                centralGravity: 0.3,
                                springLength: 95,
                                springConstant: 0.04,
                                damping: 0.09,
                                avoidOverlap: 0.1
                            },
                            maxVelocity: 50,
                            minVelocity: 0.1,
                            solver: 'barnesHut',
                            timestep: 0.5,
                            adaptiveTimestep: true
                        }
                    };
                    const network = new Network(container, dataForGraph, options);
                })
                .catch(error => console.error('Error fetching graph data:', error));
        }

        function fetchCity() {
            const cityInput = document.getElementById('link-list').value;
            const serverUrl = 'http://localhost:3000';

            fetch(`${serverUrl}/neo4j-city?city=${cityInput}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.text();
                })
                .then(data => {
                    console.log(data);
                    showSuccessMessage();
                })
                .catch(error => {
                    console.error('Error fetching city data:', error);
                    alert('City data not found. Please check the console for more information.');
                });
        }

        function fetchUrl() {
            const urlInput = document.getElementById('link-list').value;
            const serverUrl = 'http://localhost:3000';

            fetch(`${serverUrl}/neo4j-urlinput?urlinput=${encodeURIComponent(urlInput)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.text();
                })
                .then(data => {
                    console.log(data);
                    showSuccessMessage();
                })
                .catch(error => {
                    console.error('Error fetching url data:', error);
                    alert('Url format is incorrect or missing. Please check the console for more information.');
                });
        }

        function fetchIp() {
            const ipInput = document.getElementById('link-list').value;
            const serverUrl = 'http://localhost:3000';

            fetch(`${serverUrl}/neo4j-ipinput?ipinput=${ipInput}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.text();
                })
                .then(data => {
                    console.log(data);
                    showSuccessMessage();
                })
                .catch(error => {
                    console.error('Error fetching ip data:', error);
                    alert('Ip format is incorrect or missing. Please check the console for more information.');
                });
        }

        function deleteData() {
            const serverUrl = 'http://localhost:3000';

            fetch(serverUrl + '/neo4j-delete')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.text();
                })
                .then(data => {
                    console.log(data);
                    showSuccessMessage();
                    location.reload(true);
                })
                .catch(error => {
                    console.error('Error deleting data:', error);
                    alert('Error while deleting data. Please check the console for more information.');
                });
        }

        function selectDepth() {
            const selectedValue = selectRef.current.value;
            const serverUrl = 'http://localhost:3000';

            fetch(`${serverUrl}/neo4j-depth?depthinput=${selectedValue}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.text();
                })
                .then(data => {
                    console.log(data);
                    showSuccessMessage();
                })
                .catch(error => {
                    console.error('Error selecting depth:', error);
                    alert('Error while selecting depth. Please check the console for more information.');
                });
        }

        function relationshipCount() {
            const serverUrl = 'http://localhost:3000';

            fetch(serverUrl + '/neo4j-count')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log(data);

                    const relationshipDataDiv = document.getElementById('relationshipData');
                    relationshipDataDiv.innerHTML = "";

                    data.forEach(item => {
                        const itemDiv = document.createElement('div');
                        itemDiv.classList.add('relationship-item', 'p-4', 'mb-4', 'bg-white', 'border', 'border-gray-300', 'rounded', 'hover:bg-gray-200');

                        const linkElement = document.createElement('div');
                        linkElement.classList.add('link', 'text-black', 'font-bold');
                        linkElement.textContent = `LINK: ${item.url}`;

                        const countElement = document.createElement('div');
                        countElement.classList.add('count', 'text-gray-600', 'font-bold');
                        countElement.textContent = ` Has Link Count: ${item.relationship_count}`;

                        itemDiv.appendChild(linkElement);
                        itemDiv.appendChild(countElement);

                        relationshipDataDiv.appendChild(itemDiv);
                    });

                    showSuccessMessage();
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    alert('Error while getting the number of outgoing links. Please check the console for more information.');
                });
        }

        function relationshipIncoming() {
            const serverUrl = 'http://localhost:3000';

            fetch(serverUrl + '/neo4j-incoming')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log(data);

                    const relationshipDataDiv = document.getElementById('relationshipData');
                    relationshipDataDiv.innerHTML = "";

                    data.forEach(item => {
                        const itemDiv = document.createElement('div');
                        itemDiv.classList.add('relationship-item', 'p-4', 'mb-4', 'bg-white', 'border', 'border-gray-300', 'rounded', 'hover:bg-gray-200');

                        const linkElement = document.createElement('div');
                        linkElement.classList.add('link', 'text-black', 'font-bold');
                        linkElement.textContent = `LINK: ${item.url}`;

                        const countElement = document.createElement('div');
                        countElement.classList.add('count', 'text-gray-600', 'font-bold');
                        countElement.textContent = ` Has Link Count: ${item.relationship_count}`;

                        itemDiv.appendChild(linkElement);
                        itemDiv.appendChild(countElement);

                        relationshipDataDiv.appendChild(itemDiv);
                    });

                    showSuccessMessage();
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    alert('Error while getting the number of incoming links. Please check the console for more information.');
                });
        }

        function ipRange() {
            const ipInput1 = document.getElementById('list1').value;
            const ipInput2 = document.getElementById('list2').value;
            const serverUrl = 'http://localhost:3000';

            fetch(`${serverUrl}/neo4j-iprangesearcher?ipinput1=${ipInput1}&ipinput2=${ipInput2}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.text();
                })
                .then(data => {
                    console.log(data);
                    showSuccessMessage();
                })
                .catch(error => {
                    console.error('Error fetching IP data:', error);
                    alert('Error while determining the IP range. Please check the console for more information.');
                });
        }

        function showSuccessMessage() {
            const successMessage = document.getElementById('successMessage');
            successMessage.style.display = 'block';
            setTimeout(() => {
                successMessage.style.display = 'none';
            }, 3000);
        }

        // Function to add event listeners
        function addEventListeners() {
            if (selectRef.current) selectRef.current.addEventListener('change', selectDepth);
            if (fetchCityButtonRef.current) fetchCityButtonRef.current.addEventListener('click', fetchCity);
            if (fetchUrlButtonRef.current) fetchUrlButtonRef.current.addEventListener('click', fetchUrl);
            if (fetchIpButtonRef.current) fetchIpButtonRef.current.addEventListener('click', fetchIp);
            if (fetchGraphButtonRef.current) fetchGraphButtonRef.current.addEventListener('click', fetchGraph);
            if (relationshipCountButtonRef.current) relationshipCountButtonRef.current.addEventListener('click', relationshipCount);
            if (relationshipIncomingButtonRef.current) relationshipIncomingButtonRef.current.addEventListener('click', relationshipIncoming);
            if (deleteDataButtonRef.current) deleteDataButtonRef.current.addEventListener('click', deleteData);
            if (iprangeButtonRef.current) iprangeButtonRef.current.addEventListener('click', ipRange);
        }

        // Function to remove event listeners
        function removeEventListeners() {
            if (selectRef.current) selectRef.current.removeEventListener('change', selectDepth);
            if (fetchCityButtonRef.current) fetchCityButtonRef.current.removeEventListener('click', fetchCity);
            if (fetchUrlButtonRef.current) fetchUrlButtonRef.current.removeEventListener('click', fetchUrl);
            if (fetchIpButtonRef.current) fetchIpButtonRef.current.removeEventListener('click', fetchIp);
            if (fetchGraphButtonRef.current) fetchGraphButtonRef.current.removeEventListener('click', fetchGraph);
            if (relationshipCountButtonRef.current) relationshipCountButtonRef.current.removeEventListener('click', relationshipCount);
            if (relationshipIncomingButtonRef.current) relationshipIncomingButtonRef.current.removeEventListener('click', relationshipIncoming);
            if (deleteDataButtonRef.current) deleteDataButtonRef.current.removeEventListener('click', deleteData);
            if (iprangeButtonRef.current) iprangeButtonRef.current.removeEventListener('click', ipRange);
        }

        addEventListeners(); // Add event listeners when component mounts

        // Clean up event listeners when component unmounts
        return () => {
            removeEventListeners();
        };
    }, []);

    return (
        <div className="min-h-screen w-screen flex flex-col pt-16 bg-gradient-to-br from-blue-400 via-blue-300 to-blue-200 text-gray-800 overflow-hidden"> {/* Added pt-16 for padding */}
            <div className="flex flex-grow">
                <div className="flex-[1_1_25%] bg-gray-100 p-5 overflow-y-auto" id="sidebar">
                    <img src="/logo.png" alt="logo" className="w-40 h-auto" />
                    <div className="mb-4">
                        <label htmlFor="maxDepthSelect" className="block mb-2 text-black">Select depth:</label>
                        <select id="maxDepthSelect" ref={selectRef} className="block w-full p-2 border border-white rounded bg-white text-black" defaultValue="1">
                            <option value="1">1</option>
                            <option value="2">2</option>
                            <option value="3">3</option>
                        </select>
                    </div>

                    <div className="mb-4">
                        <input id="link-list" className="w-full p-2 border border-gray-300 rounded bg-white" placeholder="Enter link or IP here" />
                    </div>

                    <div className="flex justify-between">
                        <button id="fetchCityButton" ref={fetchCityButtonRef} className="w-1/3 h-10 p-2 bg-blue-500 text-white rounded mx-1 hover:bg-blue-700">Add City</button>
                        <button id="fetchUrlButton" ref={fetchUrlButtonRef} className="w-1/3 h-10 p-2 bg-blue-500 text-white rounded mx-1 hover:bg-blue-700">Add Url</button>
                        <button id="fetchIpButton" ref={fetchIpButtonRef} className="w-1/3 h-10 p-2 bg-blue-500 text-white rounded mx-1 hover:bg-blue-700">Add Ip</button>
                    </div>
                    

                    <div className="mt-4">
                        <button id="fetchGraphButton" ref={fetchGraphButtonRef} className="w-full h-10 p-2 bg-blue-500 text-white rounded hover:bg-blue-700">Get Graph</button>
                        <button id="relationshipCountButton" ref={relationshipCountButtonRef} className="w-full h-10 p-2 bg-blue-500 text-white rounded mt-2 hover:bg-blue-700">Outgoing Link</button>
                        <button id="relationshipIncomingButton" ref={relationshipIncomingButtonRef} className="w-full h-10 p-2 bg-blue-500 text-white rounded mt-2 hover:bg-blue-700">Incoming Link</button>
                        <button id="deleteDataButton" ref={deleteDataButtonRef} className="w-full h-10 p-2 bg-red-600 text-white rounded mt-2 hover:bg-red-800">Delete Data</button>
                    </div>

                    <div className="mt-4 flex justify-between">
                        <input id="list1" className="w-[48%] p-3 border border-gray-300 rounded bg-white" placeholder="Enter start IP here" />
                        <input id="list2" className="w-[48%] p-3 border border-gray-300 rounded bg-white ml-2" placeholder="Enter end IP here" />
                    </div>

                    <div className="mt-4">
                        <button id="iprangeButton" ref={iprangeButtonRef} className="w-full h-10 p-2 bg-blue-500 text-white rounded hover:bg-blue-700">Search IP Range</button>
                    </div>
                </div>

                <div className="flex-[2_1_50%] h-screen bg-gray-300 p-5 overflow-hidden bg-white w-full h-full flex flex-col">
                    <h2 className="text-xl font-bold mb-4 text-black">Graph Visualization</h2>
                    <div id="graph" ref={graphRef} className="border border-black-900 flex-grow "></div>
                </div>

                <div className="flex-[1_1_25%] bg-gray-100 p-5 overflow-y-auto" id="links-sidebar">
                    <h2 className="text-xl font-bold mb-4 text-black">Links</h2>
                    <div id="relationshipData" className="overflow-y-auto" style={{ maxHeight: '500px' }}></div>
                </div>

                <div id="successMessage" className="fixed bottom-5 right-5 bg-green-500 text-white p-3 rounded hidden">Request completed successfully!</div>
            </div>
        </div>
    );
}

export default GraphViewer;


// npm run dev -> start react