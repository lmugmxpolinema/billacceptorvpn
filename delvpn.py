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

def remove_vpn_configuration():
    """Menghapus file konfigurasi VPN dan crontab."""
    print_log("🗑️ Menghapus file konfigurasi VPN...")
    vpn_config_path = "/etc/ppp/peers/vpn"
    
    if os.path.exists(vpn_config_path):
        run_command(f"sudo rm -f {vpn_config_path}")
        print_log(f"✅ File {vpn_config_path} telah dihapus.")
    else:
        print_log(f"⚠️ File {vpn_config_path} tidak ditemukan, mungkin sudah dihapus.")

def remove_crontab_entry():
    """Menghapus entri crontab yang menghubungkan VPN saat boot."""
    print_log("🕒 Menghapus konfigurasi crontab VPN...")
    cron_command = "@reboot sudo pon vpn updetach"
    run_command(f'(crontab -l | grep -v "{cron_command}" | crontab -)')
    print_log("✅ Konfigurasi crontab VPN telah dihapus.")

def uninstall_vpn_dependencies():
    """Menghapus paket VPN yang telah diinstal."""
    print_log("📦 Menghapus paket VPN...")
    packages = ["pptp-linux", "ufw"]
    
    for package in packages:
        run_command(f"sudo apt remove --purge -y {package}")
    
    run_command("sudo apt autoremove -y")
    print_log("✅ Semua paket VPN telah dihapus.")

def disable_firewall():
    """Menonaktifkan firewall (opsional)."""
    print_log("🔐 Menonaktifkan firewall (jika diaktifkan)...")
    run_command("sudo ufw disable")
    print_log("✅ Firewall telah dinonaktifkan.")

if __name__ == "__main__":
    print("\n🗑️ **Uninstall VPN Setup**\n")

    remove_vpn_configuration()
    remove_crontab_entry()
    disable_firewall()
    uninstall_vpn_dependencies()

    print("\n🎉 **Pembersihan selesai! Semua konfigurasi VPN telah dihapus.** 🎉")
