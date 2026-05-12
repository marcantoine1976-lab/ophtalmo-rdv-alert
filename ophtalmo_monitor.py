import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

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
        print("🔍 Accès à la page...")
        
        # Headers pour sembler comme un navigateur
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print("✅ Page récupérée")
        
        # Parser la page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Chercher le message "Aucune disponibilité"
        aucune_dispo = soup.find(string=lambda text: text and "Aucune disponibilité" in text)
        
        if aucune_dispo:
            print("⏳ Aucun créneau disponible pour le moment")
        else:
            # Chercher les créneaux (boutons)
            buttons = soup.find_all('button')
            
            slot_times = []
            for button in buttons:
                text = button.get_text(strip=True)
                # Chercher les heures (format XX:XX)
                if ':' in text and any(char.isdigit() for char in text):
                    if text not in slot_times:  # Éviter les doublons
                        slot_times.append(text)
            
            if slot_times and len(slot_times) > 0:
                print(f"✅ {len(slot_times)} créneau(x) trouvé(s) !")
                print(f"Créneaux: {slot_times}")
                
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
        
        print("✅ Vérification terminée")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout - le serveur met trop de temps à répondre")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau: {e}")
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_rdv()
