import streamlit as st
from data_service import load_portfolio, get_usd_to_cad_rate, auto_complete_missing_sectors, auto_complete_missing_countries

# Import des composants
from components import portefeuille

st.set_page_config(
    page_title="Analyse de Portfolio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Réduire l'espace en haut de la page
st.markdown("""
    <style>
        .block-container {
            padding-top: 2.5rem;
            padding-bottom: 0rem;
        }
    </style>
    """, unsafe_allow_html=True)

# Sidebar pour paramètres globaux
st.sidebar.title("⚙️ Paramètres")
st.sidebar.markdown("---")

# Option pour prix temps réel
use_realtime = st.sidebar.checkbox("Utiliser les prix en temps réel", value=True, 
                                   help="Si activé, les valeurs sont calculées avec les prix actuels du marché")


# Charger les données
df_p, df_geo, df_consolidated = load_portfolio(use_realtime_prices=use_realtime)

if not df_p.empty:
    # Métriques globales
    total_v = df_p['Valeur_Finale'].sum()
    usd_to_cad = get_usd_to_cad_rate()
    
    # Ajouter le taux USD/CAD dans la sidebar
    st.sidebar.markdown("---")
    if usd_to_cad:
        st.sidebar.metric("Taux USD/CAD (Temps Réel)", f"{usd_to_cad:.4f}")
    else:
        st.sidebar.metric("Taux USD/CAD (Temps Réel)", "⚠️ Indisponible")

    # Afficher la valeur totale à droite avec CSS
    st.markdown(f"""
        <style>
            .portfolio-value {{
                position: fixed;
                top: 3.5rem;
                right: 2rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 0.75rem 1.25rem;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.15);
                z-index: 999;
            }}
            .portfolio-value-label {{
                font-size: 0.7rem;
                opacity: 0.9;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 0.25rem;
            }}
            .portfolio-value-amount {{
                font-size: 1.3rem;
                font-weight: 700;
            }}
        </style>
        <div class="portfolio-value">
            <div class="portfolio-value-label">Portefeuille</div>
            <div class="portfolio-value-amount">{total_v:,.0f} $</div>
        </div>
        """, unsafe_allow_html=True)

    # Affichage direct du portefeuille (conserve la 2ème barre d'onglets)
    portefeuille.render(df_p, df_geo, df_consolidated)

else:
    st.error("❌ Aucun portefeuille détecté. Assurez-vous d'avoir un dossier '/data' avec vos fichiers CSV.")
