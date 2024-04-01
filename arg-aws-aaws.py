from datetime import datetime, timedelta
import requests

def get_rainfall_data(url_template, station_codes, date_format, datetime_index, rainfall_index, date_sub_path=False,
                      custom_split_char=';'):
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    formatted_date = yesterday.strftime('%d-%m-%Y')  # Pastikan format ini sesuai dengan yang diinginkan oleh URL
    dynamic_date = yesterday.strftime('%d%m%Y')  # Format tanggal menjadi DDMMYYYY

    # Pastikan placeholder untuk tanggal digantikan dengan nilai tanggal yang sebenarnya
    if date_sub_path:
        url = url_template.format(date=formatted_date)
    else:
        # Jika URL tidak membutuhkan sub path tanggal, pastikan tidak ada placeholder tanggal dalam url_template
        url = url_template

    try:
        response = requests.get(url)
        response.raise_for_status()  # Memastikan bahwa kita mendapatkan respons 'OK' dari server
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return {}


    last_entries = {}
    for line in response.text.strip().split('\n'):
        parts = line.split(custom_split_char)
        if len(parts) > max(datetime_index, rainfall_index) and parts[0] in station_codes:
            # Proses dan simpan data
            date_time = parts[datetime_index]
            if date_time.startswith(dynamic_date):
                last_entries[parts[0]] = {
                    'DateTime': date_time,
                    'Rainfall': parts[rainfall_index]
                }
    return last_entries

# Konfigurasi dan penggabungan data dari semua URL seperti sebelumnya...

# Pastikan sisanya kode Anda tidak berubah, hanya fungsi get_rainfall_data yang diperbarui



# Konfigurasi untuk setiap URL
configurations = [
    # URL asli dengan penyesuaian
    {
        "url_template": "http://202.90.198.212/logger/log-%d-%m-%Y.txt",
        "station_codes": ['150111', 'STA0259', '150108', '150115', '14032795', '150113', '150114', '150109',
                          '14032793', '150106', '150107', '150112', 'STA0203', 'STA0008', 'STA0009', '150110',
                          'STA0178', '150262', '150259', '150261', '150260', 'STG1014'],
        # Daftar semua kode stasiun relevan
        "date_format": "log-%d-%m-%Y.txt",
        "datetime_index": 1,
        "rainfall_index": 2,
        "date_sub_path": True
    },
    # Konfigurasi untuk URL tambahan 1
    {
        "url_template": "http://202.90.198.212/logger/logfile/logAAWS-{date}.txt",
        "station_codes": ['STA2295', 'stw1052'],
        "date_format": "%d-%m-%Y",
        "datetime_index": 1,
        "rainfall_index": 18,
        "date_sub_path": True
    },
    # Konfigurasi untuk URL tambahan 2
    {
        "url_template": "http://202.90.198.212/logger/ftp/logAAWS-{date}.txt",
        "station_codes": ['STA3209', 'STA3032', 'STA3212', 'STS1001'],
        "date_format": "%d-%m-%Y",
        "datetime_index": 0,  # Menggunakan contoh data yang diberikan, ini mungkin perlu disesuaikan
        "rainfall_index": 9,
        "date_sub_path": True,
        "custom_split_char": ';'  # Default, bisa diubah jika format berbeda
    },
    # Konfigurasi untuk URL tambahan 3
    {
        "url_template": "http://202.90.198.212/logger/ftp/logAWS-{date}.txt",
        "station_codes": ['160051', '160044'],
        "date_format": "%d-%m-%Y",
        "datetime_index": 0,  # Menggunakan format yang diberikan, perlu disesuaikan jika format berbeda
        "rainfall_index": 10,
        "date_sub_path": True,
        "custom_split_char": ','  # Menggunakan koma sebagai pemisah karena format yang berbeda
    }
]

# Penggabungan dan pemrosesan data dari semua URL
all_last_entries = {}
for config in configurations:
    last_entries = get_rainfall_data(**config)
    all_last_entries.update(last_entries)


# Fungsi untuk mencetak laporan
def print_rainfall_report(last_entries, station_codes):
    i = 1
    for station_code in station_codes:
        if station_code in last_entries:
            data = last_entries[station_code]
            rainfall_value = float(data['Rainfall'])  # Konversi nilai curah hujan ke float
            print(f"{i}. {station_code} Curah Hujan {rainfall_value:.1f} mm pada {data['DateTime']}")
            i += 1


# Mencetak laporan curah hujan dengan urutan sesuai station_codes
print_rainfall_report(all_last_entries, configurations[0]["station_codes"])
