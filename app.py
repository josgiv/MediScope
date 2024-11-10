# app.py
import subprocess
import os
import time

def run_api():
    try:
        script_path = os.path.join(os.getcwd(), 'API', 'quick_checkup_API.py')
        
        if not os.path.exists(script_path):
            print(f"File {script_path} tidak ditemukan.")
            return
        
        print(f"Menjalankan API: {script_path}")
        process = subprocess.Popen(
            ['python', script_path],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
        )

        time.sleep(2) 
        print("Running Flask on the Background.")
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print("Error executing API:")
            print(stderr.decode())
        else:
            print("Output API:")
            print(stdout.decode())

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    run_api()
