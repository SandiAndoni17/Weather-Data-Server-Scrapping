from datetime import datetime, timedelta
import requests

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
    else:
        print(f"Error mengunduh data: Status code {response.status_code}")
        return {}

from datetime import datetime, timedelta
import requests

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

def print_rainfall_report(last_entries, station_codes):
    # Fungsi untuk mencetak hasil dalam format yang diinginkan, terurut sesuai station_codes
    i = 1
    for station_code in station_codes:
        if station_code in last_entries:
            data = last_entries[station_code]
            rainfall_value = float(data['Rainfall'])  # Konversi nilai curah hujan ke float
            # Mencetak nilai dalam format float dengan satu angka desimal
            print(f"{i}. {station_code} Curah Hujan {rainfall_value:.1f} mm")
            i += 1

# Contoh penggunaan
station_codes = ['150111', 'STA0259', '150108', '150115', '14032795', '150113', '150114', '150109',
                 '14032793', '150106', '150107', '150112', 'STA0203', 'STA0008', 'STA0009', '150110',
                 'STA0178', '150262', '150259', '150261', '150260', 'STG1014']
last_entries = get_rainfall_last_entries(station_codes)

# Mencetak laporan curah hujan dengan urutan sesuai station_codes
print_rainfall_report(last_entries, station_codes)
