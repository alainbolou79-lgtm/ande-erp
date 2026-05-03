"""
Module de gestion de la base de données SQLite
Suivi des projets environnementaux – Alertes Email
"""
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projets.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Crée les tables si elles n'existent pas."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS projets (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                promoteur       TEXT NOT NULL,
                intitule        TEXT NOT NULL,
                date_passage    TEXT,
                date_creation   TEXT DEFAULT (datetime('now','localtime')),
                date_modif      TEXT DEFAULT (datetime('now','localtime')),
                alerte_envoyee  INTEGER DEFAULT 0,
                nb_alertes      INTEGER DEFAULT 0,
                derniere_alerte TEXT,
                notes           TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS historique_alertes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                projet_id   INTEGER NOT NULL,
                date_envoi  TEXT DEFAULT (datetime('now','localtime')),
                destinataire TEXT NOT NULL,
                jours_ecoules INTEGER,
                statut      TEXT DEFAULT 'envoyé',
                FOREIGN KEY (projet_id) REFERENCES projets(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS config (
                cle     TEXT PRIMARY KEY,
                valeur  TEXT
            );
        """)
        # Config par défaut
        defaults = [
            ("smtp_host", "smtp.gmail.com"),
            ("smtp_port", "587"),
            ("smtp_user", ""),
            ("smtp_pass", ""),
            ("alert_email", "alainbolou@yahoo.fr"),
            ("alert_days", "15"),
            ("auto_check_interval", "60"),  # minutes
        ]
        for cle, val in defaults:
            conn.execute(
                "INSERT OR IGNORE INTO config (cle, valeur) VALUES (?, ?)",
                (cle, val)
            )
        conn.commit()


def import_from_json(json_path):
    """Importe les données depuis l'ancien fichier JSON."""
    if not os.path.exists(json_path):
        return 0
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM projets").fetchone()[0]
        if count > 0:
            return 0  # Déjà importé
        inserted = 0
        for p in data:
            conn.execute(
                """INSERT INTO projets (promoteur, intitule, date_passage, alerte_envoyee)
                   VALUES (?, ?, ?, ?)""",
                (p.get("promoteur", ""), p.get("intitule", ""),
                 p.get("date_passage", "") or None,
                 1 if p.get("alerte_envoyee") else 0)
            )
            inserted += 1
        conn.commit()
    return inserted


# ── CRUD Projets ────────────────────────────────────────────────────────────

def get_all_projets(search="", filtre="tous"):
    with get_connection() as conn:
        sql = "SELECT * FROM projets WHERE 1=1"
        params = []
        if search:
            sql += " AND (LOWER(promoteur) LIKE ? OR LOWER(intitule) LIKE ?)"
            params += [f"%{search.lower()}%", f"%{search.lower()}%"]
        if filtre == "alerte":
            sql += " AND date_passage IS NOT NULL AND date_passage != '' AND CAST((julianday('now','localtime') - julianday(date_passage)) AS INTEGER) > 15"
        elif filtre == "sans_date":
            sql += " AND (date_passage IS NULL OR date_passage = '')"
        elif filtre == "ok":
            sql += " AND date_passage IS NOT NULL AND date_passage != '' AND CAST((julianday('now','localtime') - julianday(date_passage)) AS INTEGER) <= 15"
        sql += " ORDER BY date_passage DESC NULLS LAST, id DESC"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def get_projet(pid):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM projets WHERE id=?", (pid,)).fetchone()
        return dict(row) if row else None


def add_projet(promoteur, intitule, date_passage=None, notes=""):
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO projets (promoteur, intitule, date_passage, notes)
               VALUES (?, ?, ?, ?)""",
            (promoteur.strip(), intitule.strip(), date_passage or None, notes)
        )
        conn.commit()
        return cur.lastrowid


def update_projet(pid, promoteur, intitule, date_passage=None, notes=""):
    with get_connection() as conn:
        conn.execute(
            """UPDATE projets SET promoteur=?, intitule=?, date_passage=?,
               notes=?, date_modif=datetime('now','localtime')
               WHERE id=?""",
            (promoteur.strip(), intitule.strip(), date_passage or None, notes, pid)
        )
        conn.commit()


def delete_projet(pid):
    with get_connection() as conn:
        conn.execute("DELETE FROM projets WHERE id=?", (pid,))
        conn.commit()


def get_projets_en_alerte(seuil_jours=15):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *,
                   CAST((julianday('now','localtime') - julianday(date_passage)) AS INTEGER) AS jours_ecoules
            FROM projets
            WHERE date_passage IS NOT NULL AND date_passage != ''
              AND CAST((julianday('now','localtime') - julianday(date_passage)) AS INTEGER) > ?
            ORDER BY jours_ecoules DESC
        """, (seuil_jours,)).fetchall()
        return [dict(r) for r in rows]


def marquer_alerte_envoyee(projet_ids, destinataire):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        for pid in projet_ids:
            p = conn.execute("SELECT * FROM projets WHERE id=?", (pid,)).fetchone()
            if p:
                jours = p["date_passage"] and int(
                    (datetime.now() - datetime.strptime(p["date_passage"], "%Y-%m-%d")).days
                )
                conn.execute("""
                    UPDATE projets SET alerte_envoyee=1, nb_alertes=nb_alertes+1,
                           derniere_alerte=?, date_modif=? WHERE id=?
                """, (now, now, pid))
                conn.execute("""
                    INSERT INTO historique_alertes (projet_id, destinataire, jours_ecoules)
                    VALUES (?, ?, ?)
                """, (pid, destinataire, jours))
        conn.commit()


# ── Historique ──────────────────────────────────────────────────────────────

def get_historique(limit=200):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT h.*, p.promoteur, p.intitule
            FROM historique_alertes h
            JOIN projets p ON h.projet_id = p.id
            ORDER BY h.date_envoi DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]


def get_stats():
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM projets").fetchone()[0]
        alertes = conn.execute("""
            SELECT COUNT(*) FROM projets
            WHERE date_passage IS NOT NULL AND date_passage != ''
              AND CAST((julianday('now','localtime') - julianday(date_passage)) AS INTEGER) > 15
        """).fetchone()[0]
        attention = conn.execute("""
            SELECT COUNT(*) FROM projets
            WHERE date_passage IS NOT NULL AND date_passage != ''
              AND CAST((julianday('now','localtime') - julianday(date_passage)) AS INTEGER) BETWEEN 10 AND 15
        """).fetchone()[0]
        ok = conn.execute("""
            SELECT COUNT(*) FROM projets
            WHERE date_passage IS NOT NULL AND date_passage != ''
              AND CAST((julianday('now','localtime') - julianday(date_passage)) AS INTEGER) < 10
        """).fetchone()[0]
        sans_date = conn.execute("""
            SELECT COUNT(*) FROM projets WHERE date_passage IS NULL OR date_passage = ''
        """).fetchone()[0]
        total_alertes_envoyees = conn.execute("SELECT COUNT(*) FROM historique_alertes").fetchone()[0]
        return {
            "total": total, "alertes": alertes, "attention": attention,
            "ok": ok, "sans_date": sans_date, "total_alertes_envoyees": total_alertes_envoyees
        }


# ── Config ──────────────────────────────────────────────────────────────────

def get_config():
    with get_connection() as conn:
        rows = conn.execute("SELECT cle, valeur FROM config").fetchall()
        return {r["cle"]: r["valeur"] for r in rows}


def set_config(cle, valeur):
    with get_connection() as conn:
        conn.execute("INSERT OR REPLACE INTO config (cle, valeur) VALUES (?, ?)", (cle, valeur))
        conn.commit()
