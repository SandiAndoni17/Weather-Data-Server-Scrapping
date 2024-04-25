from datetime import datetime, timedelta
import requests
import openpyxl
from openpyxl import load_workbook
from station_list import ARG_STATION_LIST, AAWS_STATION_LIST, AWS_STATION_LIST, AWS2_STATION_LIST


def get_rainfall_data(url, station_codes, dynamic_date):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Will raise an HTTPError for bad responses
        data = response.text
        last_entries = {}
        for line in data.strip().split('\n'):
            parts = line.split(';')
            if len(parts) > 3 and parts[0] in station_codes:
                station_code, date_time = parts[0], parts[1]
                rainfall_index = 3 if station_code == 'STA0259' else 2
                if date_time.startswith(dynamic_date):
                    last_entries[station_code] = {
                        'DateTime': date_time,
                        'Rainfall': parts[rainfall_index]
                    }
        return last_entries
    except requests.RequestException as e:
        print(f"Error retrieving data: {str(e)}")
        return {}


def update_excel_sheet(sheet, last_entries, station_column_mapping):
    for station, data in last_entries.items():
        if station in station_column_mapping:
            column_cell = station_column_mapping[station]
            sheet[column_cell] = data['Rainfall']


def main():
    station_codes = ['150111', 'STA0259', '150108', '150115', '14032795', '150113', '150114', '150109',
                     '14032793', '150106', '150107', '150112', 'STA0203', 'STA0008', 'STA0009', '150110',
                     'STA0178', '150262', '150259', '150261', '150260', 'STG1014']  # Complete your station list
    formatted_date = (datetime.now() - timedelta(days=1)).strftime('log-%d-%m-%Y.txt')
    url = f"http://202.90.198.212/logger/{formatted_date}"
    dynamic_date = datetime.now().strftime('%d%m%Y')

    rainfall_data = get_rainfall_data(url, station_codes, dynamic_date)

    workbook = load_workbook(r'S:\FILE_RWID\PyCharmProjects\python-fundamental\Weather-Data-Server-Scrapping\Template.xlsx')
    sheet = workbook.active

    # Station to column mapping for rainfall data
    station_column_mapping = {
        '150111': 'E4', 'STA0259': 'E5', '150108': 'E6', '150115': 'E7',
        '14032795': 'E8', '150113': 'E9', '150114': 'E10', '150109': 'E11',
        '14032793': 'E12', '150106': 'E13', '150107': 'E14', '150112': 'E15',
        'STA0203': 'E16', 'STA0008': 'E17', 'STA0009': 'E18', '150110': 'E19',
        'STA0178': 'E20', '150262': 'E21', '150259': 'E22', '150261': 'E23',
        '150260': 'E24', 'STG1014': 'E25'
    }
    update_excel_sheet(sheet, rainfall_data, station_column_mapping)

    # Save the updated workbook
    save_path = r'S:\FILE_RWID\PyCharmProjects\python-fundamental\Weather-Data-Server-Scrapping\Rainfall_Data.xlsx'
    workbook.save(save_path)
    # Menambahkan judul dengan tanggal
    tanggal_kemarin = (datetime.now() - timedelta(days=1)).strftime('%d-%m-%Y')
    sheet['A1'] = f"Monitoring Data Curah Hujan ARG, AWS, dan AAWS Sumatera Utara per {tanggal_kemarin}"


if __name__ == '__main__':
    main()
