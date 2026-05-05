


{% extends "base.html" %}
{% block title %}Alertes Actives{% endblock %}
{% block content %}
<main>
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:10px">
    <div>
      <h2 style="font-size:16px;font-weight:700;color:var(--danger)">
        ⚠️ {{ alertes|length }} projet(s) hors délais (> {{ seuil }} jours)
      </h2>
      <p style="font-size:12px;color:var(--text-dim);margin-top:4px">
        Les emails d'alerte sont envoyés automatiquement toutes les 60 minutes.
      </p>
    </div>
    <form method="post" action="{{ url_for('envoyer_alertes') }}">
      <button type="submit" class="btn btn-orange">
        📧 Envoyer les alertes maintenant
      </button>
    </form>
  </div>

  {% if alertes %}
    {% for p in alertes %}
    <div class="alert-card">
      <div style="flex:1">
        <div class="ac-title">
          {{ p.promoteur }}
          <span style="color:var(--danger);font-weight:700"> – {{ p.intitule[:80] }}{% if p.intitule|length>80 %}...{% endif %} est hors délais</span>
        </div>
        <div class="ac-sub" style="margin-top:6px;display:flex;gap:20px;flex-wrap:wrap">
          <span>📅 Date de passage :
            <strong style="color:var(--text)">
              {% if p.date_passage %}
                {{ p.date_passage[8:10] }}/{{ p.date_passage[5:7] }}/{{ p.date_passage[:4] }}
              {% else %}—{% endif %}
            </strong>
          </span>
          <span>📧 Alertes envoyées : <strong style="color:var(--accent)">{{ p.nb_alertes or 0 }}</strong></span>
          {% if p.derniere_alerte %}
          <span>🕐 Dernière alerte : <strong style="color:var(--text)">{{ p.derniere_alerte[:16] }}</strong></span>
          {% endif %}
        </div>
      </div>
      <div class="ac-days">
        {{ p.jours_ecoules }}
        <span>jours de retard</span>
      </div>
      <a href="{{ url_for('modifier_projet', pid=p.id) }}" class="btn btn-warning btn-sm">✏️ Modifier</a>
    </div>
    {% endfor %}
  {% else %}
    <div class="card" style="text-align:center;padding:40px">
      <div style="font-size:48px;margin-bottom:12px">✅</div>
      <div style="font-size:16px;color:var(--success);font-weight:700">
        Aucun projet hors délais !
      </div>
      <div style="font-size:13px;color:var(--text-dim);margin-top:8px">
        Tous les projets sont dans les délais impartis.
      </div>
    </div>
  {% endif %}
</main>
{% endblock %}

<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ANDE – {% block title %}ERP{% endblock %}</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --green:      #1A6B2A;
      --green-dark: #0D4A1A;
      --green-light:#2E8B40;
      --accent:     #00C9A7;
      --bg:         #0F1923;
      --panel:      #162030;
      --card:       #1E2D3D;
      --border:     #243447;
      --text:       #E8F0FE;
      --text-dim:   #7A8FA6;
      --danger:     #FF4444;
      --warning:    #FFB800;
      --success:    #4CAF50;
      --orange:     #FF6B35;
    }
    body { font-family: 'Segoe UI', Arial, sans-serif; background: var(--bg);
           color: var(--text); min-height: 100vh; }

    /* ── HEADER ANDE ── */
    .ande-header {
      background: var(--green);
      padding: 0;
      overflow: hidden;
    }
    .ande-header img.banner {
      width: 100%; height: 90px; object-fit: cover; object-position: left center;
      display: block;
    }
    .ande-header .fallback {
      display: flex; align-items: center; padding: 16px 24px; gap: 16px;
    }
    .ande-header .fallback h1 {
      color: white; font-size: 20px; font-weight: 700;
    }

    /* ── SERVICE BAR ── */
    .service-bar {
      background: var(--green-dark);
      display: flex; align-items: center; justify-content: space-between;
      padding: 10px 24px;
    }
    .service-bar .service-title {
      font-size: 14px; font-weight: 700; color: white; letter-spacing: 1px;
    }
    .service-bar .service-right {
      font-size: 12px; color: #A8D5A2; display: flex; gap: 20px; align-items: center;
    }

    /* ── NAV ── */
    nav {
      background: var(--panel);
      border-bottom: 1px solid var(--border);
      display: flex; align-items: center; gap: 4px; padding: 0 16px;
      overflow-x: auto;
    }
    nav a {
      display: flex; align-items: center; gap: 6px;
      color: var(--text-dim); text-decoration: none;
      padding: 14px 18px; font-size: 13px; font-weight: 600;
      border-bottom: 3px solid transparent;
      white-space: nowrap; transition: all .2s;
    }
    nav a:hover { color: var(--text); background: var(--card); }
    nav a.active { color: var(--accent); border-bottom-color: var(--accent); }

    /* ── STATS BAR ── */
    .stats-bar {
      display: grid; grid-template-columns: repeat(6, 1fr);
      gap: 8px; padding: 12px 20px; background: var(--panel);
      border-bottom: 1px solid var(--border);
    }
    .stat-card {
      background: var(--card); border-radius: 10px;
      padding: 12px; text-align: center;
    }
    .stat-card .val { font-size: 26px; font-weight: 700; }
    .stat-card .lbl { font-size: 10px; color: var(--text-dim);
                      text-transform: uppercase; letter-spacing: .5px; margin-top: 2px; }

    /* ── MAIN ── */
    main { padding: 20px; }

    /* ── CARDS ── */
    .card {
      background: var(--card); border-radius: 12px;
      border: 1px solid var(--border); padding: 20px; margin-bottom: 16px;
    }
    .card-title {
      font-size: 13px; font-weight: 700; color: var(--accent);
      text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px;
      padding-bottom: 10px; border-bottom: 1px solid var(--border);
    }

    /* ── TABLE ── */
    .table-wrap { overflow-x: auto; border-radius: 10px; border: 1px solid var(--border); }
    table { width: 100%; border-collapse: collapse; }
    thead tr { background: #0A1520; }
    thead th {
      padding: 12px 14px; text-align: left; font-size: 11px;
      color: var(--accent); text-transform: uppercase; letter-spacing: .8px;
      font-weight: 700; white-space: nowrap;
    }
    tbody tr { border-bottom: 1px solid var(--border); transition: background .15s; }
    tbody tr:hover { background: rgba(255,255,255,.03); }
    tbody td { padding: 12px 14px; font-size: 13px; vertical-align: middle; }
    tbody tr:last-child { border-bottom: none; }

    /* ── BADGES ── */
    .badge {
      display: inline-block; padding: 4px 10px; border-radius: 20px;
      font-size: 11px; font-weight: 700; white-space: nowrap;
    }
    .badge-alerte  { background: rgba(255,68,68,.15);  color: #FF6B6B; }
    .badge-warning { background: rgba(255,184,0,.15);  color: #FFB800; }
    .badge-ok      { background: rgba(76,175,80,.15);  color: #4CAF50; }
    .badge-nodate  { background: rgba(122,143,166,.15);color: var(--text-dim); }

    /* ── BUTTONS ── */
    .btn {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 9px 18px; border-radius: 8px; border: none;
      font-size: 13px; font-weight: 600; cursor: pointer;
      text-decoration: none; transition: all .2s; white-space: nowrap;
    }
    .btn-primary  { background: var(--accent);   color: #0A1520; }
    .btn-danger   { background: var(--danger);   color: white; }
    .btn-warning  { background: var(--warning);  color: #0A1520; }
    .btn-orange   { background: var(--orange);   color: white; }
    .btn-dim      { background: var(--border);   color: var(--text); }
    .btn:hover    { opacity: .85; transform: translateY(-1px); }
    .btn-sm       { padding: 5px 12px; font-size: 12px; }

    /* ── FORMS ── */
    .form-group { margin-bottom: 16px; }
    .form-group label {
      display: block; font-size: 12px; color: var(--text-dim);
      text-transform: uppercase; letter-spacing: .5px;
      margin-bottom: 6px; font-weight: 600;
    }
    .form-group input, .form-group select, .form-group textarea {
      width: 100%; padding: 10px 14px; border-radius: 8px;
      border: 1px solid var(--border); background: var(--panel);
      color: var(--text); font-size: 14px; font-family: inherit;
      transition: border .2s;
    }
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
      outline: none; border-color: var(--accent);
    }
    .form-group textarea { min-height: 90px; resize: vertical; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

    /* ── ALERTS ── */
    .flash { padding: 12px 18px; border-radius: 8px; margin-bottom: 16px;
             font-size: 13px; font-weight: 600; }
    .flash-success { background: rgba(76,175,80,.15); color: #4CAF50;
                     border: 1px solid rgba(76,175,80,.3); }
    .flash-error   { background: rgba(255,68,68,.15);  color: #FF6B6B;
                     border: 1px solid rgba(255,68,68,.3); }

    /* ── TOOLBAR ── */
    .toolbar {
      display: flex; align-items: center; gap: 10px;
      margin-bottom: 16px; flex-wrap: wrap;
    }
    .toolbar .search-box {
      display: flex; align-items: center; gap: 8px;
      background: var(--card); border: 1px solid var(--border);
      border-radius: 8px; padding: 8px 14px; flex: 1; max-width: 320px;
    }
    .toolbar .search-box input {
      background: none; border: none; color: var(--text);
      font-size: 13px; outline: none; width: 100%;
    }
    .filter-tabs { display: flex; gap: 4px; }
    .filter-tab {
      padding: 7px 14px; border-radius: 20px; font-size: 12px;
      font-weight: 600; cursor: pointer; text-decoration: none;
      color: var(--text-dim); background: var(--card);
      border: 1px solid var(--border); transition: all .2s;
    }
    .filter-tab.active, .filter-tab:hover {
      background: var(--accent); color: var(--bg); border-color: var(--accent);
    }

    /* ── PROJET ROW alertes ── */
    tr.row-alerte  { background: rgba(255,68,68,.05); }
    tr.row-warning { background: rgba(255,184,0,.05); }

    /* ── Alert cards ── */
    .alert-card {
      background: var(--card); border-radius: 12px;
      border-left: 4px solid var(--danger);
      padding: 16px 20px; margin-bottom: 12px;
      display: flex; align-items: center; justify-content: space-between;
      flex-wrap: wrap; gap: 10px;
    }
    .alert-card .ac-title { font-size: 14px; font-weight: 700; color: var(--text); }
    .alert-card .ac-sub   { font-size: 12px; color: var(--text-dim); margin-top: 4px; }
    .alert-card .ac-days  { font-size: 28px; font-weight: 700; color: var(--danger);
                            text-align: center; min-width: 80px; }
    .alert-card .ac-days span { font-size: 11px; display: block; color: var(--text-dim); }

    /* ── Responsive ── */
    @media (max-width: 768px) {
      .stats-bar { grid-template-columns: repeat(3,1fr); }
      .form-row  { grid-template-columns: 1fr; }
    }
    @media (max-width: 480px) {
      .stats-bar { grid-template-columns: repeat(2,1fr); }
    }
  </style>
</head>
<body>

  <!-- BANNIÈRE ANDE -->
  <header class="ande-header">
    <img class="banner" src="{{ url_for('static', filename='img/ande_logo.jpg') }}"
         alt="ANDE" onerror="this.style.display='none';document.querySelector('.fallback').style.display='flex'">
    <div class="fallback" style="display:none">
      <h1>🌿 AGENCE NATIONALE DE L'ENVIRONNEMENT – ANDE</h1>
    </div>
  </header>

  <!-- BARRE SERVICE -->
  <div class="service-bar">
    <span class="service-title">🏛️ SERVICE PROMOTEUR ET RELATIONS EXTERIEURES</span>
    <div class="service-right">
      <span>📧 {{ config.get('alert_email','alainbolou@yahoo.fr') if config is defined else 'alainbolou@yahoo.fr' }}</span>
      <span id="clock">⏰ --:--:--</span>
    </div>
  </div>

  <!-- NAVIGATION -->
  <nav>
    <a href="{{ url_for('index') }}"          class="{{ 'active' if request.endpoint=='index' }}">🏠 Tableau de bord</a>
    <a href="{{ url_for('projets') }}"         class="{{ 'active' if request.endpoint=='projets' }}">📋 Projets</a>
    <a href="{{ url_for('alertes') }}"         class="{{ 'active' if request.endpoint=='alertes' }}">🔴 Alertes</a>
    <a href="{{ url_for('historique') }}"      class="{{ 'active' if request.endpoint=='historique' }}">📜 Historique</a>
    <a href="{{ url_for('importer') }}"        class="{{ 'active' if request.endpoint=='importer' }}">📥 Importer</a>
    <a href="{{ url_for('configuration') }}"   class="{{ 'active' if request.endpoint=='configuration' }}">⚙️ Configuration</a>
  </nav>

  <!-- FLASH MESSAGES -->
  <div style="padding: 0 20px; margin-top: 12px;">
    {% for cat, msg in get_flashed_messages(with_categories=True) %}
      <div class="flash flash-{{ cat }}">{{ msg }}</div>
    {% endfor %}
  </div>

  {% block content %}{% endblock %}

  <script>
    // Horloge
    function updateClock() {
      const now = new Date();
      document.getElementById("clock").textContent =
        "⏰ " + now.toLocaleTimeString("fr-FR");
    }
    setInterval(updateClock, 1000); updateClock();
  </script>
  {% block scripts %}{% endblock %}
</body>
</html>

{% extends "base.html" %}
{% block title %}Configuration{% endblock %}
{% block content %}
<main>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;max-width:1000px">

    <!-- Config SMTP -->
    <div class="card">
      <div class="card-title">⚙️ CONFIGURATION SMTP</div>
      <form method="post">
        <div class="form-group">
          <label>Email destinataire des alertes</label>
          <input type="email" name="alert_email" value="{{ cfg.get('alert_email','alainbolou@yahoo.fr') }}">
        </div>
        <div class="form-group">
          <label>Seuil d'alerte (jours)</label>
          <input type="number" name="alert_days" value="{{ cfg.get('alert_days','15') }}" min="1" max="365">
        </div>
        <div class="form-group">
          <label>Serveur SMTP</label>
          <input type="text" name="smtp_host" value="{{ cfg.get('smtp_host','smtp.gmail.com') }}">
        </div>
        <div class="form-group">
          <label>Port SMTP</label>
          <input type="number" name="smtp_port" value="{{ cfg.get('smtp_port','587') }}">
        </div>
        <div class="form-group">
          <label>Email expéditeur (login Gmail)</label>
          <input type="email" name="smtp_user" value="{{ cfg.get('smtp_user','') }}" placeholder="votre@gmail.com">
        </div>
        <div class="form-group">
          <label>Mot de passe / App Password</label>
          <input type="password" name="smtp_pass" value="{{ cfg.get('smtp_pass','') }}" placeholder="••••••••••••••••">
        </div>
        <div class="form-group">
          <label>Intervalle de vérification (minutes)</label>
          <input type="number" name="auto_check_interval" value="{{ cfg.get('auto_check_interval','60') }}" min="10">
        </div>
        <div style="display:flex;gap:10px;margin-top:8px">
          <button type="submit" class="btn btn-primary">💾 Sauvegarder</button>
        </div>
      </form>
    </div>

    <!-- Aide + Test -->
    <div>
      <div class="card" style="margin-bottom:16px">
        <div class="card-title">🧪 TESTER L'ENVOI EMAIL</div>
        <p style="font-size:13px;color:var(--text-dim);margin-bottom:14px">
          Envoie un email de test à {{ cfg.get('alert_email','alainbolou@yahoo.fr') }} pour vérifier la configuration.
        </p>
        <form method="post" action="{{ url_for('tester_email') }}">
          <button type="submit" class="btn btn-orange">📧 Envoyer un email de test</button>
        </form>
      </div>

      <div class="card">
        <div class="card-title">💡 AIDE – GMAIL APP PASSWORD</div>
        <div style="font-size:13px;color:var(--text-dim);line-height:1.8">
          <p style="margin-bottom:8px">Pour Gmail, vous devez créer un <strong style="color:var(--text)">App Password</strong> :</p>
          <ol style="padding-left:18px">
            <li>Allez sur <strong style="color:var(--accent)">myaccount.google.com/apppasswords</strong></li>
            <li>Connectez-vous avec votre compte Gmail</li>
            <li>Tapez un nom : <em>ANDE ERP</em></li>
            <li>Cliquez <strong>Créer</strong></li>
            <li>Copiez le code 16 caractères</li>
            <li>Collez-le dans le champ <strong>Mot de passe</strong> ci-contre</li>
          </ol>
          <div style="margin-top:14px;padding:10px;background:var(--panel);border-radius:8px;border-left:3px solid var(--accent)">
            <strong style="color:var(--accent)">Yahoo :</strong> smtp.mail.yahoo.com port 587<br>
            <strong style="color:var(--accent)">Gmail :</strong> smtp.gmail.com port 587
          </div>
        </div>
      </div>
    </div>
  </div>
</main>
{% endblock %}

{% extends "base.html" %}
{% block title %}{{ 'Modifier' if projet else 'Nouveau' }} Projet{% endblock %}
{% block content %}
<main>
  <div class="card" style="max-width:800px;margin:0 auto">
    <div class="card-title">{{ '✏️ MODIFIER LE PROJET' if projet else '➕ NOUVEAU PROJET' }}</div>
    <form method="post">

      <div class="form-row">
        <div class="form-group">
          <label>PROMOTEUR *</label>
          <input type="text" name="promoteur" required value="{{ data.get('promoteur','') }}" placeholder="Nom du promoteur">
        </div>
        <div class="form-group">
          <label>CONTACT PROMOTEUR</label>
          <input type="text" name="contact_promoteur" value="{{ data.get('contact_promoteur','') }}" placeholder="Téléphone / Email du contact">
        </div>
      </div>

      <div class="form-group">
        <label>INTITULÉ DU PROJET *</label>
        <textarea name="intitule" required placeholder="Description complète du projet">{{ data.get('intitule','') }}</textarea>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>TYPE DE PROJET</label>
          <select name="type_projet">
            <option value="">-- Choisir --</option>
            <option value="AES"  {{ 'selected' if data.get('type_projet','')=='AES' }}>AES – Audit Environnemental et Social</option>
            <option value="ERES" {{ 'selected' if data.get('type_projet','')=='ERES' }}>ERES – Étude Relative à l'Environnement et Social</option>
            <option value="EES"  {{ 'selected' if data.get('type_projet','')=='EES' }}>EES – Évaluation Environnementale Stratégique</option>
            <option value="EIES" {{ 'selected' if data.get('type_projet','')=='EIES' }}>EIES – Étude d'Impact Environnemental et Social</option>
            <option value="SE"   {{ 'selected' if data.get('type_projet','')=='SE' }}>SE – Suivi Environnemental</option>
          </select>
        </div>
        <div class="form-group">
          <label>DATE DE PASSAGE</label>
          <input type="date" name="date_passage" value="{{ data.get('date_passage','') }}">
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>COÛT DU PROJET</label>
          <input type="text" name="cout_projet" value="{{ data.get('cout_projet','') }}" placeholder="Ex: 5 000 000 FCFA">
        </div>
        <div class="form-group">
          <label>STATUT DU COÛT</label>
          <select name="statut_cout">
            <option value="">-- Choisir --</option>
            <option value="Réglé"     {{ 'selected' if data.get('statut_cout','')=='Réglé' }}>✅ Réglé</option>
            <option value="Non réglé" {{ 'selected' if data.get('statut_cout','')=='Non réglé' }}>❌ Non réglé</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>OBSERVATIONS</label>
        <textarea name="observations" placeholder="Remarques, notes complémentaires...">{{ data.get('observations','') }}</textarea>
      </div>

      <div style="display:flex;gap:10px;margin-top:8px">
        <button type="submit" class="btn btn-primary">💾 Enregistrer</button>
        <a href="{{ url_for('projets') }}" class="btn btn-dim">Annuler</a>
      </div>
    </form>
  </div>
</main>
{% endblock %}

{% extends "base.html" %}
{% block title %}Historique{% endblock %}
{% block content %}
<main>
  <div class="card">
    <div class="card-title">📜 HISTORIQUE DES ALERTES ENVOYÉES – {{ historique|length }} entrée(s)</div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>DATE & HEURE</th>
            <th>PROMOTEUR</th>
            <th>INTITULÉ</th>
            <th>JOURS</th>
            <th>DESTINATAIRE</th>
            <th>STATUT</th>
          </tr>
        </thead>
        <tbody>
          {% for h in historique %}
          <tr>
            <td style="white-space:nowrap;color:var(--text-dim)">{{ h.date_envoi[:16] }}</td>
            <td style="font-weight:600">{{ h.promoteur }}</td>
            <td style="color:var(--text-dim)">
              {{ h.intitule[:60] }}{% if h.intitule|length > 60 %}...{% endif %}
            </td>
            <td style="text-align:center;color:var(--danger);font-weight:700">
              {{ h.jours_ecoules or '—' }} j
            </td>
            <td style="color:var(--accent)">{{ h.destinataire }}</td>
            <td><span class="badge badge-ok">✅ {{ h.statut }}</span></td>
          </tr>
          {% else %}
          <tr><td colspan="6" style="text-align:center;padding:40px;color:var(--text-dim)">
            Aucune alerte envoyée pour l'instant.
          </td></tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</main>
{% endblock %}

{% extends "base.html" %}
{% block title %}Importer{% endblock %}
{% block content %}
<main>
  <div class="card" style="max-width:900px;margin:0 auto">
    <div class="card-title">📥 IMPORTER UNE BASE DE DONNÉES EXISTANTE</div>
    <p style="font-size:13px;color:var(--text-dim);margin-bottom:20px">
      Importez vos projets depuis un fichier Excel (.xlsx) ou CSV (.csv). Les colonnes sont détectées automatiquement.
    </p>
    <form method="post" enctype="multipart/form-data" id="importForm">

      <div style="background:var(--panel);border-radius:10px;padding:16px;margin-bottom:16px;border:1px solid var(--border)">
        <div style="font-size:12px;font-weight:700;color:var(--accent);margin-bottom:10px;text-transform:uppercase">Étape 1 – Choisir le fichier</div>
        <input type="file" name="fichier" id="fichierInput" accept=".xlsx,.xls,.csv" required style="color:var(--text);cursor:pointer" onchange="previewFile(this)">
      </div>

      <div id="colonnesSection" style="display:none;background:var(--panel);border-radius:10px;padding:16px;margin-bottom:16px;border:1px solid var(--border)">
        <div style="font-size:12px;font-weight:700;color:var(--accent);margin-bottom:14px;text-transform:uppercase">Étape 2 – Associer les colonnes</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
          {% for key,lbl,req in [
            ('col_promoteur','PROMOTEUR',True),
            ('col_intitule','INTITULÉ DU PROJET',True),
            ('col_contact','CONTACT PROMOTEUR',False),
            ('col_type','TYPE DE PROJET',False),
            ('col_date_passage','DATE DE PASSAGE',False),
            ('col_cout','COÛT DU PROJET',False),
            ('col_statut_cout','STATUT DU COÛT',False),
            ('col_observations','OBSERVATIONS',False),
          ] %}
          <div class="form-group" style="margin:0">
            <label>{{ lbl }} {% if req %}<span style="color:var(--danger)">*</span>{% else %}<span style="color:var(--text-dim)">(optionnel)</span>{% endif %}</label>
            <select name="{{ key }}" id="sel_{{ key }}" class="col-select">
              <option value="">{% if req %}(sélectionner){% else %}(ignorer){% endif %}</option>
            </select>
          </div>
          {% endfor %}
        </div>

        <div style="margin-top:16px">
          <div style="font-size:12px;color:var(--text-dim);margin-bottom:8px;font-weight:700">APERÇU DES DONNÉES</div>
          <div class="table-wrap" id="apercu"></div>
        </div>
      </div>

      <div id="optionsSection" style="display:none;background:var(--panel);border-radius:10px;padding:16px;margin-bottom:16px;border:1px solid var(--border)">
        <div style="font-size:12px;font-weight:700;color:var(--accent);margin-bottom:12px;text-transform:uppercase">Étape 3 – Options</div>
        <label style="display:flex;align-items:center;gap:10px;cursor:pointer;margin-bottom:10px">
          <input type="radio" name="mode" value="ajouter" checked>
          <span style="font-size:13px">➕ Ajouter à la base existante <strong>(recommandé)</strong></span>
        </label>
        <label style="display:flex;align-items:center;gap:10px;cursor:pointer">
          <input type="radio" name="mode" value="remplacer">
          <span style="font-size:13px;color:var(--danger)">⚠️ Remplacer toute la base</span>
        </label>
      </div>

      <div id="btnSection" style="display:none">
        <button type="submit" class="btn btn-primary">🚀 Lancer l'importation</button>
        <a href="{{ url_for('projets') }}" class="btn btn-dim" style="margin-left:10px">Annuler</a>
      </div>
    </form>
  </div>
</main>
{% endblock %}
{% block scripts %}
<script>
const autoMap = {
  "sel_col_promoteur":   /promoteur|promo|porteur|nom/,
  "sel_col_intitule":    /intitul|projet|description|objet|titre/,
  "sel_col_contact":     /contact|tel|phone|email|mail/,
  "sel_col_type":        /type|categorie/,
  "sel_col_date_passage":/date|passage/,
  "sel_col_cout":        /cout|co.t|montant|prix/,
  "sel_col_statut_cout": /statut|regl|paiement/,
  "sel_col_observations":/obs|note|remarque|commentaire/,
};
async function previewFile(input) {
  const file = input.files[0]; if(!file) return;
  const fd = new FormData(); fd.append("fichier", file);
  const res  = await fetch("{{ url_for('preview_fichier') }}", {method:"POST",body:fd});
  const data = await res.json();
  if(data.error){ alert("Erreur: "+data.error); return; }
  const cols = data.colonnes;
  document.querySelectorAll(".col-select").forEach(sel => {
    const cur = sel.value;
    sel.innerHTML = sel.name==="col_promoteur"||sel.name==="col_intitule"
      ? '<option value="">(sélectionner)</option>'
      : '<option value="">(ignorer)</option>';
    cols.forEach(c => { const opt=new Option(c,c); sel.appendChild(opt); });
    // Auto-détection
    const pattern = autoMap["sel_"+sel.name];
    if(pattern) cols.forEach(c => { if(pattern.test(c.toLowerCase())) sel.value=c; });
  });
  let html="<table><thead><tr>";
  cols.forEach(c => html+=`<th>${c}</th>`);
  html+="</tr></thead><tbody>";
  data.apercu.forEach(row => { html+="<tr>"; row.forEach(cell => html+=`<td>${cell}</td>`); html+="</tr>"; });
  html+="</tbody></table>";
  document.getElementById("apercu").innerHTML=html;
  document.getElementById("colonnesSection").style.display="block";
  document.getElementById("optionsSection").style.display="block";
  document.getElementById("btnSection").style.display="block";
}
</script>
{% endblock %}

{% extends "base.html" %}
{% block title %}Tableau de bord{% endblock %}
{% block content %}

<div class="stats-bar">
  <div class="stat-card"><div class="val" style="color:var(--text)">{{ stats.total }}</div><div class="lbl">📋 Total projets</div></div>
  <div class="stat-card"><div class="val" style="color:var(--danger)">{{ stats.alertes }}</div><div class="lbl">🔴 Alertes</div></div>
  <div class="stat-card"><div class="val" style="color:var(--warning)">{{ stats.attention }}</div><div class="lbl">🟡 Attention</div></div>
  <div class="stat-card"><div class="val" style="color:var(--success)">{{ stats.ok }}</div><div class="lbl">🟢 OK</div></div>
  <div class="stat-card"><div class="val" style="color:#00C9A7">{{ stats.aes }}</div><div class="lbl">🔵 AES</div></div>
  <div class="stat-card"><div class="val" style="color:#9B59B6">{{ stats.eres }}</div><div class="lbl">🟣 ERES</div></div>
  <div class="stat-card"><div class="val" style="color:var(--success)">{{ stats.regle }}</div><div class="lbl">💰 Réglé</div></div>
  <div class="stat-card"><div class="val" style="color:var(--danger)">{{ stats.non_regle }}</div><div class="lbl">❌ Non réglé</div></div>
</div>

<main>

  <!-- Ligne 1 : Alertes + Actions rapides -->
  <div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:16px">

    <div class="card">
      <div class="card-title">⚠️ Projets hors délais (Top 5)</div>
      {% if alertes %}
        {% for p in alertes %}
        <div class="alert-card">
          <div style="flex:1">
            <div class="ac-title">{{ p.promoteur }}
              {% if p.type_projet %}<span class="badge" style="background:rgba(0,201,167,.15);color:#00C9A7;margin-left:8px;font-size:10px">{{ p.type_projet }}</span>{% endif %}
            </div>
            <div class="ac-sub">{{ p.intitule[:80] }}{% if p.intitule|length>80 %}...{% endif %}</div>
            <div style="display:flex;gap:16px;margin-top:6px;flex-wrap:wrap">
              <span class="ac-sub">📅 {{ p.date_passage or '—' }}</span>
              {% if p.statut_cout %}<span class="ac-sub">💰 {{ p.statut_cout }}</span>{% endif %}
              {% if p.contact_promoteur %}<span class="ac-sub">📞 {{ p.contact_promoteur }}</span>{% endif %}
            </div>
          </div>
          <div class="ac-days">{{ p.jours_ecoules }}<span>jours</span></div>
        </div>
        {% endfor %}
        <a href="{{ url_for('alertes') }}" class="btn btn-orange" style="margin-top:8px">Voir toutes les alertes →</a>
      {% else %}
        <div style="text-align:center;padding:30px">
          <div style="font-size:40px">✅</div>
          <div style="color:var(--success);font-weight:700;margin-top:8px">Aucun projet hors délais !</div>
        </div>
      {% endif %}
    </div>

    <div class="card">
      <div class="card-title">⚡ Actions rapides</div>
      <div style="display:flex;flex-direction:column;gap:8px">
        <a href="{{ url_for('nouveau_projet') }}" class="btn btn-primary">➕ Nouveau projet</a>
        <a href="{{ url_for('alertes') }}" class="btn btn-orange">📧 Gérer les alertes</a>
        <a href="{{ url_for('projets') }}?filtre=non_regle" class="btn btn-danger">❌ Projets non réglés</a>
        <a href="{{ url_for('importer') }}" class="btn btn-dim">📥 Importer Excel/CSV</a>
        <a href="{{ url_for('historique') }}" class="btn btn-dim">📜 Historique emails</a>
        <a href="{{ url_for('configuration') }}" class="btn btn-dim">⚙️ Configuration SMTP</a>
      </div>
      <div style="margin-top:16px;padding:12px;background:var(--panel);border-radius:8px;border:1px solid var(--border)">
        <div style="font-size:11px;color:var(--text-dim);margin-bottom:4px">SCHEDULER AUTO</div>
        <div style="font-size:12px;color:var(--success)">🟢 Actif – toutes les 60 min</div>
        <div style="font-size:11px;color:var(--text-dim);margin-top:2px">+ quotidien à 08h00</div>
      </div>
    </div>
  </div>

  <!-- Ligne 2 : Graphiques -->
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px">

    <!-- Graphique 1 : Statut délai (Donut) -->
    <div class="card">
      <div class="card-title">⏱️ Statut des délais</div>
      <canvas id="chartDelai" height="200"></canvas>
      <div style="display:flex;justify-content:center;gap:16px;margin-top:12px;flex-wrap:wrap">
        <div style="display:flex;align-items:center;gap:6px;font-size:11px">
          <div style="width:12px;height:12px;border-radius:50%;background:#FF4444"></div>Alerte ({{ stats.alertes }})
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:11px">
          <div style="width:12px;height:12px;border-radius:50%;background:#FFB800"></div>Attention ({{ stats.attention }})
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:11px">
          <div style="width:12px;height:12px;border-radius:50%;background:#4CAF50"></div>OK ({{ stats.ok }})
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:11px">
          <div style="width:12px;height:12px;border-radius:50%;background:#7A8FA6"></div>Sans date ({{ stats.sans_date }})
        </div>
      </div>
    </div>

    <!-- Graphique 2 : Type projet (Donut) -->
    <div class="card">
      <div class="card-title">📊 Répartition par type</div>
      <canvas id="chartType" height="200"></canvas>
      <div style="display:flex;justify-content:center;gap:16px;margin-top:12px;flex-wrap:wrap">
        <div style="display:flex;align-items:center;gap:6px;font-size:11px">
          <div style="width:12px;height:12px;border-radius:50%;background:#00C9A7"></div>AES ({{ stats.aes }})
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:11px">
          <div style="width:12px;height:12px;border-radius:50%;background:#9B59B6"></div>ERES ({{ stats.eres }})
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:11px">
          <div style="width:12px;height:12px;border-radius:50%;background:#7A8FA6"></div>Autres ({{ stats.autres_type }})
        </div>
      </div>
    </div>

    <!-- Graphique 3 : Statut coût (Donut) -->
    <div class="card">
      <div class="card-title">💰 Statut des coûts</div>
      <canvas id="chartCout" height="200"></canvas>
      <div style="display:flex;justify-content:center;gap:16px;margin-top:12px;flex-wrap:wrap">
        <div style="display:flex;align-items:center;gap:6px;font-size:11px">
          <div style="width:12px;height:12px;border-radius:50%;background:#4CAF50"></div>Réglé ({{ stats.regle }})
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:11px">
          <div style="width:12px;height:12px;border-radius:50%;background:#FF4444"></div>Non réglé ({{ stats.non_regle }})
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:11px">
          <div style="width:12px;height:12px;border-radius:50%;background:#7A8FA6"></div>
          Non renseigné ({{ stats.total - stats.regle - stats.non_regle }})
        </div>
      </div>
    </div>
  </div>

  <!-- Ligne 3 : Graphique barres comparatif -->
  <div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:16px">
    <div class="card">
      <div class="card-title">📈 Vue comparative – Type vs Statut délai</div>
      <canvas id="chartBarre" height="120"></canvas>
    </div>

    <div class="card">
      <div class="card-title">📋 Résumé global</div>
      <table style="width:100%;font-size:13px">
        <tr style="border-bottom:1px solid var(--border)">
          <td style="padding:8px 0;color:var(--text-dim)">Total projets</td>
          <td style="text-align:right;font-weight:700">{{ stats.total }}</td>
        </tr>
        <tr style="border-bottom:1px solid var(--border)">
          <td style="padding:8px 0;color:var(--danger)">🔴 En alerte</td>
          <td style="text-align:right;font-weight:700;color:var(--danger)">{{ stats.alertes }}</td>
        </tr>
        <tr style="border-bottom:1px solid var(--border)">
          <td style="padding:8px 0;color:#00C9A7">🔵 Type AES</td>
          <td style="text-align:right;font-weight:700;color:#00C9A7">{{ stats.aes }}</td>
        </tr>
        <tr style="border-bottom:1px solid var(--border)">
          <td style="padding:8px 0;color:#9B59B6">🟣 Type ERES</td>
          <td style="text-align:right;font-weight:700;color:#9B59B6">{{ stats.eres }}</td>
        </tr>
        <tr style="border-bottom:1px solid var(--border)">
          <td style="padding:8px 0;color:var(--success)">💰 Coûts réglés</td>
          <td style="text-align:right;font-weight:700;color:var(--success)">{{ stats.regle }}</td>
        </tr>
        <tr style="border-bottom:1px solid var(--border)">
          <td style="padding:8px 0;color:var(--danger)">❌ Coûts non réglés</td>
          <td style="text-align:right;font-weight:700;color:var(--danger)">{{ stats.non_regle }}</td>
        </tr>
        <tr>
          <td style="padding:8px 0;color:var(--accent)">📧 Emails envoyés</td>
          <td style="text-align:right;font-weight:700;color:var(--accent)">{{ stats.total_alertes_envoyees }}</td>
        </tr>
      </table>
    </div>
  </div>

  <!-- Code couleur -->
  <div class="card">
    <div class="card-title">🎨 Code couleur</div>
    <div style="display:flex;gap:20px;flex-wrap:wrap">
      {% for badge,lbl in [('alerte','🔴 ALERTE – Plus de 15 jours'),('warning','🟡 ATTENTION – Entre 10 et 15 jours'),('ok','🟢 OK – Moins de 10 jours'),('nodate','⬜ SANS DATE – Pas de date renseignée')] %}
      <div style="display:flex;align-items:center;gap:8px">
        <span class="badge badge-{{ badge }}">{{ lbl.split(' – ')[0] }}</span>
        <span style="font-size:12px;color:var(--text-dim)">{{ lbl.split(' – ')[1] }}</span>
      </div>
      {% endfor %}
    </div>
  </div>

</main>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const chartDefaults = {
  plugins: { legend: { display: false } },
  responsive: true,
};

// Graphique 1 – Statut délai (Donut)
new Chart(document.getElementById('chartDelai'), {
  type: 'doughnut',
  data: {
    labels: ['Alerte', 'Attention', 'OK', 'Sans date'],
    datasets: [{
      data: [{{ stats.alertes }}, {{ stats.attention }}, {{ stats.ok }}, {{ stats.sans_date }}],
      backgroundColor: ['#FF4444','#FFB800','#4CAF50','#7A8FA6'],
      borderWidth: 0,
    }]
  },
  options: { ...chartDefaults, cutout: '65%' }
});

// Graphique 2 – Type projet (Donut)
new Chart(document.getElementById('chartType'), {
  type: 'doughnut',
  data: {
    labels: ['AES', 'ERES', 'Autres'],
    datasets: [{
      data: [{{ stats.aes }}, {{ stats.eres }}, {{ stats.autres_type }}],
      backgroundColor: ['#00C9A7','#9B59B6','#7A8FA6'],
      borderWidth: 0,
    }]
  },
  options: { ...chartDefaults, cutout: '65%' }
});

// Graphique 3 – Statut coût (Donut)
new Chart(document.getElementById('chartCout'), {
  type: 'doughnut',
  data: {
    labels: ['Réglé', 'Non réglé', 'Non renseigné'],
    datasets: [{
      data: [{{ stats.regle }}, {{ stats.non_regle }}, {{ stats.total - stats.regle - stats.non_regle }}],
      backgroundColor: ['#4CAF50','#FF4444','#7A8FA6'],
      borderWidth: 0,
    }]
  },
  options: { ...chartDefaults, cutout: '65%' }
});

// Graphique 4 – Barres comparatives
new Chart(document.getElementById('chartBarre'), {
  type: 'bar',
  data: {
    labels: ['Total', 'AES', 'ERES', 'Alertes', 'Réglés', 'Non réglés', 'Sans date'],
    datasets: [{
      label: 'Projets',
      data: [{{ stats.total }}, {{ stats.aes }}, {{ stats.eres }}, {{ stats.alertes }}, {{ stats.regle }}, {{ stats.non_regle }}, {{ stats.sans_date }}],
      backgroundColor: ['#243447','#00C9A7','#9B59B6','#FF4444','#4CAF50','#FF6B35','#7A8FA6'],
      borderRadius: 6,
      borderWidth: 0,
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      x: { ticks: { color: '#7A8FA6', font: { size: 11 } }, grid: { color: '#243447' } },
      y: { ticks: { color: '#7A8FA6', stepSize: 1 }, grid: { color: '#243447' }, beginAtZero: true }
    }
  }
});
</script>
{% endblock %}

{% extends "base.html" %}
{% block title %}Projets{% endblock %}
{% block content %}
<div class="stats-bar">
  <div class="stat-card"><div class="val" style="color:var(--text)">{{ stats.total }}</div><div class="lbl">📋 Total</div></div>
  <div class="stat-card"><div class="val" style="color:var(--danger)">{{ stats.alertes }}</div><div class="lbl">🔴 Alertes</div></div>
  <div class="stat-card"><div class="val" style="color:var(--warning)">{{ stats.attention }}</div><div class="lbl">🟡 Attention</div></div>
  <div class="stat-card"><div class="val" style="color:var(--success)">{{ stats.ok }}</div><div class="lbl">🟢 OK</div></div>
  <div class="stat-card"><div class="val" style="color:#00C9A7">{{ stats.aes }}</div><div class="lbl">🔵 AES</div></div>
  <div class="stat-card"><div class="val" style="color:#9B59B6">{{ stats.eres }}</div><div class="lbl">🟣 ERES</div></div>
  <div class="stat-card"><div class="val" style="color:var(--success)">{{ stats.regle }}</div><div class="lbl">💰 Réglé</div></div>
  <div class="stat-card"><div class="val" style="color:var(--danger)">{{ stats.non_regle }}</div><div class="lbl">❌ Non réglé</div></div>
</div>
<main>
  <div class="toolbar">
    <a href="{{ url_for('nouveau_projet') }}" class="btn btn-primary">➕ Nouveau projet</a>
    <form method="get" style="display:flex;gap:8px;flex:1;align-items:center;flex-wrap:wrap">
      <div class="search-box">
        <span>🔍</span>
        <input name="search" value="{{ search }}" placeholder="Promoteur, intitulé, contact...">
        <input type="hidden" name="filtre" value="{{ filtre }}">
        <input type="hidden" name="type_projet" value="{{ type_projet }}">
      </div>
      <button class="btn btn-dim btn-sm" type="submit">Chercher</button>
    </form>
  </div>
  <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;align-items:center">
    <span style="font-size:11px;color:var(--text-dim);font-weight:700">DÉLAI:</span>
    {% for val,lbl in [('tous','Tous'),('alerte','🔴 Alerte'),('ok','🟢 OK'),('sans_date','⬜ Sans date')] %}
    <a href="?filtre={{ val }}&search={{ search }}&type_projet={{ type_projet }}" class="filter-tab {{ 'active' if filtre==val }}">{{ lbl }}</a>
    {% endfor %}
    <span style="font-size:11px;color:var(--text-dim);font-weight:700;margin-left:10px">TYPE:</span>
    {% for val,lbl in [('','Tous'),('AES','🔵 AES'),('ERES','🟣 ERES')] %}
    <a href="?filtre={{ filtre }}&search={{ search }}&type_projet={{ val }}" class="filter-tab {{ 'active' if type_projet==val }}">{{ lbl }}</a>
    {% endfor %}
    <span style="font-size:11px;color:var(--text-dim);font-weight:700;margin-left:10px">COÛT:</span>
    {% for val,lbl in [('tous','Tous'),('regle','💰 Réglé'),('non_regle','❌ Non réglé')] %}
    <a href="?filtre={{ val }}&search={{ search }}&type_projet={{ type_projet }}" class="filter-tab {{ 'active' if filtre==val }}">{{ lbl }}</a>
    {% endfor %}
  </div>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>#</th><th>PROMOTEUR</th><th>CONTACT</th><th>INTITULÉ DU PROJET</th>
          <th>TYPE</th><th>DATE PASSAGE</th><th>COÛT</th><th>STATUT COÛT</th>
          <th>JOURS</th><th>STATUT DÉLAI</th><th>OBSERVATIONS</th><th>ACTIONS</th>
        </tr>
      </thead>
      <tbody>
        {% for p in projets %}
        <tr class="row-{{ p.statut }}">
          <td style="color:var(--text-dim);font-size:11px">{{ p.id }}</td>
          <td style="font-weight:600">{{ p.promoteur }}</td>
          <td style="color:var(--text-dim);font-size:12px">{{ p.contact_promoteur or '—' }}</td>
          <td style="max-width:260px" title="{{ p.intitule }}">{{ p.intitule[:65] }}{% if p.intitule|length>65 %}...{% endif %}</td>
          <td style="text-align:center">
            {% if p.type_projet|upper=='AES' %}<span class="badge" style="background:rgba(0,201,167,.15);color:#00C9A7">AES</span>
            {% elif p.type_projet|upper=='ERES' %}<span class="badge" style="background:rgba(155,89,182,.15);color:#9B59B6">ERES</span>
            {% elif p.type_projet %}<span class="badge badge-nodate">{{ p.type_projet }}</span>
            {% else %}<span style="color:var(--text-dim)">—</span>{% endif %}
          </td>
          <td style="white-space:nowrap;text-align:center">
            {% if p.date_passage %}{{ p.date_passage[8:10] }}/{{ p.date_passage[5:7] }}/{{ p.date_passage[:4] }}
            {% else %}<span style="color:var(--text-dim)">—</span>{% endif %}
          </td>
          <td style="text-align:center;font-size:12px">{{ p.cout_projet or '—' }}</td>
          <td style="text-align:center">
            {% if p.statut_cout %}
              {% if 'non' in p.statut_cout|lower %}<span class="badge badge-alerte">❌ Non réglé</span>
              {% elif 'regl' in p.statut_cout|lower %}<span class="badge badge-ok">✅ Réglé</span>
              {% else %}<span class="badge badge-nodate">{{ p.statut_cout }}</span>{% endif %}
            {% else %}<span style="color:var(--text-dim)">—</span>{% endif %}
          </td>
          <td style="text-align:center;font-weight:700;color:{% if p.statut=='alerte' %}var(--danger){% elif p.statut=='warning' %}var(--warning){% elif p.statut=='ok' %}var(--success){% else %}var(--text-dim){% endif %}">
            {% if p.jours is not none %}{{ p.jours }} j{% else %}—{% endif %}
          </td>
          <td><span class="badge badge-{{ p.statut }}">
            {% if p.statut=='alerte' %}🔴 ALERTE{% elif p.statut=='warning' %}🟡 ATTENTION{% elif p.statut=='ok' %}🟢 OK{% else %}⬜ Sans date{% endif %}
          </span></td>
          <td style="font-size:11px;color:var(--text-dim);max-width:130px" title="{{ p.observations }}">
            {{ (p.observations or '')[:35] }}{% if p.observations and p.observations|length>35 %}...{% endif %}
          </td>
          <td>
            <div style="display:flex;gap:4px">
              <a href="{{ url_for('modifier_projet', pid=p.id) }}" class="btn btn-warning btn-sm">✏️</a>
              <form method="post" action="{{ url_for('supprimer_projet', pid=p.id) }}" onsubmit="return confirm('Supprimer ?')">
                <button class="btn btn-danger btn-sm" type="submit">🗑️</button>
              </form>
            </div>
          </td>
        </tr>
        {% else %}
        <tr><td colspan="12" style="text-align:center;padding:40px;color:var(--text-dim)">Aucun projet trouvé.</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  <div style="margin-top:8px;font-size:12px;color:var(--text-dim)">{{ projets|length }} projet(s) affiché(s)</div>
</main>
{% endblock %}

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
