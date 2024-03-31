from datetime import datetime, timedelta
import requests

def get_rainfall_last_entries(station_codes):
    # Langkah 1: Menghasilkan URL dinamis
    # Mendapatkan tanggal saat ini
    tanggal_sekarang = datetime.now()

    # Mengurangi dengan satu hari untuk tanggal "kemarin"
    tanggal_sebelumnya = tanggal_sekarang - timedelta(days=1)

    # Memformat tanggal sesuai format URL (log-DD-MM-YYYY.txt)
    formatted_date = tanggal_sebelumnya.strftime('log-%d-%m-%Y.txt')

    # Membuat URL dinamis
    url_dinamis = f"http://202.90.198.212/logger/{formatted_date}"

    # Langkah 2: Mengunduh dan memproses data
    # Mengunduh data dari URL
    response = requests.get(url_dinamis)
    if response.status_code == 200:
        data_string = response.text
        # Memproses teks untuk mengekstrak data
        last_entries = {}
        for line in data_string.strip().split('\n'):
            parts = line.split(';')
            if len(parts) > 3 and parts[0] in station_codes:
                station_code = parts[0]
                last_entries[station_code] = {
                    'DateTime': parts[1],
                    'Rainfall': parts[2]
                }
        return last_entries
    else:
        print(f"Error mengunduh data: Status code {response.status_code}")
        return {}

# Contoh penggunaan
station_codes = ['150111', 'STA0259', '150108','150115','14032795','150113','150114','150109',
                 '14032793','150106','150107','150112','STA0203','STA0008','STA0009','150110',
                 'STA0178','150262','150259','150261','150260''STG1014']
last_entries = get_rainfall_last_entries(station_codes)
print(last_entries)
