import subprocess
import time
import schedule

def run_monitor():
    print("\n🔔 Lancement du monitoring...")
    subprocess.run(['python', 'ophtalmo_monitor.py'])

schedule.every().hour.do(run_monitor)

print("✅ Monitoring lancé - s'exécutera toutes les heures")

try:
    while True:
        schedule.run_pending()
        time.sleep(60)
except KeyboardInterrupt:
    print("\n❌ Monitoring arrêté")
