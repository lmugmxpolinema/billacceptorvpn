import os
import subprocess
import logging
import re

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def print_log(message, level="info"):
    """Mencetak pesan ke terminal dan mencatat log."""
    if level == "info":
        print(f"✅ {message}")
        logging.info(message)
    elif level == "warning":
        print(f"⚠️ {message}")
        logging.warning(message)
    elif level == "error":
        print(f"❌ {message}")
        logging.error(message)

def run_command(command):
    """Menjalankan perintah shell dengan subprocess dan menangani error."""
    try:
        subprocess.run(command, check=True, shell=True)
        print_log(f"Berhasil menjalankan: {command}")
    except subprocess.CalledProcessError as e:
        print_log(f"Gagal menjalankan: {command}\nError: {e}", "error")

def install_vpn_dependencies():
    """Menginstal dependensi VPN."""
    print_log("📦 Menginstal dependensi VPN...")
    dependencies = [
        "sudo apt update && sudo apt upgrade -y",
        "sudo apt install -y pptp-linux",
        "sudo apt install -y ufw"
    ]
    for dep in dependencies:
        run_command(dep)
    print_log("✅ Semua dependensi VPN telah diinstal.")
def create_vpn_reconnect_script(script_path="/usr/local/bin/vpn_reconnect.sh"):
    """Membuat skrip bash untuk cek koneksi VPN dan reconnect otomatis."""
    script_content = """#!/bin/bash

if pgrep -f "pppd.*vpn" > /dev/null
then
    echo "$(date): VPN sudah aktif."
else
    echo "$(date): VPN tidak aktif, mencoba reconnect..."
    sudo pon vpn updetach
fi
"""
    try:
        with open("vpn_reconnect.sh", "w") as f:
            f.write(script_content)
        run_command(f"sudo mv vpn_reconnect.sh {script_path}")
        run_command(f"sudo chmod +x {script_path}")
        print_log(f"✅ Skrip reconnect VPN dibuat di {script_path}")
    except Exception as e:
        print_log(f"❌ Gagal membuat skrip reconnect VPN: {e}", "error")

def replace_line_in_file(filename, pattern, replacement):
    """Mengganti baris dalam file berdasarkan pola regex."""
    try:
        with open(filename, "r") as file:
            lines = file.readlines()
        
        with open(filename, "w") as file:
            for line in lines:
                file.write(re.sub(pattern, replacement, line))
        print_log(f"✅ Berhasil memperbarui konfigurasi di {filename}")
    except Exception as e:
        print_log(f"❌ Gagal mengedit file {filename}: {e}", "error")

def configure_rc_local():
    """Mengonfigurasi /etc/rc.local agar VPN otomatis terhubung saat boot."""
    rc_local_path = "/etc/rc.local"
    print_log("📝 Menghapus isi rc.local dan menambahkan konfigurasi baru...")
    
    with open(rc_local_path, "w") as rc_local:
        rc_local.write("#!/bin/bash\n")
        rc_local.write("vpn=\"on\"\n")  # Mengganti dengan vpn="0"
        rc_local.write("exit 0\n")
    
    run_command(f"sudo chmod +x {rc_local_path}")
    print_log("✅ rc.local telah diperbarui.")

def configure_vpn(vpn_gateway, vpn_user, vpn_pass, log_path):
    """Mengonfigurasi VPN PPTP."""
    print_log("🔧 Mengonfigurasi VPN...")
    vpn_config_file = "vpn"
    
    vpn_config_content = """pty "pptp 0.0.0.0 --nolaunchpppd --debug"
name user
password pass
remotename PPTP
require-mppe-128
require-mschap-v2
refuse-eap
refuse-pap
refuse-chap
refuse-mschap
noauth
debug
persist
maxfail 0
holdoff 10
defaultroute
replacedefaultroute
usepeerdns
"""
    if not os.path.exists(vpn_config_file):
        with open(vpn_config_file, "w") as vpn_file:
            vpn_file.write(vpn_config_content)
        print_log("✅ File konfigurasi VPN awal telah dibuat.")
    
    replace_line_in_file(vpn_config_file, r'pty "pptp .*', f'pty "pptp {vpn_gateway} --nolaunchpppd --debug"')
    replace_line_in_file(vpn_config_file, r'^name .*', f'name {vpn_user}')
    replace_line_in_file(vpn_config_file, r'password .*', f'password {vpn_pass}')
    
    run_command(f"sudo mv {vpn_config_file} /etc/ppp/peers/vpn")
    run_command("sudo chmod 600 /etc/ppp/peers/vpn")
    print_log("✅ File konfigurasi VPN telah dipindahkan dan diberikan izin aman.")
    
    print_log("🔐 Mengonfigurasi UFW...")
    run_command("sudo ufw allow 22")
    run_command("sudo ufw allow from 0.0.0.0/0")
    run_command("sudo ufw reload")
    
    print_log("🕒 Menambahkan konfigurasi crontab untuk VPN...")
    cron_command = f'@reboot sudo pon vpn updetach >> {log_path}/logvpn.txt 2>&1'
    run_command(f'(crontab -l 2>/dev/null; echo "{cron_command}") | crontab -')

    print_log("🕒 Menambahkan konfigurasi crontab untuk VPN reconnect tiap 5 menit...")
    reconnect_command = f'*/5 * * * * /usr/local/bin/vpn_reconnect.sh >> {log_path}/vpn_reconnect.log 2>&1'
    run_command(f'(crontab -l 2>/dev/null; echo "{reconnect_command}") | crontab -')

    configure_rc_local()
    print_log("✅ Konfigurasi VPN selesai. VPN akan terhubung otomatis saat boot.")

def ensure_directory_exists(directory):
    """Membuat folder jika belum ada."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print_log(f"📁 Membuat folder: {directory}")
    else:
        print_log(f"✅ Folder sudah ada: {directory}")

if __name__ == "__main__":
    print("\n🔧 **Setup VPN PPTP**\n")
    vpn_gateway = input("Masukkan IP Gateway VPN: ")
    vpn_user = input("Masukkan Username VPN: ")
    vpn_pass = input("Masukkan Password VPN: ")
    log_path = input("Masukkan path untuk log VPN: ")
    
    ensure_directory_exists(log_path)
    install_vpn_dependencies()
    create_vpn_reconnect_script()
    configure_vpn(vpn_gateway, vpn_user, vpn_pass, log_path)
    
    print("\n🎉 **Setup selesai! VPN telah dikonfigurasi dan akan tersambung otomatis saat boot.** 🎉")
