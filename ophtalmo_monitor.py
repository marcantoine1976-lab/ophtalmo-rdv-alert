import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
import time

def send_email(subject, body, email_from, email_password, email_to):
    """Envoie un email via Gmail"""
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(email_from, email_password)
        
        message = MIMEMultipart()
        message['From'] = email_from
        message['To'] = email_to
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        
        server.send_message(message)
        server.quit()
        print(f"✅ Email envoyé à {email_to}")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi d'email: {e}")

def check_rdv():
    """Vérifie la disponibilité des RDV"""
    email_from = os.getenv('EMAIL_FROM')
    email_password = os.getenv('EMAIL_PASSWORD')
    email_to = os.getenv('EMAIL_TO')
    
    url = "https://www.allosante.nc/ophtalmologie/noumea/bougamha-walid"
    
    try:
        # Configuration de Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        print("🔍 Démarrage du navigateur...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Attendre le chargement
        time.sleep(3)
        
        # Sélectionner "Consultation"
        print("📋 Sélection de 'Consultation'...")
        try:
            consultation_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//select[contains(@class, 'motif')]"))
            )
            select = Select(consultation_dropdown)
            select.select_by_visible_text("Consultation")
            
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Erreur lors de la sélection: {e}")
            driver.quit()
            return
        
        # Chercher les créneaux disponibles
        print("🔎 Recherche des créneaux...")
        
        try:
            # Chercher les cases disponibles (pas désactivées)
            slots = driver.find_elements(By.XPATH, "//button[contains(@class, 'slot') and not(@disabled)]")
            
            if len(slots) > 0:
                print(f"✅ {len(slots)} créneau(x) trouvé(s) !")
                
                # Extraire les horaires
                horaires = []
                for slot in slots:
                    horaires.append(slot.text)
                
                message = f"""
Bonjour,

Des créneaux sont disponibles chez l'ophtalmologue ! 🎉

Créneaux trouvés:
{', '.join(horaires)}

Va vite les réserver sur:
{url}

Bonne chance!
                """
                
                send_email(
                    subject="🎉 Des RDV sont disponibles chez l'ophtalmologue !",
                    body=message,
                    email_from=email_from,
                    email_password=email_password,
                    email_to=email_to
                )
            else:
                # Vérifier le message "Aucune disponibilité"
                try:
                    no_availability = driver.find_element(By.XPATH, "//*[contains(text(), 'Aucune disponibilité')]")
                    print("⏳ Aucun créneau disponible pour le moment")
                except:
                    print("⚠️ Impossible de déterminer la disponibilité")
        
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
        
        driver.quit()
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    check_rdv()
