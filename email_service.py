"""
Service d'envoi d'emails et scheduler automatique d'alertes
"""
import smtplib
import threading
import schedule
import time
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

logging.basicConfig(
    filename="alertes.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

_scheduler_thread = None
_scheduler_running = False
_last_check = None
_callback_ui = None  # Callback pour notifier l'UI


def build_email_html(projets, seuil):
    """
    Génère le HTML de l'email d'alerte.
    Chaque projet apparaît comme :  PROMOTEUR – INTITULÉ DU PROJET est hors délais
    """
    cards = ""
    for p in projets:
        j = p.get("jours_ecoules", "?")
        badge_color = "#FF4444" if j > 30 else "#FFB800"
        date_fmt = ""
        if p.get("date_passage"):
            try:
                date_fmt = datetime.strptime(p["date_passage"], "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                date_fmt = p["date_passage"]

        promoteur = p["promoteur"]
        intitule  = p["intitule"]

        # Ligne principale : PROMOTEUR – INTITULÉ est hors délais
        cards += f"""
        <div style='margin-bottom:16px;padding:18px 22px;background:#1E2D3D;border-radius:10px;
                    border-left:4px solid {badge_color};'>
          <p style='margin:0 0 8px;font-size:15px;font-weight:700;color:#E8F0FE;line-height:1.4'>
            {promoteur}
            <span style='color:#7A8FA6;font-weight:400'> – </span>
            {intitule}
            <span style='color:{badge_color};font-weight:700'> est hors délais</span>
          </p>
          <div style='display:flex;gap:24px;flex-wrap:wrap'>
            <span style='font-size:12px;color:#7A8FA6'>
              📅 Date de passage : <strong style='color:#B0C4DE'>{date_fmt if date_fmt else "—"}</strong>
            </span>
            <span style='font-size:12px;color:#7A8FA6'>
              ⏱️ Retard : <strong style='color:{badge_color}'>{j} jours</strong>
            </span>
          </div>
        </div>"""

    now_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style='margin:0;padding:0;background:#0A1520;font-family:Segoe UI,Arial,sans-serif'>
  <div style='max-width:820px;margin:30px auto;background:#162030;border-radius:14px;
              overflow:hidden;border:1px solid #243447'>

    <!-- En-tête -->
    <div style='background:#0F2535;padding:28px 32px;border-bottom:2px solid #00C9A7'>
      <table cellpadding="0" cellspacing="0" border="0" style="width:100%">
        <tr>
          <td style="font-size:32px;width:50px;vertical-align:middle">🌿</td>
          <td style="vertical-align:middle;padding-left:12px">
            <h1 style='margin:0;color:#00C9A7;font-size:20px;font-weight:700;letter-spacing:1px'>
              ALERTE – PROJETS HORS DÉLAIS
            </h1>
            <p style='margin:4px 0 0;color:#7A8FA6;font-size:13px'>
              Système de Suivi des Projets Environnementaux
            </p>
          </td>
        </tr>
      </table>
    </div>

    <!-- Bandeau résumé -->
    <div style='background:#2D1515;border-left:4px solid #FF4444;padding:16px 32px'>
      <p style='margin:0;color:#FF6B6B;font-size:15px;font-weight:600'>
        ⚠️ {len(projets)} projet(s) sont hors délais depuis plus de <strong>{seuil} jours</strong>
      </p>
      <p style='margin:6px 0 0;color:#7A8FA6;font-size:12px'>
        Vérification automatique effectuée le {now_str}
      </p>
    </div>

    <!-- Liste des projets hors délais -->
    <div style='padding:24px 32px'>
      <p style='margin:0 0 16px;color:#7A8FA6;font-size:13px;
                text-transform:uppercase;letter-spacing:1px;font-weight:600'>
        Projets concernés
      </p>
      {cards}
    </div>

    <!-- Pied de page -->
    <div style='padding:14px 32px 22px;border-top:1px solid #243447'>
      <p style='margin:0;color:#3D5A73;font-size:11px;text-align:center'>
        Email envoyé automatiquement • Système de Suivi des Projets • {now_str}
      </p>
    </div>
  </div>
</body>
</html>"""


def send_alert_email(projets, config):
    """Envoie un email d'alerte via SMTP."""
    if not config.get("smtp_user") or not config.get("smtp_pass"):
        raise ValueError("Configuration SMTP incomplète (email/mot de passe manquant)")

    destinataire = config.get("alert_email", "alainbolou@yahoo.fr")
    seuil = int(config.get("alert_days", 15))

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"⚠️ ALERTE – {len(projets)} projet(s) est hors délais (>{seuil} jours)"
    msg["From"] = f"Suivi Projets <{config['smtp_user']}>"
    msg["To"] = destinataire

    # Version texte
    txt_lines = [f"ALERTE – {len(projets)} projet(s) hors délais (plus de {seuil} jours)\n"]
    for p in projets:
        txt_lines.append(
            f"• {p['promoteur']} – {p['intitule']} est hors délais"
            f" | Date de passage : {p.get('date_passage','—')}"
            f" | Retard : {p.get('jours_ecoules','?')} jours"
        )
    msg.attach(MIMEText("\n".join(txt_lines), "plain", "utf-8"))

    # Version HTML
    msg.attach(MIMEText(build_email_html(projets, seuil), "html", "utf-8"))

    host = config.get("smtp_host", "smtp.gmail.com")
    port = int(config.get("smtp_port", 587))

    with smtplib.SMTP(host, port, timeout=15) as server:
        server.ehlo()
        server.starttls()
        server.login(config["smtp_user"], config["smtp_pass"])
        server.sendmail(config["smtp_user"], destinataire, msg.as_string())

    logging.info(f"Email envoyé à {destinataire} – {len(projets)} projet(s) en alerte")
    return destinataire


def run_auto_check(callback=None):
    """Vérifie les alertes et envoie si nécessaire (appelé par le scheduler)."""
    global _last_check
    _last_check = datetime.now()
    
    # Import ici pour éviter les imports circulaires
    import database as db
    
    config = db.get_config()
    seuil = int(config.get("alert_days", 15))
    projets = db.get_projets_en_alerte(seuil)
    
    msg = f"[{_last_check.strftime('%H:%M:%S')}] Vérification auto: {len(projets)} projet(s) en alerte"
    logging.info(msg)
    
    if callback:
        callback("check", msg, len(projets))
    
    if projets and config.get("smtp_user") and config.get("smtp_pass"):
        try:
            destinataire = send_alert_email(projets, config)
            ids = [p["id"] for p in projets]
            db.marquer_alerte_envoyee(ids, destinataire)
            result_msg = f"✅ Email envoyé automatiquement à {destinataire} ({len(projets)} projets)"
            logging.info(result_msg)
            if callback:
                callback("sent", result_msg, len(projets))
        except Exception as e:
            err_msg = f"❌ Erreur envoi auto: {e}"
            logging.error(err_msg)
            if callback:
                callback("error", err_msg, 0)
    elif projets and not config.get("smtp_user"):
        warn_msg = f"⚠️ {len(projets)} alertes mais SMTP non configuré"
        if callback:
            callback("warning", warn_msg, len(projets))


def start_scheduler(interval_minutes=60, callback=None):
    """Démarre le scheduler d'alertes automatiques en arrière-plan."""
    global _scheduler_thread, _scheduler_running, _callback_ui
    _callback_ui = callback
    
    if _scheduler_running:
        stop_scheduler()
    
    schedule.clear()
    schedule.every(interval_minutes).minutes.do(run_auto_check, callback=callback)
    # Vérification aussi chaque jour à 08:00
    schedule.every().day.at("08:00").do(run_auto_check, callback=callback)
    
    _scheduler_running = True

    def loop():
        # Première vérification immédiate au démarrage
        time.sleep(3)
        run_auto_check(callback=callback)
        while _scheduler_running:
            schedule.run_pending()
            time.sleep(30)

    _scheduler_thread = threading.Thread(target=loop, daemon=True, name="AlertScheduler")
    _scheduler_thread.start()
    logging.info(f"Scheduler démarré – vérification toutes les {interval_minutes} minutes + 08:00 chaque jour")
    return _scheduler_thread


def stop_scheduler():
    global _scheduler_running
    _scheduler_running = False
    schedule.clear()
    logging.info("Scheduler arrêté")


def get_last_check():
    return _last_check


def is_running():
    return _scheduler_running
