import requests
from datetime import datetime, timedelta

def download_rainfall_data(url, stations):
    # Mengirim request ke URL
    response = requests.get(url)
    if response.status_code == 200:
        lines = response.text.split('\n')
        # Mencari data untuk stasiun yang diinginkan
        rainfall_data = {}
        for line in lines:
            for station in stations:
                if line.startswith(station):
                    data = line.split(';')
                    # Menentukan indeks curah hujan berdasarkan stasiun
                    rainfall_index = 18 if station == 'STA2295' else 7  # Indeks untuk STW1052 adalah 7
                    # Pastikan bahwa 'data' memiliki cukup elemen untuk indeks spesifik
                    if len(data) > rainfall_index:
                        rainfall_data[station] = {'rainfall': data[rainfall_index].strip(), 'datetime': data[1]}
        return rainfall_data
    else:
        return "Gagal mengakses data."

# Menghitung tanggal yang diinginkan (yaitu, satu hari sebelum tanggal saat ini)
tanggal_dinamis = datetime.now() - timedelta(days=1)

# Format tanggal untuk digunakan dalam URL
tanggal_format_url = tanggal_dinamis.strftime("%d-%m-%Y")

# Membuat URL dinamis
url_dinamis = f"http://202.90.198.212/logger/logfile/logAAWS-{tanggal_format_url}.txt"

# Stasiun yang data curah hujannya ingin diambil
stations = ['STA2295', 'STW1052']

# Download data curah hujan
rainfall_data = download_rainfall_data(url_dinamis, stations)

# Mendapatkan tanggal dan waktu saat ini untuk mencetak bersama dengan data
waktu_sekarang = datetime.now()

# Format untuk mencetak tanggal dan waktu
format_waktu = "%d-%m-%Y %H:%M:%S"

# Cetak hasil dengan tanggal, waktu, dan datetime data
print(f"Data curah hujan pada {tanggal_format_url}, diakses pada {waktu_sekarang.strftime(format_waktu)}:")
for station, data in rainfall_data.items():
    print(f"{station}: {data['rainfall']} mm, data datetime: {data['datetime']}")
