"""
ANDE – Agence Nationale De l'Environnement
Service Promoteur et Relations Extérieures
Application ERP Web – Flask
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import database as db
import email_service as es
import threading, os, json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ande-erp-secret-2024")

# Initialisation DB
db.init_db()
json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projets.json")
if os.path.exists(json_path):
    db.import_from_json(json_path)

# Démarrage scheduler automatique
def scheduler_callback(event_type, message, count):
    pass  # logs gérés par email_service

es.start_scheduler(interval_minutes=60, callback=scheduler_callback)


# ══════════════════════════════════════════════════════════════════════════════
# Routes principales
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    stats = db.get_stats()
    alertes = db.get_projets_en_alerte(int(db.get_config().get("alert_days", 15)))
    return render_template("index.html", stats=stats, alertes=alertes[:5])


@app.route("/projets")
def projets():
    search = request.args.get("search", "")
    filtre = request.args.get("filtre", "tous")
    liste  = db.get_all_projets(search=search, filtre=filtre)
    stats  = db.get_stats()
    # Calcul jours pour chaque projet
    today = datetime.today().date()
    for p in liste:
        if p.get("date_passage"):
            try:
                d = datetime.strptime(p["date_passage"], "%Y-%m-%d").date()
                p["jours"] = (today - d).days
                if p["jours"] > 15:
                    p["statut"] = "alerte"
                elif p["jours"] >= 10:
                    p["statut"] = "warning"
                else:
                    p["statut"] = "ok"
            except:
                p["jours"] = None
                p["statut"] = "nodate"
        else:
            p["jours"] = None
            p["statut"] = "nodate"
    return render_template("projets.html", projets=liste, stats=stats,
                           search=search, filtre=filtre)


@app.route("/projet/nouveau", methods=["GET", "POST"])
def nouveau_projet():
    if request.method == "POST":
        promoteur    = request.form.get("promoteur", "").strip()
        intitule     = request.form.get("intitule", "").strip()
        date_passage = request.form.get("date_passage", "").strip()
        notes        = request.form.get("notes", "").strip()
        if not promoteur or not intitule:
            flash("PROMOTEUR et INTITULÉ sont obligatoires.", "error")
            return render_template("form_projet.html", projet=None,
                                   data=request.form)
        if date_passage:
            try:
                datetime.strptime(date_passage, "%Y-%m-%d")
            except:
                flash("Format de date invalide. Utilisez AAAA-MM-JJ.", "error")
                return render_template("form_projet.html", projet=None,
                                       data=request.form)
        db.add_projet(promoteur, intitule, date_passage or None, notes)
        flash(f"Projet '{promoteur}' ajouté avec succès !", "success")
        return redirect(url_for("projets"))
    return render_template("form_projet.html", projet=None, data={})


@app.route("/projet/<int:pid>/modifier", methods=["GET", "POST"])
def modifier_projet(pid):
    projet = db.get_projet(pid)
    if not projet:
        flash("Projet introuvable.", "error")
        return redirect(url_for("projets"))
    if request.method == "POST":
        promoteur    = request.form.get("promoteur", "").strip()
        intitule     = request.form.get("intitule", "").strip()
        date_passage = request.form.get("date_passage", "").strip()
        notes        = request.form.get("notes", "").strip()
        if not promoteur or not intitule:
            flash("PROMOTEUR et INTITULÉ sont obligatoires.", "error")
            return render_template("form_projet.html", projet=projet,
                                   data=request.form)
        if date_passage:
            try:
                datetime.strptime(date_passage, "%Y-%m-%d")
            except:
                flash("Format de date invalide. Utilisez AAAA-MM-JJ.", "error")
                return render_template("form_projet.html", projet=projet,
                                       data=request.form)
        db.update_projet(pid, promoteur, intitule, date_passage or None, notes)
        flash(f"Projet modifié avec succès !", "success")
        return redirect(url_for("projets"))
    return render_template("form_projet.html", projet=projet, data=projet)


@app.route("/projet/<int:pid>/supprimer", methods=["POST"])
def supprimer_projet(pid):
    p = db.get_projet(pid)
    if p:
        db.delete_projet(pid)
        flash(f"Projet supprimé.", "success")
    return redirect(url_for("projets"))


@app.route("/alertes")
def alertes():
    cfg   = db.get_config()
    seuil = int(cfg.get("alert_days", 15))
    today = datetime.today().date()
    liste = db.get_projets_en_alerte(seuil)
    for p in liste:
        if p.get("date_passage"):
            try:
                d = datetime.strptime(p["date_passage"], "%Y-%m-%d").date()
                p["jours"] = (today - d).days
            except:
                p["jours"] = None
    return render_template("alertes.html", alertes=liste, seuil=seuil)


@app.route("/alertes/envoyer", methods=["POST"])
def envoyer_alertes():
    cfg   = db.get_config()
    seuil = int(cfg.get("alert_days", 15))
    liste = db.get_projets_en_alerte(seuil)
    if not liste:
        flash("✅ Aucun projet en alerte.", "success")
        return redirect(url_for("alertes"))
    if not cfg.get("smtp_user") or not cfg.get("smtp_pass"):
        flash("⚙️ Configurez d'abord le SMTP dans la page Configuration.", "error")
        return redirect(url_for("configuration"))
    try:
        dest = es.send_alert_email(liste, cfg)
        ids  = [p["id"] for p in liste]
        db.marquer_alerte_envoyee(ids, dest)
        flash(f"✅ Email envoyé à {dest} ({len(liste)} projet(s) en alerte).", "success")
    except Exception as e:
        flash(f"❌ Erreur envoi email : {e}", "error")
    return redirect(url_for("alertes"))


@app.route("/historique")
def historique():
    hist  = db.get_historique(200)
    stats = db.get_stats()
    return render_template("historique.html", historique=hist, stats=stats)


@app.route("/importer", methods=["GET", "POST"])
def importer():
    if request.method == "POST":
        if "fichier" not in request.files:
            flash("Aucun fichier sélectionné.", "error")
            return redirect(url_for("importer"))
        f = request.files["fichier"]
        if f.filename == "":
            flash("Aucun fichier sélectionné.", "error")
            return redirect(url_for("importer"))

        col_promoteur    = request.form.get("col_promoteur", "")
        col_intitule     = request.form.get("col_intitule", "")
        col_date_passage = request.form.get("col_date_passage", "")
        mode             = request.form.get("mode", "ajouter")

        import pandas as pd, tempfile
        suffix = ".xlsx" if f.filename.endswith((".xlsx",".xls")) else ".csv"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        f.save(tmp.name)

        try:
            if suffix == ".csv":
                df = pd.read_csv(tmp.name, encoding="utf-8", errors="replace")
            else:
                df = pd.read_excel(tmp.name)

            if mode == "remplacer":
                with db.get_connection() as conn:
                    conn.execute("DELETE FROM projets")
                    conn.commit()

            inseres = ignores = 0
            for _, row in df.iterrows():
                promoteur = str(row.get(col_promoteur,"")).strip()
                intitule  = str(row.get(col_intitule, "")).strip()
                if not promoteur or not intitule or promoteur=="nan" or intitule=="nan":
                    ignores += 1
                    continue
                date_str = None
                if col_date_passage and col_date_passage in df.columns:
                    raw = row.get(col_date_passage)
                    if pd.notna(raw):
                        try:
                            date_str = pd.to_datetime(raw).strftime("%Y-%m-%d")
                        except:
                            pass
                db.add_projet(promoteur, intitule, date_str)
                inseres += 1

            flash(f"✅ Importation réussie : {inseres} projet(s) ajouté(s), {ignores} ligne(s) ignorée(s).", "success")
        except Exception as e:
            flash(f"❌ Erreur : {e}", "error")
        finally:
            os.unlink(tmp.name)
        return redirect(url_for("projets"))

    return render_template("importer.html")


@app.route("/importer/preview", methods=["POST"])
def preview_fichier():
    """Retourne les colonnes du fichier uploadé en JSON."""
    if "fichier" not in request.files:
        return jsonify({"colonnes": [], "apercu": []})
    f = request.files["fichier"]
    import pandas as pd, tempfile
    suffix = ".xlsx" if f.filename.endswith((".xlsx",".xls")) else ".csv"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    f.save(tmp.name)
    try:
        if suffix == ".csv":
            df = pd.read_csv(tmp.name, nrows=5, encoding="utf-8", errors="replace")
        else:
            df = pd.read_excel(tmp.name, nrows=5)
        cols   = list(df.columns.astype(str))
        apercu = df.fillna("").astype(str).values.tolist()
        return jsonify({"colonnes": cols, "apercu": apercu, "headers": cols})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        os.unlink(tmp.name)


@app.route("/configuration", methods=["GET", "POST"])
def configuration():
    if request.method == "POST":
        champs = ["smtp_host","smtp_port","smtp_user","smtp_pass",
                  "alert_email","alert_days","auto_check_interval"]
        for c in champs:
            val = request.form.get(c,"").strip()
            if val:
                db.set_config(c, val)
        flash("✅ Configuration sauvegardée.", "success")
        # Redémarrer scheduler
        cfg = db.get_config()
        es.start_scheduler(int(cfg.get("auto_check_interval",60)),
                           callback=scheduler_callback)
        return redirect(url_for("configuration"))
    cfg = db.get_config()
    return render_template("configuration.html", cfg=cfg)


@app.route("/configuration/tester", methods=["POST"])
def tester_email():
    cfg = db.get_config()
    try:
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText("✅ Test de connexion SMTP réussi – ANDE ERP", "plain", "utf-8")
        msg["Subject"] = "✅ Test SMTP – ANDE Service Promoteur"
        msg["From"]    = cfg["smtp_user"]
        msg["To"]      = cfg["alert_email"]
        with smtplib.SMTP(cfg["smtp_host"], int(cfg["smtp_port"]), timeout=15) as s:
            s.ehlo(); s.starttls()
            s.login(cfg["smtp_user"], cfg["smtp_pass"])
            s.sendmail(cfg["smtp_user"], cfg["alert_email"], msg.as_string())
        flash(f"✅ Email de test envoyé à {cfg['alert_email']} !", "success")
    except Exception as e:
        flash(f"❌ Erreur SMTP : {e}", "error")
    return redirect(url_for("configuration"))


# ── API JSON ─────────────────────────────────────────────────────────────────
@app.route("/api/stats")
def api_stats():
    return jsonify(db.get_stats())

@app.route("/api/alertes")
def api_alertes():
    cfg   = db.get_config()
    seuil = int(cfg.get("alert_days", 15))
    return jsonify(db.get_projets_en_alerte(seuil))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
