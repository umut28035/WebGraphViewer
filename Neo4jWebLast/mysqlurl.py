import mysql.connector
import os

# MySQL bağlantısını kurun
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="250421nurmur",
    database="cityurl"
)
cursor = db.cursor()

# Dosyaların bulunduğu klasörü belirtin
directory = 'City\City'  # Örneğin, 'City'

# Klasördeki her dosyayı sırayla oku ve veritabanına ekle
for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        city_name = filename.replace("_veriler.txt", "")
        with open(os.path.join(directory, filename), 'r') as file:
            lines = file.readlines()
            for line in lines[1:]:  # İlk satır şehir adı olduğu için atla
                url_address = line.strip()
                if url_address:  # Boş olmayan satırları ekle
                    if len(url_address) > 255:
                        url_address = url_address[:255]  # URL'yi 255 karakterle sınırla
                    sql = "INSERT INTO url_locations (url_address, city) VALUES (%s, %s)"
                    cursor.execute(sql, (url_address, city_name))

# Değişiklikleri kaydet ve bağlantıyı kapat
db.commit()
db.close()
