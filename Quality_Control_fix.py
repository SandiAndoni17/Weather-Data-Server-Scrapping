from datetime import datetime, timedelta
import requests
import json
import openpyxl
import os
from station_list import ARG_STATION_LIST, AAWS_STATION_LIST, AWS_STATION_LIST, AWS2_STATION_LIST
import schedule
import time
from openpyxl import load_workbook
from openpyxl.styles import Alignment

station_descriptions = {
    '150111': 'ARG Arse',
    'STA0259': 'ARG Bahorok',
    '150108': 'ARG Harian',
    '150115': 'ARG Kualuh Selatan',
    '14032795': 'ARG Lubuk Barumun',
    '150113': 'ARG Mompang',
    '150114': 'ARG Patiluban',
    '150109': 'ARG Salak',
    '14032793': 'ARG Simanindo',
    '150106': 'ARG Sinabung',
    '150107': 'ARG Sipoholon',
    '150112': 'ARG Sipispis',
    'STA0203': 'ARG Kota Pinang',
    'STA0008': 'ARG Tapanuli',
    'STA0009': 'ARG Sidikalang',
    '150110': 'ARG Pakkat',
    'sta0178': 'ARG Gurgur Balige',
    '150262': 'ARG Merek',
    '150259': 'ARG Raya',
    '150261': 'ARG Tiga Binanga',
    '150260': 'ARG PDAM Sunggal',
    'STG1014': 'ARG Teluk Dalam',
    'STA3209': 'AAWS Batubara',
    'sta3032': 'AAWS Deli Serdang',
    'sta3212': 'AAWS Hinai Langkat',
    'STS1001': 'AAWS Sei Rejo',
    'STA2068': 'AWS Staklim Deli Serdang',
    '160051': 'AWS Kebun Sosa',
    '160044': 'AWS Parapat',
    'STA2295': 'AWS Dolok Sanggul',
    'STW1052': 'AWS Jawa Maraja Bah Jambi'
}



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
# def extract_datetime_from_line(line):
#     parts = line.split(' ')
#     filename = parts[0]  # Mengambil bagian nama file
#     datetime_part = filename[9:-4]  # Mengambil bagian tanggal dan waktu
#     return datetime_part

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
                    data_datetime = line.split(' ')[0]
                    datetime_part = data_datetime[7:-4]
                    # Data curah hujan terletak di indeks ke-8
                    rainfall_data[station] = {'rainfall': float(data[8].strip()) if len(data) > 8 else 0.0,
                                              'datetime': datetime_part }# indeks dimulai dari 0
                    #print(f"AAWS Data for {station}: {rainfall_data[station]}")
        return rainfall_data
    else:
        return "Gagal mengakses data."

def download_rainfall_data_aws(url, stations):
    # Mengirim request ke URL
    response = requests.get(url)
    if response.status_code == 200:
        lines = response.text.split('\n')
        rainfall_data = {}
        for line in lines:
            for station in stations:
                if station in line:
                    data = line.split(',')
                    filename = line.split(' ')[0]  # Asalnya: 'sta160051202405132340.txt' atau format lain
                    if station in ['160051', '160044']:
                        datetime_part = filename[6:-4]  # Memotong bagian datetime dari filename
                    elif station == 'STA2068':
                        datetime_part = filename[7:-4]  # Memotong bagian datetime untuk STA2068
                    else:
                        datetime_part = filename[9:-4]  # Memotong bagian datetime untuk stasiun lain

                    # Data curah hujan terletak di indeks ke-10
                    rainfall_data[station] = {
                        'datetime': datetime_part,
                        'rainfall': float(data[10]) if len(data) > 10 else 0.0
                    }
                    #print(f"AWS Data for {station}: {rainfall_data[station]}")
        return rainfall_data
    else:
        return "Gagal mengakses data."


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
                    rainfall_index = 18 if station == 'STA2295' else 7
                    # Pastikan bahwa 'data' memiliki cukup elemen untuk indeks spesifik
                    if len(data) > rainfall_index:
                        rainfall_data[station] = {'Rainfall': data[rainfall_index].strip(), 'datetime': data[1]}
        return rainfall_data
    else:
        return "Gagal mengakses data."


def update_excel_sheet(sheet, last_entries, rainfall_data_aaws, rainfall_data_aws, rainfall_data_aws2, station_column_mapping, station_descriptions):
    combined_data = {}
    combined_data.update(last_entries)
    combined_data.update(rainfall_data_aaws)
    combined_data.update(rainfall_data_aws)
    combined_data.update(rainfall_data_aws2)

    # Center alignment for cells in column E from E27 to E34
    center_alignment = Alignment(horizontal='center')

    # Definisi urutan tetap stasiun
    fixed_order_stations = [
        '150111', 'STA0259', '150108', '150115', '14032795', '150113', '150114', '150109',
        '14032793', '150106', '150107', '150112', 'STA0203', 'STA0008', 'STA0009', '150110',
        'sta0178', '150262', '150259', '150261', '150260', 'STG1014', 'STA3209', 'sta3032',
        'sta3212', 'STS1001', 'STA2068', '160051', '160044', 'STA2295', 'STW1052'
    ]

    index = 1
    for station in fixed_order_stations:
        data = combined_data.get(station, {'DateTime': '', 'Rainfall': ''})
        description = station_descriptions.get(station, 'Unknown Station')
        datetime_str = data.get('DateTime', data.get('datetime', ''))
        rainfall = data.get('Rainfall', data.get('rainfall', ''))
        time_part = datetime_str[-4:]  # Mengambil bagian HHMM dari datetime

        # Mendefinisikan validitas data berdasarkan waktu
        hour = int(time_part[:2]) if len(time_part) == 4 and time_part.isdigit() else 24  # Asumsikan data tidak valid jika format jam salah
        valid_data_message = "" if hour >= 23 else " Data tidak valid, silahkan cek data jam 00.00"

        # Mencetak dengan format yang diinginkan
        print(f"{index}. {station}\t{description} {datetime_str} {rainfall}{valid_data_message}")
        index += 1  # Meningkatkan index untuk setiap stasiun

        if station in station_column_mapping:
            column_cell = station_column_mapping[station]
            # Apply center alignment for specific cells
            if column_cell in ['E27', 'E28', 'E29', 'E30', 'E31', 'E32', 'E33', 'E34']:
                sheet[column_cell].alignment = center_alignment

            formatted_value = f"{float(rainfall):.1f}" if rainfall not in ["Data Tidak Valid", ""] else "Data Tidak Valid"
            sheet[column_cell] = formatted_value
def main():
    # Define stations and URLs
    stations_aaws = ['STA3209', 'sta3032', 'sta3212', 'STS1001']
    tanggal_sekarang_formatted = datetime.now().strftime('%d-%m-%Y')
    tanggal_dinamis = datetime.now() - timedelta(days=1)
    tanggal_format_url = tanggal_dinamis.strftime("%d-%m-%Y")
    url_aaws = f"http://202.90.198.212/logger/ftp/logAAWS-{tanggal_format_url}.txt"

    stations_aws = ['STA2068', '160051', '160044']
    url_aws = f"http://202.90.198.212/logger/ftp/logAWS-{tanggal_format_url}.txt"

    stations_aws2 = ['STA2295', 'STW1052']
    url_aws2 = f"http://202.90.198.212/logger/logfile/logAAWS-{tanggal_format_url}.txt"

    station_codes = ['150111', 'STA0259', '150108', '150115', '14032795', '150113', '150114', '150109',
                     '14032793', '150106', '150107', '150112', 'STA0203', 'STA0008', 'STA0009', '150110',
                     'sta0178', '150262', '150259', '150261', '150260', 'STG1014']

    last_entries = get_rainfall_last_entries(station_codes)
    #print(f"Last Entries: {last_entries}")

    rainfall_data_aaws = download_rainfall_data_aaws(url_aaws, stations_aaws)
    #print(f"Rainfall Data AAWS: {rainfall_data_aaws}")

    rainfall_data_aws = download_rainfall_data_aws(url_aws, stations_aws)
    #print(f"Rainfall Data AWS: {rainfall_data_aws}")

    rainfall_data_aws2 = download_rainfall_data_aws2(url_aws2, stations_aws2)
    #print(f"Rainfall Data AWS2: {rainfall_data_aws2}")

    workbook = load_workbook(r'D:\PYTHON\Weather-Data-Server-Scrapping\Template.xlsx')
    sheet = workbook.active

    tanggal_kemarin = tanggal_dinamis.strftime('%d-%m-%Y')
    sheet['A1'] = f"Monitoring Data Curah Hujan ARG, AWS, dan AAWS Sumatera Utara per {tanggal_sekarang_formatted} Jam 00.00 UTC"

    station_column_mapping = {
        '150111': 'E4', 'STA0259': 'E5', '150108': 'E6', '150115': 'E7',
        '14032795': 'E8', '150113': 'E9', '150114': 'E10', '150109': 'E11',
        '14032793': 'E12', '150106': 'E13', '150107': 'E14', '150112': 'E15',
        'STA0203': 'E16', 'STA0008': 'E17', 'STA0009': 'E18', '150110': 'E19',
        'sta0178': 'E20', '150262': 'E21', '150259': 'E22', '150261': 'E23',
        '150260': 'E24', 'STG1014': 'E25', 'STA3209': 'E26', 'sta3032': 'E27',
        'sta3212': 'E28', 'STS1001': 'E29', 'STA2068': 'E30', '160051': 'E31',
        '160044': 'E32', 'STA2295': 'E33', 'STW1052': 'E34'
    }

    update_excel_sheet(sheet, last_entries, rainfall_data_aaws, rainfall_data_aws, rainfall_data_aws2, station_column_mapping, station_descriptions)

    save_path = fr'D:\File_Monitoring_Hujan_Aloptama_Harian\Monitoring Hujan Alat Otomatis Tanggal {tanggal_sekarang_formatted}.xlsx'
    workbook.save(save_path)



if __name__ == "__main__":
    main()
    #Calling main1 to run the script
    # schedule.every().day.at("07:33").do(main)  # Menjadwalkan skrip untuk dijalankan setiap hari jam 07.30
    # while True:
    #     schedule.run_pending()  # Menjalankan tugas yang sudah dijadwalkan
    #     time.sleep(60)


