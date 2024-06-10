import requests
import urllib.parse
import json
import time
import subprocess
import os
from colorama import init, Fore

# Inisialisasi colorama
init(autoreset=True)

# URL dan headers
url = "https://api.service.gameeapp.com/"
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://cf.seeddao.org',
    'priority': 'u=1, i',
    'referer': 'https://cf.seeddao.org/',
}

# Fungsi untuk membaca initData dari file
def read_initdata_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

def get_nama_from_init_data(init_data):
    parsed_data = urllib.parse.parse_qs(init_data)
    if 'user' in parsed_data:
        user_data = parsed_data['user'][0]
        user_data_json = urllib.parse.unquote(user_data)
        user_data_dict = json.loads(user_data_json)
        first_name = user_data_dict.get('first_name', '')
        last_name = user_data_dict.get('last_name', '')
        username = user_data_dict.get('username', '')
        return f"{first_name} {last_name} ({username})".strip()
    return None

# Fungsi untuk melakukan start session
def start_session():
    return requests.post('https://elb.seeddao.org/api/v1/seed/claim', {}, headers=headers)

def claim_harian():
    return requests.post('https://elb.seeddao.org/api/v1/login-bonuses', {}, headers=headers)

def upgrade_speed():
    return requests.post('https://elb.seeddao.org/api/v1/seed/mining-speed/upgrade', {}, headers=headers)

# Fungsi untuk mengambil data ID task dan klaim task
def claim_task():
    task_progress_url = 'https://elb.seeddao.org/api/v1/tasks/progresses'
    response = requests.get(task_progress_url, headers=headers)
    if response.status_code == 200:
        tasks = response.json().get('data', [])
        claimed_tasks = []
        for task in tasks:
            task_id = task.get('id')
            if task_id:
                claim_url = f'https://elb.seeddao.org/api/v1/tasks/{task_id}'
                claim_response = requests.post(claim_url, {}, headers=headers)
                if claim_response.status_code == 200:
                    claimed_tasks.append(task)
                    print(Fore.GREEN + f"Tugas {task.get('name')} dengan ID {task_id} telah berhasil di-klaim")
                elif claim_response.status_code == 429:
                    print(Fore.RED + f"Rate limiting: Tunggu beberapa saat sebelum mencoba lagi.")
                    time.sleep(5)  # Tunggu 5 detik sebelum mencoba lagi
                else:
                    print(Fore.RED + f"Gagal meng-klaim tugas {task.get('name')} dengan ID {task_id}: {claim_response.status_code}, {claim_response.text}")
        return claimed_tasks
    else:
        print(Fore.RED + f"Gagal mengambil data tugas: {response.status_code}, {response.text}")
        return []

def claim_box():
    return requests.post('https://elb.seeddao.org/api/v1/beta-gratitude-mystery-box/my-box', {}, headers=headers)

# Fungsi untuk menjalankan operasi untuk setiap initData
def process_initdata(init_data):
    nama = get_nama_from_init_data(init_data)
    print(Fore.YELLOW + nama)
    headers['telegram-data'] = init_data
    
    try:
        start_response = start_session()
        if start_response.status_code == 200:
            print(Fore.BLUE + "Claim Hasil Mining Selesai")
        else:
            print(Fore.RED + 'Belum Waktunya Claim')
    except requests.exceptions.JSONDecodeError:
        print(Fore.RED + "Gagal mendecode respons JSON untuk sesi mulai")

    try:
        daily_response = claim_harian()
        if daily_response.status_code == 200:
            print(Fore.BLUE + "Berhasil Ambil Seed Harian")
        else:
            print(Fore.RED + 'Sudah Ambil Harian')
    except requests.exceptions.JSONDecodeError:
        print(Fore.RED + "Gagal mendecode respons JSON untuk klaim harian")

    try:
        upgrade_response = upgrade_speed()
        if upgrade_response.status_code == 200:
            print(Fore.BLUE + "Upgrade Kecepatan Penambangan telah berhasil")
        else:
            print(Fore.RED + 'Belum Waktunya Upgrade')
    except requests.exceptions.JSONDecodeError:
        print(Fore.RED + "Gagal mendecode respons JSON untuk upgrade")

    try:
        claimed_tasks = claim_task()
        if not claimed_tasks:
            print(Fore.BLUE + "Semua Tugas telah selesai")
        else:
            for task in claimed_tasks:
                # Contoh penggunaan data dari tugas yang telah diklaim
                task_id = task.get('id')
                task_name = task.get('name')
                print(Fore.GREEN + f"Tugas {task_name} dengan ID {task_id} telah selesai")
    except requests.exceptions.JSONDecodeError:
        print(Fore.RED + "Gagal mendecode respons JSON untuk klaim tugas")

    try:
        claim_box_response = claim_box()
        if claim_box_response.status_code == 200:
            print(Fore.BLUE + "BOX Berhasil di Klaim")
        else:
            print(Fore.RED + 'BOX Sudah di Klaim')
    except requests.exceptions.JSONDecodeError:
        print(Fore.RED + "Gagal mendecode respons JSON untuk klaim kotak")

# Program Utama
def main():
    initdata_file = "initdata.txt"
    
    while True:
        initdata_list = read_initdata_from_file(initdata_file)
        
        for init_data in initdata_list:
            process_initdata(init_data.strip())
            print("\n")
        
        # Delay sebelum membaca ulang file initData
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(Fore.RED + f"Terjadi kesalahan: {e}")
        # Dapatkan versi Python yang digunakan
        python_executable = os.path.basename(os.sys.executable)
        subprocess.run([python_executable, "gamee.py"])
