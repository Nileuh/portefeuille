"""
Configuration centralisée pour l'application de portefeuille.
Modifiez ce fichier pour ajuster les paramètres selon vos besoins.
"""

# ============================================
# CHEMINS DES FICHIERS
# ============================================

HISTORY_FILE = 'portfolio_history.csv'
SYMBOLES_DEVISES_FILE = 'symboles_devises.csv'
ETF_ALLOCATIONS_FILE = 'etf_allocations.csv'
ETF_ALLOCATIONS_GEO_FILE = 'etf_allocations_geo.csv'


# ============================================
# ETF CANADIENS
# ============================================
# Liste des ETF canadiens qui nécessitent le suffixe .TO pour yfinance
# Ajoutez ici tout nouvel ETF canadien que vous utilisez
ETF_CANADIENS = [
    'VFV.TO',      # Vanguard S&P 500 Index ETF
    'ZCN.TO',      # BMO S&P TSX Capped Composite Index ETF
    'ZEM.TO',      # BMO MSCI Emerging Markets Index
    'ZEA.TO',      # BMO MSCI EAFE Index ETF
    'XIC.TO',      # iShares Core S&P/TSX Capped Composite Index ETF
    'VCN.TO',      # Vanguard FTSE Canada All Cap Index ETF
    'XQQ.TO',      # iShares NASDAQ 100 Index ETF (CAD-Hedged)
    'ZNQ.TO',      # BMO NASDAQ 100 Equity Index ETF
    'XEQT.TO',     # iShares Core Equity ETF Portfolio
    'VEQT.TO',     # Vanguard All-Equity ETF Portfolio
    'VBAL.TO',     # Vanguard Balanced ETF Portfolio
    'ZBAL.TO',     # BMO Balanced ETF
    'ZSP.TO',      # BMO S&P 500 Index ETF
]


# ============================================
# ALLOCATION GÉOGRAPHIQUE CIBLE
# ============================================
# Définissez votre allocation géographique cible en pourcentage
# Le total devrait faire 100%
TARGET_ALLOCATION_GEO = {
    'USA': 55.0,
    'Canada': 20.0,
    'Marchés Développés (ex-US)': 15.0,
    'Marchés Émergents': 10.0
}


# ============================================
# MAPPING DES PAYS VERS LES ZONES GÉOGRAPHIQUES
# ============================================
# Ce mapping est utilisé pour grouper les pays individuels en zones géographiques
# Ajoutez ici tout nouveau pays que vous souhaitez classer
ZONE_MAPPING = {
    # USA
    'USA': 'USA',
    'United States': 'USA',
    
    # Canada
    'Canada': 'Canada',
    
    # Marchés Émergents
    'China': 'Marchés Émergents',
    'Taiwan': 'Marchés Émergents',
    'India': 'Marchés Émergents',
    'South Korea': 'Marchés Émergents',
    'Brazil': 'Marchés Émergents',
    'South Africa': 'Marchés Émergents',
    'Saudi Arabia': 'Marchés Émergents',
    'Mexico': 'Marchés Émergents',
    'Indonesia': 'Marchés Émergents',
    'United Arab Emirates': 'Marchés Émergents',
    'Poland': 'Marchés Émergents',
    'Thailand': 'Marchés Émergents',
    'Malaysia': 'Marchés Émergents',
    'Chile': 'Marchés Émergents',
    'Turkey': 'Marchés Émergents',
    'Philippines': 'Marchés Émergents',
    
    # Marchés Développés (ex-US)
    'Japan': 'Marchés Développés (ex-US)',
    'United Kingdom': 'Marchés Développés (ex-US)',
    'Switzerland': 'Marchés Développés (ex-US)',
    'Germany': 'Marchés Développés (ex-US)',
    'France': 'Marchés Développés (ex-US)',
    'Netherlands': 'Marchés Développés (ex-US)',
    'Australia': 'Marchés Développés (ex-US)',
    'Spain': 'Marchés Développés (ex-US)',
    'Sweden': 'Marchés Développés (ex-US)',
    'Italy': 'Marchés Développés (ex-US)',
    'Denmark': 'Marchés Développés (ex-US)',
    'Belgium': 'Marchés Développés (ex-US)',
    'Norway': 'Marchés Développés (ex-US)',
    'Finland': 'Marchés Développés (ex-US)',
    'Ireland': 'Marchés Développés (ex-US)',
    'Austria': 'Marchés Développés (ex-US)',
    'New Zealand': 'Marchés Développés (ex-US)',
    'Singapore': 'Marchés Développés (ex-US)',
    'Hong Kong': 'Marchés Développés (ex-US)',
    'Other': 'Marchés Développés (ex-US)',
}


# ============================================
# PARAMÈTRES DE CACHE
# ============================================
# Durée de vie du cache en secondes (3600 = 1 heure)
CACHE_TTL_SECONDS = 3600

# Taille maximale du cache LRU pour les fonctions
LRU_CACHE_MAXSIZE = 500


# ============================================
# TAUX SANS RISQUE
# ============================================
# Utilisé pour le calcul du ratio de Sharpe
# Valeur par défaut: 2% (0.02)
RISK_FREE_RATE = 0.02


# ============================================
# PÉRIODES D'ANALYSE DISPONIBLES
# ============================================
# Périodes disponibles dans le sélecteur de performance (en années)
PERFORMANCE_PERIODS = [1, 3, 5]


# ============================================
# BENCHMARK PAR DÉFAUT
# ============================================
# Symbole du benchmark utilisé par défaut pour la comparaison de performance
DEFAULT_BENCHMARK = 'VFV.TO'


# ============================================
# NORMALISATION DES NOMS DE PAYS
# ============================================
# Pour standardiser les différentes variantes de noms de pays
COUNTRY_NORMALIZATION = {
    'United States': 'USA',
    'United States of America': 'USA',
    'US': 'USA',
    'United Kingdom': 'UK',
    'Great Britain': 'UK',
}
