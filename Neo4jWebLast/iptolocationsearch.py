import requests
import threading
import time
from bs4 import BeautifulSoup
import sys
from collections import defaultdict


def process_ip_ranges(ip_ranges_filename):
    with open(ip_ranges_filename, 'r') as file:
        ip_ranges = file.readlines()

    output_lock = threading.Lock()
    output = []

    def process_ip_range(ip_range):
        start_ip, end_ip = ip_range.strip().split(' ')
        local_output = []
        
        for i in range(int(start_ip.split('.')[3]), int(end_ip.split('.')[3]) + 1):
            ip = start_ip.rsplit('.', 1)[0] + '.' + str(i)
            url = f"http://{ip}"
            
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    current_url = response.url
                    local_output.append(f"{ip}:{current_url}")
            except requests.RequestException as e:
                pass
        
        with output_lock:
            output.extend(local_output)

    threads = []
    for ip_range in ip_ranges:
        t = threading.Thread(target=process_ip_range, args=(ip_range,))
        threads.append(t)
        t.start()

        if len(threads) == 100:
            for t in threads:
                t.join()
            threads = []
            time.sleep(1)

    for t in threads:
        t.join()

    return output

def process_urls(output):
    output_lock = threading.Lock()
    success = []
    fail = []

    def process_url(ip, url):
        try:
            response = requests.get(f'{url}', headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [link.get('href') for link in soup.find_all('a') if link.get('href')]
            if links:
                with output_lock:
                    success.append(f"{ip}:{url}")
                print(f"Processed {url} successfully")
            else:
                with output_lock:
                    fail.append(f"{ip}:{url}")
                print(f"No links found for {url}")
        except Exception as e:
            with output_lock:
                fail.append(f"{ip}:{url}")
            print(f"Failed to process {url}: {e}")

    threads = []
    for line in output:
        ip, url = line.strip().split(':', 1)
        thread = threading.Thread(target=process_url, args=(ip, url))
        threads.append(thread)
        if len(threads) >= 100:
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            threads = []

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return success, fail

def process_city_info(success, api_key):
    def get_city_info(ip):
        url = f'https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={ip}&fields=city'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            city = data.get('city')
            return city
        elif response.status_code == 429:
            print("Rate limit exceeded. Program will exit.")
            sys.exit()
        else:
            print(f"Hata: IP {ip} için şehir bilgisi alınamadı. Hata kodu: {response.status_code}")
            return None

    cityinfos = []

    for line in success:
        parts = line.strip().split(':', 1)
        if len(parts) < 2:
            print(f"Hata: Geçersiz satır formatı - {line.strip()}")
            continue
        ip, url = parts[0], parts[1]
        print(f"Processing IP: {ip}, URL: {url}")
        city = get_city_info(ip)
        if city:
            city = city.replace('ı', 'i').replace('ö', 'o').replace('ü', 'u').replace('ğ', 'g').replace('ş', 's').replace('ç', 'c').replace('İ', 'I').replace('Ö', 'O').replace('Ü', 'U').replace('Ğ', 'G').replace('Ş', 'S').replace('Ç', 'C')
            cityinfos.append(f"{city}:{url}")
            print(f"{ip} için şehir bilgisi başarıyla eklendi.")
        else:
            print(f"{ip} için şehir bilgisi alınamadı, satır atlandı.")
            continue

    print("İşlem tamamlandı.")
    return cityinfos

def write_city_data(cityinfos):
    # Şehirlere göre grupla
    city_data = defaultdict(list)
    for line in cityinfos:
        parts = line.strip().split(':', 1)
        city = parts[0].replace('OSB', '').strip()
        ip_url = parts[1].strip().split(':')
        ip = ip_url[0].strip()
        url = ':'.join(ip_url[1:]).strip()
        city_data[city].append((ip, url))

    # Her şehir için ayrı dosyalara yaz
    for city, data in city_data.items():
        with open(f"{city}_data.txt", 'w') as f:
            f.write(f"{city}:\n")
            for ip, url in data:
                f.write(f"  {ip}{url}\n")

if __name__ == "__main__":
    ip_ranges_filename = "ip_ranges.txt"
    output = process_ip_ranges(ip_ranges_filename)
    success, fail = process_urls(output)
    api_key = '6194cb5c55f84c49baec1fa256f778ea'
    cityinfos = process_city_info(success, api_key)
    write_city_data(cityinfos)








