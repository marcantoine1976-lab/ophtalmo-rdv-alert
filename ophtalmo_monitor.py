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
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
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
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi d'email: {e}")
        return False

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
        chrome_options.add_argument("--disable-gpu")
        
        print("🔍 Démarrage du navigateur...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get(url)
        print("✅ Page chargée")
        
        # Attendre le chargement
        time.sleep(3)
        
        # Sélectionner "Consultation"
        print("📋 Sélection de 'Consultation'...")
        try:
            # Chercher le dropdown du motif
            selects = driver.find_elements(By.TAG_NAME, "select")
            consultation_found = False
            
            for select_element in selects:
                try:
                    select = Select(select_element)
                    options = [opt.text for opt in select.options]
                    if "Consultation" in options:
                        select.select_by_visible_text("Consultation")
                        consultation_found = True
                        print("✅ 'Consultation' sélectionné")
                        break
                except:
                    continue
            
            if not consultation_found:
                print("⚠️ 'Consultation' non trouvé")
                driver.quit()
                return
            
            time.sleep(4)
        except Exception as e:
            print(f"⚠️ Erreur lors de la sélection: {e}")
            driver.quit()
            return
        
        # Chercher les créneaux disponibles
        print("🔎 Recherche des créneaux...")
        
        # Chercher le message "Aucune disponibilité"
        try:
            no_availability = driver.find_element(By.XPATH, "//*[contains(text(), 'Aucune disponibilité')]")
            print("⏳ Aucun créneau disponible")
        except:
            # Si pas de message "Aucune disponibilité", chercher les créneaux
            try:
                slots = driver.find_elements(By.XPATH, "//button[not(@disabled)]")
                
                # Filtrer les slots (éviter les boutons de navigation)
                slot_times = []
                for slot in slots:
                    text = slot.text.strip()
                    if text and any(char.isdigit() for char in text):  # Contient une heure
                        slot_times.append(text)
                
                if slot_times:
                    print(f"✅ {len(slot_times)} créneau(x) trouvé(s) !")
                    
                    message = f"""Bonjour,

Des créneaux sont disponibles chez l'ophtalmologue ! 🎉

Créneaux trouvés:
{', '.join(slot_times)}

Va vite les réserver sur:
{url}

Bonne chance!"""
                    
                    send_email(
                        subject="🎉 Des RDV sont disponibles chez l'ophtalmologue !",
                        body=message,
                        email_from=email_from,
                        email_password=email_password,
                        email_to=email_to
                    )
                else:
                    print("⏳ Aucun créneau détecté")
            except Exception as e:
                print(f"⚠️ Erreur lors de la recherche: {e}")
        
        driver.quit()
        print("✅ Vérification terminée")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_rdv()
