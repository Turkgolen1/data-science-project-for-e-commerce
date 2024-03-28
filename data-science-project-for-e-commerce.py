import requests
from bs4 import BeautifulSoup
import time
import random
import mysql.connector



import mysql.connector

class MySQLConnector:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def insert_data(self, product_data):
        query = "INSERT INTO product_data (stok_sayısı, urun_kodu, urun_barkodu, urun_adı,urun_linki) VALUES (%s, %s, %s, %s,%s)"
        values = (product_data.stok_sayısı, product_data.urun_kodu, product_data.urun_barkodu, product_data.urun_adı,product_data.urun_linki)

        self.cursor.execute(query, values)
        self.connection.commit()

    def close_connection(self):
        self.connection.close()




class ProductData:
    def __init__(self, stok_sayısı, urun_kodu, urun_barkodu, urun_adı,urun_linki):
        self.stok_sayısı = stok_sayısı
        self.urun_kodu = urun_kodu
        self.urun_barkodu = urun_barkodu
        self.urun_adı = urun_adı
        self.urun_linki=urun_linki


url = "https://www.*********.com"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("1. Ana sayfa başarıyla alındı.")

    soup = BeautifulSoup(response.text, 'html.parser')

    print("soup çalıştı")

    # Tüm ürün bağlantılarını bul
    kaynak_kodları = soup.find_all("a", {"class": "plp-url"})
    urun_linkleri = [urun_linki.get("href") for urun_linki in kaynak_kodları]

    print("ürün linkleri alındı")

    print(urun_linkleri)

    for i, urun_linki in enumerate(urun_linkleri):
        # Her ürün için bir bekleme süresi ekleyerek ürün sayfasının kaynak kodunu çek
        a = random.uniform(2, 3)
        time.sleep(a)  # Her ürün için 2-3 saniye bekleme süresi

        urun_response = requests.get(urun_linki)

        if urun_response.status_code == 200:
            print(f"{i+1}. ürün sayfası başarıyla alındı.")

            urun_soup = BeautifulSoup(urun_response.text, 'html.parser')

            # Stok bilgisini çekmek için gerekli işlemleri yap
            stok_bilgisi = urun_soup.find('button', {'id': 'mobilAddOrderCart'})
            
            
            if stok_bilgisi and 'data-stock' in stok_bilgisi.attrs:
                print(f"Stok Bilgisi {i+1}:", stok_bilgisi['data-stock'])
                stok_sayısı=int(stok_bilgisi['data-stock'])
                urun_kodu=stok_bilgisi['data-productmpn']
                urun_barkodu=stok_bilgisi['data-barcode']
                urun_adı=stok_bilgisi['data-productname']
                print(urun_kodu)
                print(urun_barkodu)
                print(urun_linki)
                print(urun_adı)
                print(stok_sayısı)

                # ProductData sınıfını kullanarak ürün bilgilerini sakla
                product_data = ProductData(stok_sayısı, urun_kodu, urun_barkodu, urun_adı,urun_linki)

                # MySQLConnector kullanarak veritabanına ekle
                mysql_connector = MySQLConnector(host="localhost", user="root", password="123456", database="*********")
                try:
                    mysql_connector.insert_data(product_data)
                except Exception as e:
                    print(f"{i+1}. ürün için veri eklenirken hata oluştu: {e}")
                
            else:
                print(f"{i+1}. ürün için stok bilgisi bulunamadı.")
        
        else:
            print(f"{i+1}. ürün sayfasını alırken hata: {urun_response.status_code}")
    mysql_connector.close_connection()

else:
    print(f"Hata: Ana sayfa alınamadı. Status Code: {response.status_code}")

