from datetime import datetime, timedelta
import requests
import json
import openpyxl
import os
from station_list import ARG_STATION_LIST, AAWS_STATION_LIST, AWS_STATION_LIST, AWS2_STATION_LIST
from openpyxl import load_workbook


def get_rainfall_last_entries(station_codes):
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
            if len(parts) > 3 and parts[0] in station_codes:
                station_code = parts[0]
                date_time = parts[1]
                # Pengecekan DateTime format menjadi dinamis
                if date_time.startswith(dynamic_date):
                    last_entries[station_code] = {
                        'DateTime': date_time,
                        'Rainfall': parts[2]
                    }

        return last_entries


def get_rainfall_last_entries(station_codes):
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
            if len(parts) > 3 and parts[0] in station_codes:
                station_code = parts[0]
                date_time = parts[1]
                # Pengecekan DateTime format menjadi dinamis
                if date_time.startswith(dynamic_date):
                    # Pengeceualian untuk STA0259
                    if station_code == 'STA0259':
                        rainfall_index = 3
                    else:
                        rainfall_index = 2
                    last_entries[station_code] = {
                        'DateTime': date_time,
                        'Rainfall': parts[rainfall_index]  # Menggunakan indeks yang disesuaikan
                    }
        return last_entries
    else:
        print(f"Error mengunduh data: Status code {response.status_code}")
        return {}

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
                        rainfall_data[station] = {'Rainfall': data[rainfall_index].strip(), 'datetime': data[1]}
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


def update_excel_sheet(sheet, last_entries, rainfall_data_aaws, rainfall_data_aws, rainfall_data_aws2, station_column_mapping):
    combined_data = {}
    combined_data.update(last_entries)
    combined_data.update(rainfall_data_aaws)
    combined_data.update(rainfall_data_aws)
    combined_data.update(rainfall_data_aws2)

    for station, data in combined_data.items():
        if station in station_column_mapping:
            column_cell = station_column_mapping[station]
            # Periksa apakah 'data' adalah kamus sebelum menggunakan metode 'get()'
            if isinstance(data, dict):
                sheet[column_cell] = data.get('Rainfall', '')  # Menggunakan get() untuk memastikan kunci 'Rainfall' ada
            else:
                sheet[column_cell] = data  # Jika 'data' bukan kamus, gunakan nilainya langsung



def main1():
    station_codes = ['150111', 'STA0259', '150108', '150115', '14032795', '150113', '150114', '150109',
                     '14032793', '150106', '150107', '150112', 'STA0203', 'STA0008', 'STA0009', '150110',
                     'sta0178', '150262', '150259', '150261', '150260', 'STG1014']
    last_entries = get_rainfall_last_entries(station_codes)
    rainfall_data = get_rainfall_last_entries(station_codes)

    # Memuat workbook dan mengaktifkan worksheet
    workbook = load_workbook(
        r'S:\FILE_RWID\PyCharmProjects\python-fundamental\Weather-Data-Server-Scrapping\Template.xlsx')
    sheet = workbook.active
    # Menambahkan judul dengan tanggal
    tanggal_kemarin = (datetime.now() - timedelta(days=1)).strftime('%d-%m-%Y')
    sheet['A1'] = f"Monitoring Data Curah Hujan ARG, AWS, dan AAWS Sumatera Utara per {tanggal_kemarin} Jam 00.00 UTC"

    station_column_mapping = {
        '150111': 'E4', 'STA0259': 'E5', '150108': 'E6', '150115': 'E7',
        '14032795': 'E8', '150113': 'E9', '150114': 'E10', '150109': 'E11',
        '14032793': 'E12', '150106': 'E13', '150107': 'E14', '150112': 'E15',
        'STA0203': 'E16', 'STA0008': 'E17', 'STA0009': 'E18', '150110': 'E19',
        'sta0178': 'E20', '150262': 'E21', '150259': 'E22', '150261': 'E23',
        '150260': 'E24', 'STG1014': 'E25', 'STA3209': 'E26', 'sta3032' : 'E27',
        'sta3212' : 'E28', 'STS1001':'E29', 'STA2068': 'E30', '160051':'E31',
        '160044':'E32', 'STA2295':'E33', 'STW1052':'E34'
    }
    update_excel_sheet(sheet, rainfall_data,  rainfall_data_aaws, rainfall_data_aws,rainfall_data_aws2,
                       station_column_mapping)

    # Simpan workbook yang telah diubah
    save_path = r'S:\FILE_RWID\PyCharmProjects\python-fundamental\Weather-Data-Server-Scrapping\Rainfall_Data.xlsx'
    workbook.save(save_path)


main1()