import streamlit as st
import pandas as pd
import os
import yfinance as yf
from functools import lru_cache
import datetime as dt
from datetime import datetime
import numpy as np

# === CONFIGURATION ===
HISTORY_FILE = 'portfolio_history.csv'
SYMBOLES_DEVISES_FILE = 'symboles_devises.csv'
ETF_ALLOCATIONS_FILE = 'etf_allocations.csv'
ETF_ALLOCATIONS_GEO_FILE = 'etf_allocations_geo.csv'

# Charger le mapping des devises
_symboles_devises_cache = None
_etf_allocations_cache = None
_etf_allocations_geo_cache = None

def load_symboles_devises():
    """Charge le fichier de référence des devises des symboles."""
    global _symboles_devises_cache
    if _symboles_devises_cache is not None:
        return _symboles_devises_cache
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, SYMBOLES_DEVISES_FILE)
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # Retourner un dictionnaire avec devise, secteur ET pays
        _symboles_devises_cache = {
            'devise': dict(zip(df['Symbole'].str.upper(), df['Devise'].str.upper())),
            'secteur': dict(zip(df['Symbole'].str.upper(), df['Secteur'])) if 'Secteur' in df.columns else {},
            'pays': dict(zip(df['Symbole'].str.upper(), df['Pays'])) if 'Pays' in df.columns else {}
        }
        return _symboles_devises_cache
    return {'devise': {}, 'secteur': {}, 'pays': {}}


def update_symbole_secteur(symbol: str, secteur: str):
    """Met à jour le secteur d'un symbole dans le fichier CSV."""
    global _symboles_devises_cache
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, SYMBOLES_DEVISES_FILE)
    
    if not os.path.exists(file_path):
        return
    
    try:
        df = pd.read_csv(file_path)
        symbol_upper = symbol.upper().strip()
        
        # Trouver l'index du symbole
        mask = df['Symbole'].str.upper() == symbol_upper
        if mask.any():
            df.loc[mask, 'Secteur'] = secteur
            df.to_csv(file_path, index=False)
            
            # Mettre à jour le cache
            if _symboles_devises_cache is not None:
                _symboles_devises_cache['secteur'][symbol_upper] = secteur
    except Exception as e:
        pass  # Silencieux pour ne pas bloquer l'application


def update_symbole_pays(symbol: str, pays: str):
    """Met à jour le pays d'un symbole dans le fichier CSV."""
    global _symboles_devises_cache
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, SYMBOLES_DEVISES_FILE)
    
    if not os.path.exists(file_path):
        return
    
    try:
        df = pd.read_csv(file_path)
        symbol_upper = symbol.upper().strip()
        
        # Trouver l'index du symbole
        mask = df['Symbole'].str.upper() == symbol_upper
        if mask.any():
            df.loc[mask, 'Pays'] = pays
            df.to_csv(file_path, index=False)
            
            # Mettre à jour le cache
            if _symboles_devises_cache is not None:
                _symboles_devises_cache['pays'][symbol_upper] = pays
    except Exception as e:
        pass  # Silencieux pour ne pas bloquer l'application

def update_symbole_pays(symbol: str, pays: str):
    """Met à jour le pays d'un symbole dans le fichier CSV."""
    global _symboles_devises_cache
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, SYMBOLES_DEVISES_FILE)
    
    if not os.path.exists(file_path):
        return
    
    try:
        df = pd.read_csv(file_path)
        symbol_upper = symbol.upper().strip()
        
        # Trouver l'index du symbole
        mask = df['Symbole'].str.upper() == symbol_upper
        if mask.any():
            df.loc[mask, 'Pays'] = pays
            df.to_csv(file_path, index=False)
            
            # Mettre à jour le cache
            if _symboles_devises_cache is not None:
                _symboles_devises_cache['pays'][symbol_upper] = pays
    except Exception as e:
        pass  # Silencieux pour ne pas bloquer l'application

def load_etf_allocations():
    """Charge les allocations sectorielles des ETF depuis le fichier CSV."""
    global _etf_allocations_cache
    if _etf_allocations_cache is not None:
        return _etf_allocations_cache
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, ETF_ALLOCATIONS_FILE)
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # Créer un dictionnaire structuré comme ETF_SECTORS
        etf_dict = {}
        for symbol in df['Symbole'].unique():
            symbol_data = df[df['Symbole'] == symbol]
            allocations = dict(zip(symbol_data['Secteur'], symbol_data['Allocation_Pct']))
            etf_dict[symbol] = {
                'allocation': allocations,
                'sector': 'ETF'  # Secteur générique pour les ETF
            }
        _etf_allocations_cache = etf_dict
        return _etf_allocations_cache
    return {}


def load_etf_allocations_geo():
    """Charge les allocations géographiques des ETF depuis le fichier CSV."""
    global _etf_allocations_geo_cache
    if _etf_allocations_geo_cache is not None:
        return _etf_allocations_geo_cache
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, ETF_ALLOCATIONS_GEO_FILE)
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # Créer un dictionnaire structuré comme ETF_GEOGRAPHIC
        etf_geo_dict = {}
        for symbol in df['Symbole'].unique():
            symbol_data = df[df['Symbole'] == symbol]
            allocations = dict(zip(symbol_data['Pays'], symbol_data['Allocation_Pct']))
            etf_geo_dict[symbol] = {
                'allocation': allocations
            }
        _etf_allocations_geo_cache = etf_geo_dict
        return _etf_allocations_geo_cache
    return {}


def auto_complete_missing_sectors():
    """Remplit automatiquement tous les secteurs manquants dans le fichier CSV."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, SYMBOLES_DEVISES_FILE)
    
    if not os.path.exists(file_path):
        return 0, 0
    
    df = pd.read_csv(file_path)
    missing_count = df['Secteur'].isna().sum()
    updated_count = 0
    
    if missing_count == 0:
        return 0, 0
    
    # Parcourir les lignes avec secteur manquant
    for idx, row in df[df['Secteur'].isna()].iterrows():
        symbol = row['Symbole']
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if 'sector' in info and info['sector']:
                df.at[idx, 'Secteur'] = info['sector']
                updated_count += 1
            elif 'category' in info and info['category']:
                df.at[idx, 'Secteur'] = info['category']
                updated_count += 1
        except Exception:
            continue
    
    # Sauvegarder le fichier
    if updated_count > 0:
        df.to_csv(file_path, index=False)
        # Invalider le cache
        global _symboles_devises_cache
        _symboles_devises_cache = None
    
    return missing_count, updated_count


def auto_complete_missing_countries():
    """Remplit automatiquement tous les pays manquants dans le fichier CSV."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, SYMBOLES_DEVISES_FILE)
    
    if not os.path.exists(file_path):
        return 0, 0
    
    df = pd.read_csv(file_path)
    
    # Vérifier si la colonne Pays existe
    if 'Pays' not in df.columns:
        df['Pays'] = ''
    
    missing_count = (df['Pays'].isna() | (df['Pays'] == '')).sum()
    updated_count = 0
    
    if missing_count == 0:
        return 0, 0
    
    # Parcourir les lignes avec pays manquant
    for idx, row in df[df['Pays'].isna() | (df['Pays'] == '')].iterrows():
        symbol = row['Symbole']
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if 'country' in info and info['country']:
                df.at[idx, 'Pays'] = info['country']
                updated_count += 1
        except Exception:
            continue
    
    # Sauvegarder le fichier
    if updated_count > 0:
        df.to_csv(file_path, index=False)
        # Invalider le cache
        global _symboles_devises_cache
        _symboles_devises_cache = None
    
    return missing_count, updated_count

# === TARGET ALLOCATION ===
TARGET_ALLOCATION_GEO = {
    'USA': 55.0,
    'Canada': 20.0,
    'Marchés Développés (ex-US)': 15.0,
    'Marchés Émergents': 10.0
}


# ============================================
# DONNÉES EN CACHE (Session State)
# ============================================

@st.cache_resource
def get_cached_portfolio_data():
    """Récupère et cache les données du portefeuille pour la session."""
    return {
        'df_p': None,
        'df_geo': None,
        'df_consolidated': None,
        'total_v': None,
        'usd_to_cad': None
    }


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

@st.cache_data(ttl=3600)
def get_usd_to_cad_rate() -> float:
    """Récupère le taux USD/CAD en temps réel."""
    try:
        ticker = yf.Ticker('CADUSD=X')
        hist = ticker.history(period='1d')
        if not hist.empty:
            cad_to_usd = hist['Close'].iloc[-1]
            return 1 / cad_to_usd
    except Exception:
        pass
    return None


@lru_cache(maxsize=500)
def get_sector(symbol: str) -> str:
    """Récupère le secteur d'une action/ETF."""
    symbol_upper = symbol.upper().strip()
    
    # Vérifier d'abord dans les allocations ETF
    etf_allocations = load_etf_allocations()
    if symbol_upper in etf_allocations:
        return etf_allocations[symbol_upper]['sector']
    
    # Vérifier dans le fichier de référence
    symboles_data = load_symboles_devises()
    if symbol_upper in symboles_data['secteur']:
        secteur = symboles_data['secteur'][symbol_upper]
        # Vérifier que le secteur n'est pas NaN, None, ou une chaîne vide
        if secteur and str(secteur) != 'nan' and secteur != 'ETF':
            return secteur
    
    # Sinon, interroger yfinance et sauvegarder le résultat
    try:
        ticker = yf.Ticker(symbol_upper)
        info = ticker.info
        
        if 'sector' in info and info['sector']:
            secteur_trouve = info['sector']
            # Sauvegarder dans le CSV pour les prochaines fois
            update_symbole_secteur(symbol, secteur_trouve)
            return secteur_trouve
        
        if 'category' in info and info['category']:
            category = info['category'].lower()
            if 'equity' in category:
                if 'us' in category:
                    return "Équités US"
                elif 'canada' in category or 'tsx' in category:
                    return "Équités Canada"
                elif 'emerging' in category:
                    return "Marchés Émergents"
                elif 'dividend' in category:
                    return "Dividendes"
                else:
                    return "Équités Diversifiées"
            elif 'fixed income' in category or 'bond' in category:
                return "Revenu Fixe"
            else:
                return info['category']
        return None
    except Exception:
        return None


@lru_cache(maxsize=500)
def get_valuation_metrics(symbol: str):
    """Récupère P/E et Forward P/E pour une action."""
    try:
        ticker = yf.Ticker(symbol.upper().strip())
        info = ticker.info
        pe = info.get('trailingPE', None)
        forward_pe = info.get('forwardPE', None)
        return {
            'pe': round(pe, 2) if pe else None,
            'forward_pe': round(forward_pe, 2) if forward_pe else None
        }
    except Exception:
        return {'pe': None, 'forward_pe': None}


@lru_cache(maxsize=500)
def get_current_price(symbol: str, actif_name: str = None):
    """Récupère le prix actuel d'un symbole via yfinance.
    
    Args:
        symbol: Le symbole boursier
        actif_name: Le nom de l'actif (optionnel, utilisé pour détecter CDR Hedged)
    """
    try:
        symbol_upper = symbol.upper().strip()
        
        # Si c'est un CDR Hedged sans suffixe, ajouter .TO
        if actif_name and 'CDR' in actif_name.upper() and 'HEDGED' in actif_name.upper():
            if '.TO' not in symbol_upper and '.NE' not in symbol_upper:
                symbol_upper = symbol_upper + '.TO'
        
        # Si c'est un ETF canadien connu sans suffixe, ajouter .TO
        # Charger les ETF connus
        etf_allocations = load_etf_allocations()
        etf_canadiens = ['VFV', 'ZCN', 'ZEM', 'ZEA', 'XIC', 'VCN', 'XQQ', 'ZNQ', 'XEQT', 'VEQT', 'VBAL', 'ZBAL', 'ZSP']
        
        if symbol_upper in etf_allocations or symbol_upper in etf_canadiens:
            if '.' not in symbol_upper:  # Pas de suffixe de bourse
                symbol_upper = symbol_upper + '.TO'
        
        ticker = yf.Ticker(symbol_upper)
        # Essayer d'obtenir le prix actuel
        current_price = ticker.info.get('currentPrice')
        if current_price:
            return current_price
        
        # Fallback: dernier prix de clôture
        hist = ticker.history(period='1d')
        if not hist.empty:
            return hist['Close'].iloc[-1]
        
        return None
    except Exception:
        return None


@lru_cache(maxsize=500)
def get_country(symbol: str) -> str:
    """Récupère le pays d'une action."""
    symbol_upper = symbol.upper().strip()
    
    # Vérifier d'abord dans le fichier de référence
    symboles_data = load_symboles_devises()
    if symbol_upper in symboles_data['pays']:
        pays = symboles_data['pays'][symbol_upper]
        # Vérifier que le pays n'est pas NaN, None, ou une chaîne vide
        if pays and str(pays) != 'nan' and pays.strip():
            return pays
    
    # Sinon, interroger yfinance et sauvegarder le résultat
    try:
        # Ajouter .TO si c'est probablement un ETF canadien
        symbol_to_query = symbol_upper
        etf_allocations = load_etf_allocations()
        etf_canadiens = ['VFV', 'ZCN', 'ZEM', 'ZEA', 'XIC', 'VCN', 'XQQ', 'ZNQ', 'XEQT', 'VEQT', 'VBAL', 'ZBAL', 'ZSP']
        
        if (symbol_upper in etf_allocations or symbol_upper in etf_canadiens) and '.' not in symbol_upper:
            symbol_to_query = symbol_upper + '.TO'
        
        ticker = yf.Ticker(symbol_to_query)
        info = ticker.info
        
        if 'country' in info and info['country']:
            pays_trouve = info['country']
            # Sauvegarder dans le CSV pour les prochaines fois
            update_symbole_pays(symbol, pays_trouve)
            return pays_trouve
    except Exception:
        pass
    
    return None


def get_currency_for_symbol(symbol: str, actif_name: str = None):
    """Détermine la devise d'un symbole.
    
    Args:
        symbol: Le symbole boursier
        actif_name: Le nom de l'actif (optionnel, utilisé pour détecter CDR Hedged)
    """
    symbol_upper = symbol.upper().strip()
    
    # Si le nom contient "CDR" et "Hedged", c'est en CAD
    if actif_name and 'CDR' in actif_name.upper() and 'HEDGED' in actif_name.upper():
        return 'CAD'
    
    # Vérifier d'abord dans le fichier de référence
    symboles_data = load_symboles_devises()
    if symbol_upper in symboles_data['devise']:
        return symboles_data['devise'][symbol_upper]
    
    # Si c'est un ETF canadien connu, c'est en CAD
    etf_canadiens = ['VFV', 'ZCN', 'ZEM', 'ZEA', 'XIC', 'VCN', 'XQQ', 'ZNQ', 'XEQT', 'VEQT', 'VBAL', 'ZBAL', 'ZSP']
    if symbol_upper in etf_canadiens:
        return 'CAD'
    
    # Sinon, utiliser yfinance
    try:
        # Ajouter .TO si c'est probablement un ETF canadien
        symbol_to_query = symbol_upper
        etf_allocations = load_etf_allocations()
        if symbol_upper in etf_allocations and '.' not in symbol_upper:
            symbol_to_query = symbol_upper + '.TO'
        
        ticker = yf.Ticker(symbol_to_query)
        currency = ticker.info.get('currency', 'USD')
        return currency.upper()
    except Exception:
        # Par défaut, si le symbole se termine par .TO ou .NE, c'est CAD
        if '.TO' in symbol_upper or '.NE' in symbol_upper:
            return 'CAD'
        return 'USD'


# ============================================
# CHARGEMENT DES DONNÉES DE PORTEFEUILLE
# ============================================

def load_portfolio(use_realtime_prices=True):
    """Charge les données du portefeuille depuis le dossier /data.
    
    Args:
        use_realtime_prices: Si True, utilise les prix actuels de yfinance.
                            Si False, utilise les valeurs des CSV.
    """
    all_data = []
    geo_data = []
    
    usd_to_cad_rate = get_usd_to_cad_rate()
    if not usd_to_cad_rate:
        st.error("Impossible de récupérer le taux USD/CAD.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_path, "data")
    
    if not os.path.exists(data_dir):
        st.error(f"Dossier introuvable : {data_dir}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    for file in os.listdir(data_dir):
        if file.endswith(".csv"):
            path = os.path.join(data_dir, file)
            try:
                df = pd.read_csv(path, encoding='utf-8-sig')
            except:
                df = pd.read_csv(path, encoding='latin-1')
            
            df.columns = [str(c).strip().lower() for c in df.columns]
            cols = df.columns.tolist()
            
            # LOGIQUE WEALTHSIMPLE
            if 'name' in cols and 'number of shares' in cols:
                devise_col = next((c for c in cols if 'devise' in c or 'currency' in c), None)
                temp = pd.DataFrame({
                    'Actif': df['name'],
                    'Quantité': pd.to_numeric(df['number of shares'], errors='coerce'),
                    'Symbole': df.get('symbole', df.get('symbol', '')),
                    'Secteur': df['sector'].replace('-', 'À déterminer').fillna('À déterminer'),
                    'Valeur_Finale': pd.to_numeric(df['base market value'], errors='coerce'),
                    'Devise': df[devise_col] if devise_col else 'CAD'
                })
                all_data.append(temp.dropna(subset=['Actif']))
            
            # LOGIQUE ALTERNATIVE
            elif 'symbole' in cols or 'symbol' in cols:
                t_col = next((c for c in cols if c in ['symbole', 'symbol', 'ticker']), None)
                q_col = next((c for c in cols if 'quant' in c or 'qte' in c), None)
                devise_marchande_col = next((c for c in cols if 'devise de la valeur marchande' in c), None)
                v_marchande_col = next((c for c in cols if 'valeur marchande' in c), None)
                v_comptable_cad_col = next((c for c in cols if 'valeur comptable (cad)' in c), None)
                s_col = next((c for c in cols if 'secteur' in c or 'sector' in c), None)
                n_col = next((c for c in cols if c == 'nom' or c == 'name'), None)
                
                if t_col and q_col:
                    valeurs_finales = []
                    for idx, row in df.iterrows():
                        if v_marchande_col and devise_marchande_col:
                            devise_marche = str(row[devise_marchande_col]).strip().upper()
                            valeur_marche = pd.to_numeric(row[v_marchande_col], errors='coerce')
                            if devise_marche == 'CAD':
                                valeurs_finales.append(valeur_marche)
                            else:
                                valeur_convertie = valeur_marche * usd_to_cad_rate if valeur_marche else 0
                                valeurs_finales.append(valeur_convertie)
                        elif v_comptable_cad_col:
                            valeurs_finales.append(pd.to_numeric(row[v_comptable_cad_col], errors='coerce'))
                        else:
                            valeurs_finales.append(0)
                    
                    temp = pd.DataFrame({
                        'Actif': df[n_col].fillna(df[t_col]) if n_col else df[t_col],
                        'Quantité': pd.to_numeric(df[q_col], errors='coerce'),
                        'Symbole': df[t_col],
                        'Secteur': df[s_col] if s_col else 'À déterminer',
                        'Valeur_Finale': valeurs_finales,
                        'Devise': 'CAD'
                    })
                    all_data.append(temp.dropna(subset=['Actif']))
    
    if not all_data:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    df_portfolio = pd.concat(all_data, ignore_index=True)
    
    usd_mask = df_portfolio['Devise'] == 'USD'
    df_portfolio.loc[usd_mask, 'Valeur_Finale'] = df_portfolio.loc[usd_mask, 'Valeur_Finale'] * usd_to_cad_rate
    df_portfolio['Devise'] = 'CAD'
    
    # Grouper par Symbole ET Actif pour distinguer les versions CDR des versions US
    df_portfolio = df_portfolio.groupby(['Symbole', 'Actif'], as_index=False).agg({
        'Quantité': 'sum',
        'Secteur': 'first',
        'Valeur_Finale': 'sum',
        'Devise': 'first'
    })
    
    # Recalculer les valeurs avec prix temps réel si demandé
    if use_realtime_prices:
        with st.spinner("Récupération des prix en temps réel..."):
            for idx, row in df_portfolio.iterrows():
                symbol = str(row['Symbole']).upper().strip()
                quantite = row['Quantité']
                actif_name = str(row['Actif'])
                
                # Récupérer le prix actuel (en passant le nom pour détecter CDR)
                current_price = get_current_price(symbol, actif_name)
                if current_price:
                    # Déterminer la devise (en utilisant le nom de l'actif)
                    currency = get_currency_for_symbol(symbol, actif_name)
                    
                    # Calculer la valeur
                    valeur = quantite * current_price
                    
                    # Convertir en CAD si nécessaire
                    if currency == 'USD':
                        valeur = valeur * usd_to_cad_rate
                    
                    df_portfolio.at[idx, 'Valeur_Finale'] = valeur
    
    df_consolidated = df_portfolio.copy()
    
    with st.spinner("Traitement des données..."):
        expanded_data = []
        geo_data = []
        
        etf_allocations = load_etf_allocations()
        etf_allocations_geo = load_etf_allocations_geo()
        
        for _, row in df_portfolio.iterrows():
            symbol = str(row['Symbole']).upper().strip()
            valeur_etf = row['Valeur_Finale']
            
            if symbol in etf_allocations:
                etf_info = etf_allocations[symbol]
                for secteur, allocation in etf_info['allocation'].items():
                    valeur_secteur = valeur_etf * (allocation / 100)
                    expanded_data.append({
                        'Actif': f"{row['Actif']} - {secteur}",
                        'Quantité': row['Quantité'],
                        'Symbole': symbol,
                        'Secteur': secteur,
                        'Allocation': f"{allocation:.2f}%",
                        'Valeur_Finale': valeur_secteur
                    })
                
                if symbol in etf_allocations_geo:
                    geo_info = etf_allocations_geo[symbol]
                    for pays, allocation_geo in geo_info['allocation'].items():
                        valeur_geo = valeur_etf * (allocation_geo / 100)
                        geo_data.append({
                            'Pays': pays,
                            'Allocation': f"{allocation_geo:.2f}%",
                            'Valeur_Finale': valeur_geo
                        })
            else:
                sector = get_sector(symbol) if symbol else None
                if not sector:
                    sector = "Catégorie Inconnue"
                
                expanded_data.append({
                    'Actif': row['Actif'],
                    'Quantité': row['Quantité'],
                    'Symbole': symbol,
                    'Secteur': sector,
                    'Allocation': '100%',
                    'Valeur_Finale': row['Valeur_Finale']
                })
                
                # Récupérer le pays pour les actions individuelles
                pays = get_country(symbol) if symbol else None
                if pays:
                    geo_data.append({
                        'Pays': pays,
                        'Allocation': '100%',
                        'Valeur_Finale': row['Valeur_Finale']
                    })
        
        df_portfolio = pd.DataFrame(expanded_data)
        df_geo = pd.DataFrame(geo_data)
    
    return df_portfolio, df_geo, df_consolidated


# ============================================
# PERFORMANCE HISTORIQUE
# ============================================

@st.cache_data(ttl=3600)
def get_price_history(symbols, start_date, end_date):
    """Récupère les historiques de prix."""
    data = yf.download(
        tickers=list(symbols),
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False
    )['Close']
    if isinstance(data, pd.Series):
        data = data.to_frame()
    return data


def build_portfolio_history(df_consolidated, benchmark_symbol="VFV.TO", start_years_ago=3):
    """Construit l'historique du portefeuille."""
    if df_consolidated.empty:
        return pd.DataFrame()
    
    symbols = df_consolidated['Symbole'].str.upper().unique().tolist()
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=365 * start_years_ago)
    
    price_data = get_price_history(symbols, start_date, end_date)
    if price_data.empty:
        return pd.DataFrame()
    
    price_data = price_data.reindex(columns=symbols)
    qty = df_consolidated.set_index('Symbole')['Quantité']
    port_value = price_data.mul(qty, axis=1).sum(axis=1)
    
    bmk_price = get_price_history([benchmark_symbol], start_date, end_date)
    if not bmk_price.empty:
        bmk_series = bmk_price.iloc[:, 0]
        common_index = port_value.index.intersection(bmk_series.index)
        port_value = port_value.loc[common_index]
        bmk_series = bmk_series.loc[common_index]
        
        port_norm = (port_value / port_value.iloc[0]) * 100
        bmk_norm = (bmk_series / bmk_series.iloc[0]) * 100
        
        hist_df = pd.DataFrame({
            'Portefeuille': port_norm,
            f'Benchmark ({benchmark_symbol})': bmk_norm
        })
    else:
        hist_df = pd.DataFrame({
            'Portefeuille': (port_value / port_value.iloc[0]) * 100
        })
    
    hist_df.index.name = "Date"
    return hist_df


def calculate_risk_metrics(hist_df, risk_free_rate=0.02):
    """Calcule les métriques de risque/rendement."""
    if hist_df.empty or 'Portefeuille' not in hist_df.columns:
        return {}
    
    returns = hist_df['Portefeuille'].pct_change().dropna()
    days = (hist_df.index[-1] - hist_df.index[0]).days
    if days == 0:
        return {}
    
    annual_return = (hist_df['Portefeuille'].iloc[-1] / hist_df['Portefeuille'].iloc[0]) ** (365/days) - 1
    volatility = returns.std() * np.sqrt(252)
    sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
    
    cum_max = hist_df['Portefeuille'].expanding().max()
    drawdown = (hist_df['Portefeuille'] - cum_max) / cum_max
    max_drawdown = drawdown.min()
    
    return {
        'annual_return': annual_return * 100,
        'volatility': volatility * 100,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown * 100
    }


# ============================================
# CONCENTRATION ET ALLOCATION
# ============================================

def calculate_concentration(df_consolidated):
    """Calcule les métriques de concentration."""
    if df_consolidated.empty:
        return {}
    
    total = df_consolidated['Valeur_Finale'].sum()
    df_consolidated['Poids_%'] = (df_consolidated['Valeur_Finale'] / total * 100).round(2)
    
    top5_pct = df_consolidated.nlargest(5, 'Valeur_Finale')['Poids_%'].sum()
    hhi = (df_consolidated['Poids_%'] ** 2).sum()
    
    return {
        'top5_pct': top5_pct,
        'hhi': hhi,
        'df_weighted': df_consolidated
    }


def compare_target_allocation(df_geo, target_alloc):
    """Compare allocation actuelle vs cible."""
    if df_geo.empty:
        return pd.DataFrame()
    
    total = df_geo['Valeur_Finale'].sum()
    actual = df_geo.groupby('Pays')['Valeur_Finale'].sum() / total * 100
    
    zone_mapping = {
        'USA': 'USA',
        'Canada': 'Canada',
        'China': 'Marchés Émergents', 'Taiwan': 'Marchés Émergents', 'India': 'Marchés Émergents',
        'South Korea': 'Marchés Émergents', 'Brazil': 'Marchés Émergents', 'South Africa': 'Marchés Émergents',
        'Saudi Arabia': 'Marchés Émergents', 'Mexico': 'Marchés Émergents', 'Indonesia': 'Marchés Émergents',
        'United Arab Emirates': 'Marchés Émergents', 'Poland': 'Marchés Émergents',
        'Japan': 'Marchés Développés (ex-US)', 'United Kingdom': 'Marchés Développés (ex-US)',
        'Switzerland': 'Marchés Développés (ex-US)', 'Germany': 'Marchés Développés (ex-US)',
        'France': 'Marchés Développés (ex-US)', 'Netherlands': 'Marchés Développés (ex-US)',
        'Australia': 'Marchés Développés (ex-US)', 'Spain': 'Marchés Développés (ex-US)',
        'Sweden': 'Marchés Développés (ex-US)', 'Italy': 'Marchés Développés (ex-US)',
        'Denmark': 'Marchés Développés (ex-US)', 'Other': 'Marchés Développés (ex-US)'
    }
    
    actual_grouped = {}
    for pays, pct in actual.items():
        zone = zone_mapping.get(pays, 'Autre')
        actual_grouped[zone] = actual_grouped.get(zone, 0) + pct
    
    comparison = []
    for zone, target_pct in target_alloc.items():
        actual_pct = actual_grouped.get(zone, 0)
        ecart = actual_pct - target_pct
        comparison.append({
            'Zone': zone,
            'Cible (%)': target_pct,
            'Actuel (%)': round(actual_pct, 2),
            'Écart (%)': round(ecart, 2)
        })
    
    return pd.DataFrame(comparison)


# ============================================
# HISTORIQUE MENSUEL
# ============================================

def save_monthly_snapshot(total_value, contribution=0.0):
    """Sauvegarde le snapshot mensuel."""
    today = datetime.now()
    
    if not os.path.exists(HISTORY_FILE):
        pd.DataFrame({
            'date': [], 
            'valeur_totale_cad': [], 
            'contributions_cad': []
        }).to_csv(HISTORY_FILE, index=False)
    
    df_history = pd.read_csv(HISTORY_FILE, parse_dates=['date'])
    
    if 'contributions_cad' not in df_history.columns:
        df_history['contributions_cad'] = 0.0
    
    current_month = today.strftime('%Y-%m')
    if not any(df_history['date'].dt.strftime('%Y-%m') == current_month):
        new_row = pd.DataFrame({
            'date': [today], 
            'valeur_totale_cad': [total_value],
            'contributions_cad': [contribution]
        })
        df_history = pd.concat([df_history, new_row], ignore_index=True)
        df_history.to_csv(HISTORY_FILE, index=False)
        return True
    return False


def load_portfolio_history():
    """Charge l'historique mensuel."""
    if os.path.exists(HISTORY_FILE):
        df = pd.read_csv(HISTORY_FILE, parse_dates=['date'])
        
        if 'contributions_cad' not in df.columns:
            df['contributions_cad'] = 0.0
            if len(df) > 0:
                df.loc[0, 'contributions_cad'] = df.loc[0, 'valeur_totale_cad']
        
        return df.sort_values('date')
    return pd.DataFrame({
        'date': [], 
        'valeur_totale_cad': [], 
        'contributions_cad': []
    })


def calculate_returns_with_contributions(df_history):
    """Calcule les rendements avec contributions."""
    if df_history.empty or len(df_history) < 2:
        return None
    
    capital_investi = df_history['contributions_cad'].sum()
    valeur_actuelle = df_history['valeur_totale_cad'].iloc[-1]
    gain_reel = valeur_actuelle - capital_investi
    rendement_pct = (gain_reel / capital_investi * 100) if capital_investi > 0 else 0
    
    df_calc = df_history.copy()
    df_calc['capital_cum'] = df_calc['contributions_cad'].cumsum()
    df_calc['valeur_ajustee'] = df_calc['valeur_totale_cad'] - df_calc['contributions_cad']
    
    twr_periods = []
    for i in range(1, len(df_calc)):
        valeur_precedente = df_calc['valeur_totale_cad'].iloc[i-1]
        contribution_actuelle = df_calc['contributions_cad'].iloc[i]
        valeur_actuelle_period = df_calc['valeur_totale_cad'].iloc[i]
        
        if valeur_precedente > 0:
            ret = (valeur_actuelle_period - valeur_precedente - contribution_actuelle) / valeur_precedente
            twr_periods.append(1 + ret)
    
    if twr_periods:
        twr_total = np.prod(twr_periods) - 1
        twr_pct = twr_total * 100
    else:
        twr_pct = 0
    
    return {
        'capital_investi': capital_investi,
        'valeur_actuelle': valeur_actuelle,
        'gain_reel': gain_reel,
        'rendement_pct': rendement_pct,
        'twr_pct': twr_pct
    }


def get_sp500_shiller_pe():
    """Récupère le Shiller P/E ratio (CAPE) du S&P 500 avec historique."""
    try:
        # Utiliser SPY (SPDR S&P 500 ETF) car il a des données P/E plus fiables que l'indice
        sp500 = yf.Ticker("SPY")
        
        # Récupérer les infos actuelles
        info = sp500.info
        
        # Le Shiller PE n'est pas directement disponible via yfinance
        # On va utiliser le trailing PE comme approximation
        current_pe = info.get('trailingPE', None)
        
        if not current_pe:
            # Essayer avec des clés alternatives
            current_pe = info.get('trailingPegRatio', None)
        
        if not current_pe:
            return {'error': 'P/E non disponible pour SPY', 'current_pe': None}
        
        return {
            'current_pe': current_pe,
            'info': info,
            'error': None
        }
    except Exception as e:
        return {'error': str(e), 'current_pe': None}


def get_sp500_pe_metrics():
    """Récupère les métriques P/E et Forward P/E du S&P 500."""
    try:
        # Essayer plusieurs ETF S&P 500 pour trouver les données
        tickers_to_try = ["SPY", "IVV", "VOO"]
        
        pe = None
        forward_pe = None
        current_price = None
        
        for ticker_symbol in tickers_to_try:
            try:
                ticker = yf.Ticker(ticker_symbol)
                info = ticker.info
                
                temp_pe = info.get('trailingPE', None)
                temp_forward_pe = info.get('forwardPE', None)
                
                # Utiliser les premières données trouvées
                if temp_pe and not pe:
                    pe = temp_pe
                if temp_forward_pe and not forward_pe:
                    forward_pe = temp_forward_pe
                    current_price = info.get('regularMarketPrice', None)
                
                # Si on a les deux, on peut arrêter
                if pe and forward_pe:
                    break
            except:
                continue
        
        # Si pas de données du tout, retourner une erreur
        if not pe and not forward_pe:
            return {
                'pe': None,
                'forward_pe': None,
                'current_price': None,
                'error': 'Aucune métrique P/E disponible'
            }
        
        return {
            'pe': pe,
            'forward_pe': forward_pe,
            'current_price': current_price,
            'error': None
        }
    except Exception as e:
        return {'error': str(e), 'pe': None, 'forward_pe': None}
