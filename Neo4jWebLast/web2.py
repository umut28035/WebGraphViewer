from flask import Flask, request, jsonify
from flask_cors import CORS
from py2neo import Graph, NodeMatcher
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from neo4j import GraphDatabase
import ipaddress
from requests.exceptions import RequestException

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

# Kök domainlerin listesi
root_domains = set()

def get_root_domain(url):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    # www.altalan.domain.com -> domain.com dönüşümü için
    netloc_parts = netloc.split('.')
    if len(netloc_parts) > 2 and (netloc_parts[-2] == 'com' or netloc_parts[-2] == 'edu' or netloc_parts[-2] == 'org' or  netloc_parts[-2] == 'gov'or  netloc_parts[-2] == 'k12' ):
        root_domain = '.'.join(netloc_parts[-3:])
    else:
        root_domain = '.'.join(netloc_parts[-2:])
    return root_domain

def get_all_links(url):
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    base_url = get_root_domain(url)
    print("base: " + base_url)
    #print("Base URL:", base_url)  # Base URL'yi kontrol et
    #www.cankaya.edu.tr webonline.cankya.edu.tr twiter.com
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('/') or href.endswith('\\'):
            href = href[:-1] 

        if href.startswith('http'):
            parsed_href = urlparse(href)
            #print(parsed_href)
            link_domain = parsed_href.netloc
            #print("ph " + link_domain)
            # Ana domain dışındaki linklerin domainini kontrol et
            if base_url != link_domain:
                # Ana domaini al
                root_domain = get_root_domain(href)
                #new_root_domain = parsed_href.scheme + '://' + root_domain
                new_root_domain = root_domain
                #print("Link Domain:", root_domain)  # Link Domainini kontrol et
                #print("new"  + new_root_domain)
                # Eğer linkin domaini "http" veya "https" ile başlıyorsa, bu linki kök olarak işaretle ve kök domainler listesine ekle
                if new_root_domain not in base_url:
                    if "www" in link_domain:
                        root_domains.add(parsed_href.scheme + '://www.' + root_domain)
                    else:
                        root_domains.add(parsed_href.scheme + '://' + root_domain)
                    #root_domains.add(parsed_href.scheme + '://www.' + root_domain)
                    links.append(href)  # Kök domainleri de link listesine eklemek gerekir

                else:
                    # Eğer linkin domaini "http" veya "https" ile başlamıyorsa, bu linki sadece düğüm olarak ekle
                    links.append(href)
                
    return links


# Diğer fonksiyonlar burada kalır...

MAX_DEPTH = 1

def add_links_to_neo4j(driver, root_url, links, depth):
    if depth >= MAX_DEPTH:
        return
    with driver.session() as session:
        child_links2 = set()
        # Ana sayfa düğümü oluştur
        session.write_transaction(create_node, root_url, is_root=True, depth=0)
        # Ana sayfadaki linklerle ilişkiyi kur
        for link in links:
            session.write_transaction(create_node, link, is_root=False, depth=depth+1)
            session.write_transaction(create_relationship, root_url, link)

            # Linkin altındaki linkleri al ve ilişki kur
            if depth + 1 < MAX_DEPTH:  # Max derinliğe ulaşılmadıysa
                child_links = get_all_links(link)
                add_links_to_neo4j(driver, link, child_links, depth + 1)
            # Alt bağlantılar arasında ilişki kur
                for child_link in child_links:
                    session.write_transaction(create_relationship, link, child_link)
                    if(child_link not in child_links2):
                        child_links2.add(child_link)
        #www.cankya.edu.tr
        # Kök domainleri kök olarak ekleyin
        for domain in root_domains:
            # "http://" veya "https://" ekleyerek ana domaini oluşturun
            domain_with_http = domain
            print("domain: " + domain)
            #print(domain)
            session.write_transaction(update_root_property, domain, is_root=True, depth=0)
            # Kök domain ile alt siteleri arasında ilişki kurun
            for link in links:
                #print("link: " + link)
                parsed_link = urlparse(link)
                base_link =  parsed_link.netloc
                #print(base_link +'!')

                if urlparse(domain).netloc in base_link  and link != domain:                 
                    session.write_transaction(create_relationship, domain, link)

            for child_link2 in child_links2:
                parsed_link2 = urlparse(child_link2)
                base_link2 =  parsed_link2.netloc
                #print(base_link +'!')
                    
                if urlparse(domain).netloc in base_link2  and child_link2 != domain:                 
                    session.write_transaction(create_relationship, domain, child_link2)
                    print("1: " + base_link2)
                    print("2: " + child_link2)

# Neo4j'ye düğüm ekleme işlemi
def create_node(tx, url, is_root, depth):
    result = tx.run("MATCH (page:Page {url: $url}) RETURN page", url=url)
    if not result.single():
        tx.run("MERGE (page:Page {url: $url, is_root: $is_root, depth: $depth})", url=url, is_root=is_root, depth=depth)

# Neo4j'ye ilişki ekleme işlemi
def create_relationship(tx, root_url, url):
    tx.run("MATCH (root:Page {url: $root_url}), (page:Page {url: $url}) "
           "MERGE (root)-[:HAS_LINK]->(page)", root_url=root_url, url=url)

def update_root_property(tx, url, is_root, depth):
    result = tx.run("MATCH (page:Page {url: $url}) RETURN page", url=url)
    if not result.single():
        #print(url)
        tx.run("MERGE (page:Page {url: $url, is_root: $is_root, depth: $depth})", url=url, is_root=is_root, depth=depth)
    else:
        #print(url + "!")
        tx.run("MATCH (page:Page {url: $url}) SET page.is_root = $is_root, page.depth = $depth", url=url, is_root=is_root, depth=depth)

def read_urls_from_file(filename):
    with open(filename, 'r') as file:
        urls = file.readlines()[1:]  # Start reading from the second line
    # Remove whitespace characters like `\n` at the end of each line
    urls = [url.strip() for url in urls]
    return urls

# Ana fonksiyon
def main(city):
    # Neo4j driver oluşturma
    driver = GraphDatabase.driver(uri, auth=(username, password))

    urls = read_urls_from_file(f"server/{city}.txt")

    # Tüm sayfalardaki linkleri çekme ve Neo4j'ye ekleme
    for url in urls:
        # Ana sayfadaki linkleri al
        all_links = get_all_links(url)
        add_links_to_neo4j(driver, url, all_links, depth=0)

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
        print(url)
        add_links_to_neo4j(driver, url, all_links, depth=0)

    # Neo4j driver kapatma
    driver.close()



def addIp(ipinput):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    urls = []
    urls.append(f"http://{ipinput}/")
    # Tüm sayfalardaki linkleri çekme ve Neo4j'ye ekleme
    for url in urls:
        # Ana sayfadaki linkleri al
        all_links = get_all_links(url)
        add_links_to_neo4j(driver, url, all_links, depth=0)

    # Neo4j driver kapatma
    driver.close()
    
#def generate_ip_range(start_ip, end_ip):
   # start = ipaddress.ip_address(start_ip)
    #end = ipaddress.ip_address(end_ip)
   #ip_list = [str(ip) for ip in range(int(start), int(end) + 1)]
   # return ip_list

def generate_ip_range(start_ip, end_ip):
    start_parts = start_ip.split('.')
    end_parts = end_ip.split('.')
    ip_list = []

    # Ensure the first three parts of the IP addresses are the same
    if start_parts[:3] == end_parts[:3]:
        for i in range(int(start_parts[3]), int(end_parts[3]) + 1):
            ip = '.'.join(start_parts[:3]) + '.' + str(i)
            ip_list.append(ip)
    else:
        raise ValueError("Start and end IP addresses must be in the same subnet")

    return ip_list

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
        query = "MATCH (n:Page {is_root: true})-[r]->(m)  RETURN n.url AS url, COUNT(r) AS relationship_count"
        result = graph.run(query)
        
        data = []
        for record in result:
            data.append({"url": record["url"], "relationship_count": record["relationship_count"]})

        return jsonify(data)
    except Exception as e:
        print("Error occurred:", str(e))
        return str(e), 500
@app.route('/neo4j-incoming', methods=['GET'])
def incoming_link():
    try:
        query = "MATCH (n:Page {is_root: true})<-[r]-(m)  RETURN n.url AS url, COUNT(r) AS relationship_count"
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