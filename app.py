from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import database as db
import email_service as es
import os, json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ande-erp-secret-2024")

db.init_db()
json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projets.json")
if os.path.exists(json_path):
    db.import_from_json(json_path)

def scheduler_callback(event_type, message, count): pass
es.start_scheduler(interval_minutes=60, callback=scheduler_callback)

@app.route("/")
def index():
    stats = db.get_stats()
    alertes = db.get_projets_en_alerte(int(db.get_config().get("alert_days",15)))
    today = datetime.today().date()
    for p in alertes:
        if p.get("date_passage"):
            try:
                d = datetime.strptime(p["date_passage"], "%Y-%m-%d").date()
                p["jours_ecoules"] = (today - d).days
            except: p["jours_ecoules"] = None
    return render_template("index.html", stats=stats, alertes=alertes[:5])

@app.route("/projets")
def projets():
    search = request.args.get("search","")
    filtre = request.args.get("filtre","tous")
    type_projet = request.args.get("type_projet","")
    liste = db.get_all_projets(search=search, filtre=filtre, type_projet=type_projet)
    stats = db.get_stats()
    today = datetime.today().date()
    for p in liste:
        if p.get("date_passage"):
            try:
                d = datetime.strptime(p["date_passage"],"%Y-%m-%d").date()
                p["jours"] = (today - d).days
                p["statut"] = "alerte" if p["jours"]>15 else "warning" if p["jours"]>=10 else "ok"
            except: p["jours"]=None; p["statut"]="nodate"
        else: p["jours"]=None; p["statut"]="nodate"
    return render_template("projets.html", projets=liste, stats=stats,
                           search=search, filtre=filtre, type_projet=type_projet)

@app.route("/projet/nouveau", methods=["GET","POST"])
def nouveau_projet():
    if request.method=="POST":
        promoteur = request.form.get("promoteur","").strip()
        intitule  = request.form.get("intitule","").strip()
        contact   = request.form.get("contact_promoteur","").strip()
        type_p    = request.form.get("type_projet","").strip()
        date_p    = request.form.get("date_passage","").strip()
        cout      = request.form.get("cout_projet","").strip()
        statut_c  = request.form.get("statut_cout","").strip()
        obs       = request.form.get("observations","").strip()
        if not promoteur or not intitule:
            flash("PROMOTEUR et INTITULÉ sont obligatoires.","error")
            return render_template("form_projet.html", projet=None, data=request.form)
        if date_p:
            try: datetime.strptime(date_p,"%Y-%m-%d")
            except: flash("Format de date invalide. Utilisez AAAA-MM-JJ.","error"); return render_template("form_projet.html",projet=None,data=request.form)
        db.add_projet(promoteur,intitule,contact,type_p,date_p or None,cout,statut_c,obs)
        flash(f"Projet '{promoteur}' ajouté avec succès !","success")
        return redirect(url_for("projets"))
    return render_template("form_projet.html", projet=None, data={})

@app.route("/projet/<int:pid>/modifier", methods=["GET","POST"])
def modifier_projet(pid):
    projet = db.get_projet(pid)
    if not projet: flash("Projet introuvable.","error"); return redirect(url_for("projets"))
    if request.method=="POST":
        promoteur = request.form.get("promoteur","").strip()
        intitule  = request.form.get("intitule","").strip()
        contact   = request.form.get("contact_promoteur","").strip()
        type_p    = request.form.get("type_projet","").strip()
        date_p    = request.form.get("date_passage","").strip()
        cout      = request.form.get("cout_projet","").strip()
        statut_c  = request.form.get("statut_cout","").strip()
        obs       = request.form.get("observations","").strip()
        if not promoteur or not intitule:
            flash("PROMOTEUR et INTITULÉ sont obligatoires.","error")
            return render_template("form_projet.html",projet=projet,data=request.form)
        if date_p:
            try: datetime.strptime(date_p,"%Y-%m-%d")
            except: flash("Format de date invalide.","error"); return render_template("form_projet.html",projet=projet,data=request.form)
        db.update_projet(pid,promoteur,intitule,contact,type_p,date_p or None,cout,statut_c,obs)
        flash("Projet modifié avec succès !","success")
        return redirect(url_for("projets"))
    return render_template("form_projet.html", projet=projet, data=projet)

@app.route("/projet/<int:pid>/supprimer", methods=["POST"])
def supprimer_projet(pid):
    db.delete_projet(pid)
    flash("Projet supprimé.","success")
    return redirect(url_for("projets"))

@app.route("/alertes")
def alertes():
    cfg = db.get_config()
    seuil = int(cfg.get("alert_days",15))
    today = datetime.today().date()
    liste = db.get_projets_en_alerte(seuil)
    for p in liste:
        if p.get("date_passage"):
            try:
                d = datetime.strptime(p["date_passage"],"%Y-%m-%d").date()
                p["jours"] = (today - d).days
            except: p["jours"]=None
    return render_template("alertes.html", alertes=liste, seuil=seuil)

@app.route("/alertes/envoyer", methods=["POST"])
def envoyer_alertes():
    cfg = db.get_config()
    seuil = int(cfg.get("alert_days",15))
    liste = db.get_projets_en_alerte(seuil)
    if not liste: flash("✅ Aucun projet en alerte.","success"); return redirect(url_for("alertes"))
    if not cfg.get("smtp_user") or not cfg.get("smtp_pass"):
        flash("⚙️ Configurez d'abord le SMTP.","error"); return redirect(url_for("configuration"))
    try:
        dest = es.send_alert_email(liste, cfg)
        db.marquer_alerte_envoyee([p["id"] for p in liste], dest)
        flash(f"✅ Email envoyé à {dest} ({len(liste)} projet(s)).","success")
    except Exception as e:
        flash(f"❌ Erreur : {e}","error")
    return redirect(url_for("alertes"))

@app.route("/historique")
def historique():
    return render_template("historique.html", historique=db.get_historique(200), stats=db.get_stats())

@app.route("/importer", methods=["GET","POST"])
def importer():
    if request.method=="POST":
        if "fichier" not in request.files: flash("Aucun fichier.","error"); return redirect(url_for("importer"))
        f = request.files["fichier"]
        col_promoteur    = request.form.get("col_promoteur","")
        col_intitule     = request.form.get("col_intitule","")
        col_contact      = request.form.get("col_contact","")
        col_type         = request.form.get("col_type","")
        col_date         = request.form.get("col_date_passage","")
        col_cout         = request.form.get("col_cout","")
        col_statut_cout  = request.form.get("col_statut_cout","")
        col_obs          = request.form.get("col_observations","")
        mode             = request.form.get("mode","ajouter")
        import pandas as pd, tempfile
        suffix = ".xlsx" if f.filename.endswith((".xlsx",".xls")) else ".csv"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        f.save(tmp.name)
        try:
            df = pd.read_csv(tmp.name, encoding="utf-8", errors="replace") if suffix==".csv" else pd.read_excel(tmp.name)
            if mode=="remplacer":
                with db.get_connection() as conn:
                    conn.execute("DELETE FROM projets"); conn.commit()
            inseres=ignores=0
            for _, row in df.iterrows():
                promoteur = str(row.get(col_promoteur,"")).strip()
                intitule  = str(row.get(col_intitule,"")).strip()
                if not promoteur or not intitule or promoteur=="nan" or intitule=="nan":
                    ignores+=1; continue
                contact = str(row.get(col_contact,"")).strip() if col_contact else ""
                type_p  = str(row.get(col_type,"")).strip() if col_type else ""
                cout    = str(row.get(col_cout,"")).strip() if col_cout else ""
                statut_c= str(row.get(col_statut_cout,"")).strip() if col_statut_cout else ""
                obs     = str(row.get(col_obs,"")).strip() if col_obs else ""
                date_str=None
                if col_date and col_date in df.columns:
                    raw=row.get(col_date)
                    if pd.notna(raw):
                        try: date_str=pd.to_datetime(raw).strftime("%Y-%m-%d")
                        except: pass
                db.add_projet(promoteur,intitule,
                              "" if contact=="nan" else contact,
                              "" if type_p=="nan" else type_p,
                              date_str,
                              "" if cout=="nan" else cout,
                              "" if statut_c=="nan" else statut_c,
                              "" if obs=="nan" else obs)
                inseres+=1
            flash(f"✅ {inseres} projet(s) importé(s), {ignores} ignoré(s).","success")
        except Exception as e: flash(f"❌ Erreur : {e}","error")
        finally: os.unlink(tmp.name)
        return redirect(url_for("projets"))
    return render_template("importer.html")

@app.route("/importer/preview", methods=["POST"])
def preview_fichier():
    if "fichier" not in request.files: return jsonify({"colonnes":[],"apercu":[]})
    f = request.files["fichier"]
    import pandas as pd, tempfile
    suffix = ".xlsx" if f.filename.endswith((".xlsx",".xls")) else ".csv"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    f.save(tmp.name)
    try:
        df = pd.read_csv(tmp.name,nrows=5,encoding="utf-8",errors="replace") if suffix==".csv" else pd.read_excel(tmp.name,nrows=5)
        cols=list(df.columns.astype(str))
        return jsonify({"colonnes":cols,"apercu":df.fillna("").astype(str).values.tolist(),"headers":cols})
    except Exception as e: return jsonify({"error":str(e)})
    finally: os.unlink(tmp.name)

@app.route("/configuration", methods=["GET","POST"])
def configuration():
    if request.method=="POST":
        for c in ["smtp_host","smtp_port","smtp_user","smtp_pass","alert_email","alert_days","auto_check_interval"]:
            val=request.form.get(c,"").strip()
            if val: db.set_config(c,val)
        flash("✅ Configuration sauvegardée.","success")
        cfg=db.get_config()
        es.start_scheduler(int(cfg.get("auto_check_interval",60)),callback=scheduler_callback)
        return redirect(url_for("configuration"))
    return render_template("configuration.html", cfg=db.get_config())

@app.route("/configuration/tester", methods=["POST"])
def tester_email():
    cfg=db.get_config()
    try:
        import smtplib
        from email.mime.text import MIMEText
        msg=MIMEText("✅ Test SMTP réussi – ANDE ERP","plain","utf-8")
        msg["Subject"]="✅ Test SMTP – ANDE"; msg["From"]=cfg["smtp_user"]; msg["To"]=cfg["alert_email"]
        with smtplib.SMTP(cfg["smtp_host"],int(cfg["smtp_port"]),timeout=15) as s:
            s.ehlo(); s.starttls(); s.login(cfg["smtp_user"],cfg["smtp_pass"])
            s.sendmail(cfg["smtp_user"],cfg["alert_email"],msg.as_string())
        flash(f"✅ Email de test envoyé à {cfg['alert_email']} !","success")
    except Exception as e: flash(f"❌ Erreur SMTP : {e}","error")
    return redirect(url_for("configuration"))

@app.route("/api/stats")
def api_stats(): return jsonify(db.get_stats())

if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port,debug=False)
