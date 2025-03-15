import os
import subprocess
import logging

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
    """Menginstal semua dependensi yang dibutuhkan untuk VPN."""
    print_log("📦 Menginstal dependensi VPN...")
    dependencies = [
        "sudo apt update && sudo apt upgrade -y",
        "sudo apt install -y pptp-linux",
        "sudo apt install -y ufw"
    ]
    for dep in dependencies:
        run_command(dep)
    print_log("✅ Semua dependensi VPN telah terinstal.")

def configure_vpn(vpn_gateway, vpn_user, vpn_pass, log_path):
    """Mengonfigurasi VPN PPTP dan mengatur koneksi otomatis saat boot."""
    print_log("🔧 Mengonfigurasi VPN...")

    vpn_config_filename = "vpn"  # Nama file konfigurasi di folder kerja
    vpn_config_path = os.path.join(os.getcwd(), vpn_config_filename)  # Simpan di folder kerja

    vpn_config_content = f'''
pty "pptp {vpn_gateway} --nolaunchpppd --debug"
name {vpn_user}
password {vpn_pass}
persist
noauth
maxfail 0
require-mppe
'''

    # Buat file konfigurasi di folder kerja
    try:
        with open(vpn_config_path, "w") as vpn_file:
            vpn_file.write(vpn_config_content)
        print_log(f"✅ Konfigurasi VPN berhasil dibuat di {vpn_config_path}")
    except Exception as e:
        print_log(f"❌ Gagal membuat file konfigurasi VPN: {e}", "error")
        return

    # Pindahkan file ke /etc/ppp/peers/
    destination_path = "/etc/ppp/peers/vpn"
    run_command(f"sudo mv {vpn_config_path} {destination_path}")
    run_command(f"sudo chmod 600 {destination_path}")  # Amankan file

    # Konfigurasi firewall
    print_log("🔐 Mengonfigurasi UFW...")
    run_command("sudo ufw enable")

    # Konfigurasi crontab agar VPN tersambung otomatis saat boot
    print_log("🕒 Menambahkan konfigurasi crontab untuk VPN...")
    cron_command = f'@reboot sudo pon vpn updetach >> {log_path}/logvpn.txt 2>&1'
    run_command(f'(crontab -l 2>/dev/null; echo "{cron_command}") | crontab -')

    print_log("✅ Konfigurasi VPN selesai. VPN akan terhubung secara otomatis saat boot.")

def ensure_directory_exists(directory):
    """Membuat folder jika belum ada."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print_log(f"📁 Membuat folder: {directory}")
    else:
        print_log(f"✅ Folder sudah ada: {directory}")

if __name__ == "__main__":
    print("\n🔧 **Setup VPN PPTP**\n")

    # Input dari pengguna
    vpn_gateway = input("Masukkan IP Gateway VPN: ")
    vpn_user = input("Masukkan Username VPN: ")
    vpn_pass = input("Masukkan Password VPN: ")
    log_path = input("Masukkan path untuk log VPN: ")

    ensure_directory_exists(log_path)

    # Jalankan setup VPN
    install_vpn_dependencies()
    configure_vpn(vpn_gateway, vpn_user, vpn_pass, log_path)

    print("\n🎉 **Setup selesai! VPN telah dikonfigurasi dan akan tersambung otomatis saat boot.** 🎉")