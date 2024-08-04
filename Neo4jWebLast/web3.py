from flask import Flask, request, jsonify
from flask_cors import CORS
from py2neo import Graph, NodeMatcher
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from neo4j import GraphDatabase
import ipaddress
from requests.exceptions import RequestException
import mysql.connector
from tld import get_tld
from publicsuffix2 import get_sld

app = Flask(__name__)
CORS(app)  # Allow all origins by default

# Connect to the Neo4j database
graph = Graph("bolt://localhost:7687", auth=("neo4j", "25042166"))
uri = "bolt://localhost:7687"
username = "neo4j"
password = "25042166"
#neo4j part
urls = []
#urls = ['https://www.milliyet.com.tr','https://webonline.cankaya.edu.tr','https://cubicl.io/tr','https://www.cankaya.edu.tr']
MAX_DEPTH = 1
# Kök domainlerin listesi
root_domains = set()

mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '250421nurmur',
    'database': 'cityurl'
}


#def get_root_domain(url):
#    parsed_url = urlparse(url)
#    netloc = parsed_url.netloc
#    netloc_parts = netloc.split('.')
#    if len(netloc_parts) > 2 and (netloc_parts[-2] in ['com', 'edu', 'org', 'gov', 'k12']):
#        root_domain = '.'.join(netloc_parts[-3:])
#    else:
#        root_domain = '.'.join(netloc_parts[-2:])
#    return root_domain


def get_root_domain(url):
    parsed_url = urlparse(url)
    domain = get_sld(parsed_url.netloc)
    return domain


# Helper function to get all links from a given URL
def get_all_links(url):
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    base_url = get_root_domain(url)
    print("Base URL:", base_url)
    for link in soup.find_all('a', href=True):
        href = link['href'].rstrip('/')
        if href.startswith('http'):
            parsed_href = urlparse(href)
            link_domain = parsed_href.netloc
            if base_url != link_domain:
                root_domain = get_root_domain(href)
                if root_domain not in base_url:
                    root_domains.add(root_domain)
                    links.append(strip_url(href))
                else:    
                    links.append(strip_url(href))
    return links

# Helper function to strip http, https, and www
def strip_url(url):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.replace('www.', '')
    return netloc + parsed_url.path

# Neo4j transaction functions
def create_node(tx, url, is_root, depth):
    stripped_url = strip_url(url)
    result = tx.run("MATCH (page:Page {url: $url}) RETURN page", url=stripped_url)
    if not result.single():
        tx.run("MERGE (page:Page {url: $url, is_root: $is_root, depth: $depth})", url=stripped_url, is_root=is_root, depth=depth)

def create_relationship(tx, root_url, url):
    stripped_root_url = strip_url(root_url)
    stripped_url = strip_url(url)
    tx.run("MATCH (root:Page {url: $root_url}), (page:Page {url: $url}) "
           "MERGE (root)-[:HAS_LINK]->(page)", root_url=stripped_root_url, url=stripped_url)

def update_root_property(tx, url, is_root, depth):
    stripped_url = strip_url(url)
    result = tx.run("MATCH (page:Page {url: $url}) RETURN page", url=stripped_url)
    if not result.single():
        tx.run("MERGE (page:Page {url: $url, is_root: $is_root, depth: $depth})", url=stripped_url, is_root=is_root, depth=depth)
    else:
        tx.run("MATCH (page:Page {url: $url}) SET page.is_root = $is_root, page.depth = $depth", url=stripped_url, is_root=is_root, depth=depth)

# Main function to add links to Neo4j
def add_links_to_neo4j(driver, root_url, links, depth):
    if depth >= MAX_DEPTH:
        return
    with driver.session() as session:
        child_links2 = set()
        stripped_root_url = strip_url(root_url)
        session.write_transaction(create_node, root_url, is_root=True, depth=0)
        for link in links:
            session.write_transaction(create_node, link, is_root=False, depth=depth+1)
            session.write_transaction(create_relationship, root_url, link)
            if depth + 1 < MAX_DEPTH:
                child_links = get_all_links("http://" + link)
                add_links_to_neo4j(driver, link, child_links, depth + 1)
                for child_link in child_links:
                    session.write_transaction(create_relationship, link, child_link)
                    child_links2.add(child_link)
        for domain in root_domains:
            stripped_domain = strip_url(domain)
            session.write_transaction(update_root_property, domain, is_root=True, depth=0)
            for link in links:

                parsed_link = urlparse(link)
                base_link = get_root_domain("http://" + parsed_link.path)
                if stripped_domain in base_link and link != domain:
                    session.write_transaction(create_relationship, domain, link)
            for child_link2 in child_links2:
                parsed_link2 = urlparse(child_link2)
                base_link2 = parsed_link2.netloc
                if stripped_domain in base_link2 and child_link2 != domain:
                    session.write_transaction(create_relationship, domain, child_link2)

# Function to read URLs from a file
#def read_urls_from_file(filename):
#    with open(filename, 'r') as file:
#        urls = file.readlines()[1:]
#    urls = [url.strip() for url in urls]
#    return urls


# MySQL'den URL'leri okuyan fonksiyon
def read_urls_from_mysql(city):
    urls = []
    connection = None  # connection değişkenini None ile başlatın
    try:
        # MySQL bağlantısını oluştur
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Belirli bir şehre ait URL'leri veritabanından al
        cursor.execute("SELECT url_address FROM url_locations WHERE city = %s", (city,))
        rows = cursor.fetchall()

        # URL'leri listeye ekle
        urls = [row[0] for row in rows]

    except mysql.connector.Error as error:
        print("MySQL error:", error)

    finally:
        # Bağlantıyı kapat
        if connection and connection.is_connected():  # connection değişkenini kontrol edin
            cursor.close()
            connection.close()

    return urls


# Ana fonksiyon
def main(city):
    # Neo4j driver oluşturma
    driver = GraphDatabase.driver(uri, auth=(username, password))

    urls = read_urls_from_mysql(city)

    # Tüm sayfalardaki linkleri çekme ve Neo4j'ye ekleme
    for url in urls:
        try:
            response = requests.get(url, timeout=5)  # Set a timeout for the request
            response.raise_for_status()  # Raise an HTTPError if the response was unsuccessful
            all_links = get_all_links(url)
            add_links_to_neo4j(driver, url, all_links, depth=0)
        except RequestException as e:
            print(f"Skipping {url} due to error: {e}")
            continue  # Skip to the next URL in case of an error

    # Neo4j driver kapatma
    driver.close()

def addUrl(urlinput):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    urls = []
    urls.append(urlinput)

    # Tüm sayfalardaki linkleri çekme ve Neo4j'ye ekleme
    for url in urls:
        # Ana sayfadaki linkleri al
        if url.endswith('/'):
            url = url[:-1] 
        all_links = get_all_links(url)
        add_links_to_neo4j(driver, url, all_links, depth=0)

    # Neo4j driver kapatma
    driver.close()



def addIp(ipinput):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    urls = []
    urls.append(f"http://{ipinput}")
    # Tüm sayfalardaki linkleri çekme ve Neo4j'ye ekleme
    for url in urls:
        # Ana sayfadaki linkleri al
        all_links = get_all_links(url)
        add_links_to_neo4j(driver, url, all_links, depth=0)

    # Neo4j driver kapatma
    driver.close()
    

def generate_ip_range(start_ip, end_ip):
    start_parts = start_ip.split('.')
    end_parts = end_ip.split('.')

    if start_parts[:3] == end_parts[:3]:
        if int(start_parts[3]) > int(end_parts[3]):
            raise ValueError("End IP must be greater than start IP")
        ip_list = []
        for i in range(int(start_parts[3]), int(end_parts[3]) + 1):
            ip = '.'.join(start_parts[:3]) + '.' + str(i)
            ip_list.append(ip)
        return ip_list
    else:
        raise ValueError("Start and end IP addresses must be in the same subnet")

def addIpRange(ip1, ip2):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    urls = []

    # Generate IP range and append to urls list
    ip_range = generate_ip_range(ip1, ip2)
    for ip in ip_range:
        urls.append(f"http://{ip}")

    # Process each URL (fetch links and add to Neo4j)
    for url in urls:
        try:
            response = requests.get(url, timeout=5)  # Set a timeout for the request
            response.raise_for_status()  # Raise an HTTPError if the response was unsuccessful
            all_links = get_all_links(url)
            add_links_to_neo4j(driver, url, all_links, depth=0)
        except RequestException as e:
            print(f"Skipping {url} due to error: {e}")
            continue  # Skip to the next URL in case of an error

    # Close Neo4j driver
    driver.close()


#backend part

@app.route('/neo4j-api', methods=['GET'])
def get_neo4j_data():
    try:
        query = "MATCH (n)-[r]->(m) RETURN n, r, m"
        result = graph.run(query)

        nodes = {}
        edges = []

        for record in result:
            node1 = record['n']
            node2 = record['m']
            relationship = record['r']

            # Serialize node properties
            def serialize_node(node):
                return {
                    "id": node.identity,
                    "properties": dict(node)
                }

            # Add node1 if not already added
            if node1.identity not in nodes:
                nodes[node1.identity] = serialize_node(node1)

            # Add node2 if not already added
            if node2.identity not in nodes:
                nodes[node2.identity] = serialize_node(node2)

            # Add the relationship as an edge
            edges.append({
                "from": node1.identity,
                "to": node2.identity,
                "label": relationship.__class__.__name__  # Get the relationship type
            })

        return jsonify({"nodes": list(nodes.values()), "edges": edges})

    except Exception as e:
        print(f'Error fetching graph data: {e}')
        return jsonify({"error": "Internal server error"}), 500

@app.route('/neo4j-city', methods=['GET'])
def get_city_link():
    try:
        city = request.args.get('city')
        main(city = city)
        return "Links for {} city added to Neo4j successfully!".format(city)
    except Exception as e:
        print("Error occurred:", str(e))
        return str(e), 500

@app.route('/neo4j-urlinput', methods=['GET'])
def get_url_link():
    try:
        urlinput = request.args.get('urlinput')
        addUrl(urlinput = urlinput)
        return "Links for {} url added to Neo4j successfully!".format(urlinput)
    except Exception as e:
        print("Error occurred:", str(e))
        return str(e), 500


@app.route('/neo4j-ipinput', methods=['GET'])
def get_ip_link():
    try:
        ipinput = request.args.get('ipinput')
        addIp(ipinput = ipinput)
        return "Links for {} ip added to Neo4j successfully!".format(ipinput)
    except Exception as e:
        print("Error occurred:", str(e))
        return str(e), 500
    


@app.route('/neo4j-delete', methods=['GET'])
def delete_link():
    try:
        query = "MATCH (n:Page) DETACH DELETE n"
        result = graph.run(query)
        return "Links delete to Neo4j successfully!"
    except Exception as e:
        print("Error occurred:", str(e))
        return str(e), 500


@app.route('/neo4j-depth', methods=['GET'])
def get_depth():
    global MAX_DEPTH 
    try:
        depthinput = request.args.get('depthinput')
        MAX_DEPTH = int(depthinput)
        return "Select {} depth successfully!".format(depthinput)
    except Exception as e:
        print("Error occurred:", str(e))
        return str(e), 500


@app.route('/neo4j-count', methods=['GET'])
def count_link():
    try:
        query = "MATCH (n:Page {is_root: true})-[r]->(m)  RETURN n.url AS url, COUNT(r) AS relationship_count ORDER BY relationship_count DESC"
        result = graph.run(query)
        
        data = []
        for record in result:
            data.append({"url": record["url"], "relationship_count": record["relationship_count"]})
        print("Data to be returned:", data)  # Log the data
        return jsonify(data)
    except Exception as e:
        print("Error occurred:", str(e))
        return str(e), 500
        
@app.route('/neo4j-incoming', methods=['GET'])
def incoming_link():
    try:
        query = """
        MATCH (n:Page {is_root: true})-[r1]->(m)<-[r2]-(n2:Page {is_root: true})
        WITH n, m, n2, r2, SPLIT(m.url, '/')[0] AS m_base_url
        WHERE m_base_url CONTAINS n2.url
        RETURN n2.url AS url, COUNT(r2) AS relationship_count
        ORDER BY relationship_count DESC
        """
        result = graph.run(query)
        
        data = []
        for record in result:
            data.append({"url": record["url"], "relationship_count": record["relationship_count"]})

        return jsonify(data)
    except Exception as e:
        print("Error occurred:", str(e))
        return str(e), 500

@app.route('/neo4j-iprangesearcher', methods=['GET'])
def iprangesearcher():
    try:
        ipinput1 = request.args.get('ipinput1')
        ipinput2 = request.args.get('ipinput2')
        addIpRange(ipinput1, ipinput2)
        return "Links for {} and {} added to Neo4j successfully!".format(ipinput1, ipinput2)
    except Exception as e:
        print("Error occurred:", str(e))
        return str(e), 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)