from datetime import datetime, timedelta
import requests
import json
import openpyxl
from station_list import ARG_STATION_LIST, AAWS_STATION_LIST, AWS_STATION_LIST, AWS2_STATION_LIST


def get_rainfall_last_entries(stations):
    stations = [station['id_stn'] for station in ARG_STATION_LIST]
    # Langkah 1: Menghasilkan URL dan tanggal dinamis
    tanggal_sekarang = datetime.now()
    tanggal_sebelumnya = tanggal_sekarang - timedelta(days=1)
    formatted_date = tanggal_sebelumnya.strftime('log-%d-%m-%Y.txt')
    dynamic_date = tanggal_sebelumnya.strftime('%d%m%Y')  # Format tanggal menjadi DDMMYYYY

    url_dinamis = f"http://202.90.198.212/logger/{formatted_date}"

    # Langkah 2: Mengunduh dan memproses data
    response = requests.get(url_dinamis)
    if response.status_code == 200:
        data_string = response.text
        last_entries = {}

        for line in data_string.strip().split('\n'):
            parts = line.split(';')
            if len(parts) > 3 and parts[0] in '':
                station_code = parts[0]
                date_time = parts[1]
                # Pengecekan DateTime format menjadi dinamis
                if date_time.startswith(dynamic_date):
                    last_entries[stations] = {
                        'DateTime': date_time,
                        'Rainfall': parts[2]
                    }

        return last_entries

        for line in data_string.strip().split('\n'):
            parts = line.split(';')
            if len(parts) > 3 and parts[0] in stations:
                station_code = parts[0]
                date_time = parts[1]
                # Pengecekan DateTime format menjadi dinamis
                if date_time.startswith(dynamic_date):
                    # Pengeceualian untuk STA0259
                    if station_code == 'STA0259':
                        rainfall_index = 3
                    else:
                        rainfall_index = 2
                    last_entries[stations] = {
                        'DateTime': date_time,
                        'Rainfall': parts[rainfall_index]  # Menggunakan indeks yang disesuaikan
                    }
        return last_entries
    else:
        print(f"Error mengunduh data: Status code {response.status_code}")
        return {}


def print_rainfall_report(last_entries, stations):
    stations = [station['id_stn'] for station in ARG_STATION_LIST]
    # Fungsi untuk mencetak hasil dalam format yang diinginkan, terurut sesuai station_codes
    i = 1
    for station_code in stations:
        if station_code in last_entries:
            data = last_entries[stations]
            rainfall_value = float(data['Rainfall'])  # Konversi nilai curah hujan ke float
            # Mencetak nilai dalam format float dengan satu angka desimal
            # print(f"{i}. {station_code} Curah Hujan {rainfall_value:.1f} mm")
            i += 1


# # Contoh penggunaan
# station_codes = ['150111', 'STA0259', '150108', '150115', '14032795', '150113', '150114', '150109',
#                  '14032793', '150106', '150107', '150112', 'STA0203', 'STA0008', 'STA0009', '150110',
#                  'STA0178', '150262', '150259', '150261', '150260', 'STG1014']
last_entries = get_rainfall_last_entries(stations)
last_entries_json = json.dumps(last_entries, indent=4)

# Mencetak atau menggunakan JSON string
print(last_entries_json)

# Mencetak laporan curah hujan dengan urutan sesuai station_codes
print_rainfall_report(last_entries, stations)


def download_rainfall_data_aaws(url, stations):
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
                    # Data curah hujan terletak di indeks ke-8
                    rainfall_data[station] = float(data[8].strip()) if len(data) > 8 else 0.0  # indeks dimulai dari 0
        return rainfall_data
    else:
        return "Gagal mengakses data."


# Menghitung tanggal yang diinginkan (yaitu, satu hari sebelum tanggal saat ini)
tanggal_dinamis = datetime.now() - timedelta(days=1)

# Format tanggal untuk digunakan dalam URL
tanggal_format_url = tanggal_dinamis.strftime("%d-%m-%Y")

# Membuat URL dinamis
url_dinamis = f"http://202.90.198.212/logger/ftp/logAAWS-{tanggal_format_url}.txt"

# Stasiun yang data curah hujannya ingin diambil
stations = ['STA3209', 'sta3032', 'sta3212', 'STS1001']

# Download dan cetak data curah hujan
rainfall_data_aaws = download_rainfall_data_aaws(url_dinamis, stations)

# Mendapatkan tanggal dan waktu saat ini untuk mencetak bersama dengan data
waktu_sekarang = datetime.now()

# Format untuk mencetak tanggal dan waktu
format_waktu = "%d-%m-%Y %H:%M:%S"

# Cetak hasil dengan tanggal, waktu, dan datetime data
# print(f"Data curah hujan pada {tanggal_format_url}, diakses pada {waktu_sekarang.strftime(format_waktu)}:")
# for station, rainfall in rainfall_data_aaws.items():
#     print(f"{station}: Curah Hujan {rainfall} mm")

rainfall_data_json = json.dumps(rainfall_data_aaws, indent=4)

# Mencetak atau menggunakan JSON string
print(rainfall_data_json)


def download_rainfall_data_aws(url, stations):
    # Mengirim request ke URL
    response = requests.get(url)
    if response.status_code == 200:
        lines = response.text.split('\n')
        # Mencari data untuk stasiun yang diinginkan
        rainfall_data = {}
        for line in lines:
            for station in stations:
                if station in line:
                    data = line.split(',')
                    # Data curah hujan terletak di indeks ke-10
                    rainfall_data[station] = float(data[10]) if len(data) > 10 else 0.0
        return rainfall_data
    else:
        return "Gagal mengakses data."


# Menghitung tanggal yang diinginkan (yaitu, satu hari sebelum tanggal saat ini)
tanggal_dinamis = datetime.now() - timedelta(days=1)

# Format tanggal untuk digunakan dalam URL
tanggal_format_url = tanggal_dinamis.strftime("%d-%m-%Y")

# Membuat URL dinamis
url_dinamis = f"http://202.90.198.212/logger/ftp/logAWS-{tanggal_format_url}.txt"

# Stasiun yang data curah hujannya ingin diambil
stations = ['STA2068', '160051', '160044']

# Download dan cetak data curah hujan
rainfall_data_aws = download_rainfall_data_aws(url_dinamis, stations)

# Mendapatkan tanggal dan waktu saat ini untuk mencetak bersama dengan data
waktu_sekarang = datetime.now()

# Format untuk mencetak tanggal dan waktu
format_waktu = "%d-%m-%Y %H:%M:%S"

# Cetak hasil dengan tanggal, waktu, dan datetime data
# print(f"Data curah hujan pada {tanggal_format_url}, diakses pada {waktu_sekarang.strftime(format_waktu)}:")
# for station, rainfall in rainfall_data_aws.items():
#     print(f"{station}: Curah Hujan {rainfall} mm")

rainfall_data_json = json.dumps(rainfall_data_aws, indent=4)

# Mencetak atau menggunakan JSON string
print(rainfall_data_json)


def download_rainfall_data_aws2(url, stations):
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
rainfall_data_aws2 = download_rainfall_data_aws2(url_dinamis, stations)

# Mendapatkan tanggal dan waktu saat ini untuk mencetak bersama dengan data
waktu_sekarang = datetime.now()

# Format untuk mencetak tanggal dan waktu
format_waktu = "%d-%m-%Y %H:%M:%S"

# Cetak hasil dengan tanggal, waktu, dan datetime data
# print(f"Data curah hujan pada {tanggal_format_url}, diakses pada {waktu_sekarang.strftime(format_waktu)}:")
# for station, data in rainfall_data_aws2.items():
#     print(f"{station}: {data['rainfall']} mm, data datetime: {data['datetime']}")

rainfall_data_json = json.dumps(rainfall_data_aws2, indent=4)

# Mencetak atau menggunakan JSON string
print(rainfall_data_json)