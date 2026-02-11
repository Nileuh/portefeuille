# install 
python -m pip install streamlit pandas yfinance plotly

# execute
streamlit run app.py

# 📂 Comment remplir les fichiers CSV

L'application utilise trois fichiers CSV principaux pour la configuration et l'analyse du portefeuille. Voici comment les remplir :

#### 1. `symboles_devises.csv`
- **But :** Référence des titres détenus, leur devise, secteur et pays.
- **Colonnes principales :**
    - `Symbole` : Le ticker (ex: AAPL, VFV)
    - `Nom` : Nom complet de l'actif (optionnel)
    - `Type` : Type d'actif (ex: Action US, ETF)
    - `Devise` : Devise de cotation (USD, CAD, etc.)
    - `Marche` : Marché de cotation (ex: NASDAQ, TSX)
    - `Secteur` : Secteur d'activité (ex: Technology, Financial Services)
    - `Pays` : Pays principal de l'entreprise ou de l'ETF
- **Conseil :**
    - Ajoutez chaque nouveau titre détenu dans ce fichier.
    - Complétez manuellement les secteurs/pays si besoin, ou laissez vide pour une détection automatique.

#### 2. `etf_allocations.csv`
- **But :** Répartition sectorielle de chaque ETF (en %).
- **Colonnes principales :**
    - `Symbole` : Le ticker de l'ETF (ex: VFV)
    - `Secteur` : Secteur (ex: Technology, Health Care)
    - `Allocation_Pct` : Pourcentage d'allocation à ce secteur (la somme doit faire 100% par ETF)
- **Conseil :**
    - Utilisez les rapports officiels des émetteurs d'ETF pour remplir les secteurs et leurs poids.
    - Chaque ligne = 1 secteur pour 1 ETF.

#### 3. `etf_allocations_geo.csv`
- **But :** Répartition géographique de chaque ETF (en %).
- **Colonnes principales :**
    - `Symbole` : Le ticker de l'ETF (ex: VFV)
    - `Pays` : Pays ou zone géographique (ex: USA, Canada, Japan, Other)
    - `Allocation_Pct` : Pourcentage d'allocation à ce pays/zone (la somme doit faire 100% par ETF)
- **Conseil :**
    - Utilisez les rapports officiels des émetteurs d'ETF pour remplir les pays et leurs poids.
    - Chaque ligne = 1 pays pour 1 ETF.

**Remarque :**
Pour chaque nouvel ETF ou titre, pensez à compléter ces fichiers pour garantir une analyse correcte et éviter les avertissements dans l'application.

# Guide de Configuration

Ce fichier explique comment utiliser le fichier `config.py` pour personnaliser votre application de portefeuille.

## 📋 Structure de Configuration

Les paramètres configurables de l'application sont dans le fichier **`config.py`**. 
Les ETF doivent être référencés dans les fichiers **`etf_allocations_geo.csv`** et **`etf_allocations.csv`** ainsi que dans **`symboles_devises.csv`** si vous les détenez.

## 🔧 Paramètres Disponibles

### 1. ETF Canadiens (`ETF_CANADIENS`)

**Quoi :** Liste des ETF canadiens nécessitant le suffixe `.TO` pour yfinance.

**Quand modifier :** Si vous ajoutez un nouvel ETF canadien à votre portefeuille qui n'est pas dans la liste.

**Exemple :**
```python
ETF_CANADIENS = [
    'VFV',      # Vanguard S&P 500 Index ETF
    'ZCN',      # BMO S&P TSX Capped Composite Index ETF
    'VOTRE_ETF', # Ajoutez le vôtre ici
]
```


## 📝 Cheminement pour Ajouter un Nouvel ETF

1. Ouvrez `config.py`
2. Trouvez la section `ETF_CANADIENS`
3. Ajoutez votre symbole dans la liste :
   ```python
   'VOTRE_SYMBOLE',  # Description de l'ETF
   ```
4. Ouvrez `etf_allocations_geo.csv` et compléter la répartition géographique
5. Ouvrez `etf_allocations.csv` et compléter la répartition sectorielle
6. Rechargez l'application Streamlit (Ctrl+R dans le navigateur)

---

### 2. Allocation Géographique Cible (`TARGET_ALLOCATION_GEO`)

**Quoi :** Votre allocation géographique idéale en pourcentage (doit totaliser 100%).

**Quand modifier :** Si vous souhaitez changer votre stratégie d'allocation géographique.

**Exemple :**
```python
TARGET_ALLOCATION_GEO = {
    'USA': 55.0,                          # 55% aux États-Unis
    'Canada': 20.0,                       # 20% au Canada
    'Marchés Développés (ex-US)': 15.0,  # 15% marchés développés
    'Marchés Émergents': 10.0             # 10% marchés émergents
}
```

---

### 3. Mapping des Pays vers les Zones (`ZONE_MAPPING`)

**Quoi :** Associe chaque pays à une zone géographique (USA, Canada, Marchés Développés, Marchés Émergents).

**Quand modifier :** Si un pays n'est pas reconnu ou si vous voulez le reclasser dans une autre zone.

**Exemple :**
```python
ZONE_MAPPING = {
    'France': 'Marchés Développés (ex-US)',
    'Vietnam': 'Marchés Émergents',  # Ajoutez un nouveau pays
}
```

---

### 4. Normalisation des Noms de Pays (`COUNTRY_NORMALIZATION`)

**Quoi :** Standardise les différentes variantes de noms de pays (ex: "United States" → "USA").

**Quand modifier :** Si vos données contiennent des variations de noms de pays non reconnues.

**Exemple :**
```python
COUNTRY_NORMALIZATION = {
    'United States': 'USA',
    'États-Unis': 'USA',  # Ajoutez une variante française
}
```

---



### 6. Benchmark par Défaut (`DEFAULT_BENCHMARK`)

**Quoi :** Le symbole utilisé par défaut pour comparer votre performance.

**Quand modifier :** Si vous préférez un autre indice de référence.

**Exemple :**
```python
DEFAULT_BENCHMARK = '^GSPTSE'  # TSX Composite au lieu de VFV.TO
```

---

### 7. Taux Sans Risque (`RISK_FREE_RATE`)

**Quoi :** Taux utilisé pour calculer le ratio de Sharpe (par défaut 2% = 0.02).

**Quand modifier :** Si vous voulez utiliser un taux différent (ex: taux des obligations du gouvernement).

**Exemple :**
```python
RISK_FREE_RATE = 0.03  # 3%
```

---

### 8. Paramètres de Cache

**TTL du Cache (`CACHE_TTL_SECONDS`):** Durée de vie du cache (3600 = 1 heure)
**Taille du Cache (`LRU_CACHE_MAXSIZE`):** Nombre maximum d'éléments en cache (500)

**Quand modifier :** Si vous voulez que les données soient actualisées plus/moins souvent.

---

