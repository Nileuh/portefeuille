import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import datetime as dt
from data_service import (
    build_portfolio_history,
    calculate_risk_metrics,
    calculate_concentration,
    compare_target_allocation,
    load_etf_allocations,
    get_sector,
    get_country,
    get_valuation_metrics,
    get_current_price,
    get_currency_for_symbol,
    get_usd_to_cad_rate,
    get_sp500_shiller_pe,
    get_sp500_pe_metrics
)
from config import (
    TARGET_ALLOCATION_GEO,
    COUNTRY_NORMALIZATION,
    PERFORMANCE_PERIODS,
    DEFAULT_BENCHMARK,
    RISK_FREE_RATE
)


def render(df_p, df_geo, df_consolidated):
    """Affiche le portefeuille (sans onglet Historique/Projection)."""
    
    if df_p.empty:
        st.info("Aucune donnée de portefeuille")
        return
    
    # Sous-onglets pour la page Portefeuille
    subtab1, subtab3, subtab4, subtab5 = st.tabs([
        "📊 Répartition",
        "🎯 Concentration",
        "📋 Positions",
        "🔍 Analyse"
    ])
    
    # Sous-onglet 1: Répartition
    with subtab1:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_sec = px.pie(
                df_p,
                values='Valeur_Finale',
                names='Secteur',
                title="Répartition par Secteur",
                hole=0.4
            )
            fig_sec.update_traces(
                textposition='none',
                hovertemplate='<b>%{label}</b><br>%{value:,.2f} $ CAD<br>%{percent}<extra></extra>'
            )
            fig_sec.update_layout(
                legend=dict(x=1.0, y=1.0, xanchor='right', yanchor='top')
            )
            st.plotly_chart(fig_sec, width='stretch')
        
        with col2:
            if not df_geo.empty:
                # Normaliser les noms de pays avant le groupement
                df_geo_copy = df_geo.copy()
                df_geo_copy['Pays'] = df_geo_copy['Pays'].replace(COUNTRY_NORMALIZATION)
                
                df_geo_grouped = df_geo_copy.groupby('Pays')['Valeur_Finale'].sum().reset_index()
                df_geo_grouped['Percentage'] = (df_geo_grouped['Valeur_Finale'] /
                                                df_geo_grouped['Valeur_Finale'].sum() * 100).round(2)
                
                fig_geo = px.pie(
                    df_geo_grouped,
                    values='Valeur_Finale',
                    names='Pays',
                    title="Répartition Géographique",
                    hole=0.4
                )
                
                fig_geo.update_traces(
                    textposition='none',
                    hovertemplate='<b>%{label}</b><br>%{value:,.2f} $ CAD<br>%{percent}<extra></extra>'
                )
                fig_geo.update_layout(
                    legend=dict(x=1.0, y=1.0, xanchor='right', yanchor='top')
                )
                st.plotly_chart(fig_geo, width='stretch')
            else:
                st.warning("Pas de données géographiques disponibles")
    
    # Onglet Performance supprimé
    
    # Sous-onglet 3: Concentration & Allocation
    with subtab3:
        if not df_consolidated.empty:
            st.subheader("Top positions et concentration")
            
            conc_data = calculate_concentration(df_consolidated)
            
            if conc_data:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Concentration Top 5",
                        f"{conc_data['top5_pct']:.2f} %",
                        help="Poids des 5 plus grandes positions"
                    )
                with col2:
                    st.metric(
                        "Indice Herfindahl (HHI)",
                        f"{conc_data['hhi']:.0f}",
                        help="Mesure de concentration (10000 = 1 actif, <1500 = bien diversifié)"
                    )
                
                # Top 10 bar chart
                top10 = conc_data['df_weighted'].nlargest(10, 'Valeur_Finale')
                fig_top = px.bar(
                    top10,
                    x='Poids_%',
                    y='Actif',
                    orientation='h',
                    title="Top 10 des positions (% du portefeuille)",
                    labels={'Poids_%': 'Poids (%)', 'Actif': 'Titre'}
                )
                fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_top, width='stretch')
            
            st.markdown("---")
            st.subheader("Comparaison à l'allocation cible")
            
            comparison_df = compare_target_allocation(df_geo, TARGET_ALLOCATION_GEO)
            
            if not comparison_df.empty:
                st.dataframe(comparison_df, width='stretch', hide_index=True)
                
                # Bar chart écarts
                fig_ecart = go.Figure()
                fig_ecart.add_trace(go.Bar(
                    x=comparison_df['Zone'],
                    y=comparison_df['Cible (%)'],
                    name='Cible',
                    marker_color='lightblue'
                ))
                fig_ecart.add_trace(go.Bar(
                    x=comparison_df['Zone'],
                    y=comparison_df['Actuel (%)'],
                    name='Actuel',
                    marker_color='orange'
                ))
                fig_ecart.update_layout(
                    title="Allocation géographique : Cible vs Actuel",
                    xaxis_title="Zone",
                    yaxis_title="Allocation (%)",
                    barmode='group'
                )
                st.plotly_chart(fig_ecart, width='stretch')
            else:
                st.info("Configuration de l'allocation cible requise.")
        else:
            st.info("Aucune donnée de portefeuille pour l'analyse de concentration")
    
    # Sous-onglet 4: Positions détaillées
    with subtab4:
        if not df_consolidated.empty:
            st.subheader("Liste détaillée des positions")
            
            total_v = df_p['Valeur_Finale'].sum()
            df_tableau = []
            usd_to_cad = get_usd_to_cad_rate()
            etf_allocations = load_etf_allocations()
            
            symboles_prix_manquants = []
            secteurs_manquants = []
            pays_manquants = []
            
            with st.spinner("Récupération des ratios de valorisation..."):
                for _, row in df_consolidated.iterrows():
                    symbol = str(row['Symbole']).upper().strip()
                    actif_name = str(row['Actif'])
                    
                    # Récupérer le prix actuel et la devise (en passant le nom pour détecter CDR)
                    current_price = get_current_price(symbol, actif_name)
                    currency = get_currency_for_symbol(symbol, actif_name)
                    
                    # Formater le prix selon la devise
                    if current_price:
                        if currency == 'USD' and usd_to_cad:
                            prix_cad = current_price * usd_to_cad
                            prix_display = f"{current_price:.2f} USD ({prix_cad:.2f} CAD)"
                        else:
                            prix_display = f"{current_price:.2f} {currency}"
                    else:
                        prix_display = '⚠️ Non trouvé'
                        symboles_prix_manquants.append(f"{symbol} ({actif_name})")
                    
                    if symbol in etf_allocations:
                        etf_info = etf_allocations[symbol]
                        valeur_etf = row['Valeur_Finale']
                        
                        # Récupérer le pays pour l'ETF si disponible
                        pays_etf = get_country(symbol) if symbol else None
                        
                        df_tableau.append({
                            'ETF/Action': row['Actif'],
                            'Symbole': symbol,
                            'Quantité': int(row['Quantité']),
                            'Prix': prix_display,
                            'Secteur': 'ETF',
                            'Pays': pays_etf if pays_etf else '',
                            'Valeur (CAD)': valeur_etf,
                            'Poids (%)': round(valeur_etf / total_v * 100, 2),
                            'P/E': None,
                            'Forward P/E': None
                        })
                    else:
                        sector = get_sector(symbol) if symbol else None
                        if not sector:
                            sector = "⚠️ Catégorie Inconnue"
                            secteurs_manquants.append(f"{symbol} ({actif_name})")
                        
                        # Récupérer le pays pour l'action
                        pays_action = get_country(symbol) if symbol else None
                        if not pays_action:
                            pays_manquants.append(f"{symbol} ({actif_name})")
                        
                        valuation = get_valuation_metrics(symbol)
                        
                        df_tableau.append({
                            'ETF/Action': row['Actif'],
                            'Symbole': symbol,
                            'Quantité': int(row['Quantité']),
                            'Prix': prix_display,
                            'Secteur': sector,
                            'Pays': pays_action if pays_action else '⚠️ Non défini',
                            'Valeur (CAD)': row['Valeur_Finale'],
                            'Poids (%)': round(row['Valeur_Finale'] / total_v * 100, 2),
                            'P/E': valuation['pe'] if valuation['pe'] else None,
                            'Forward P/E': valuation['forward_pe'] if valuation['forward_pe'] else None
                        })
            
            df_display = pd.DataFrame(df_tableau).sort_values('Valeur (CAD)', ascending=False)
            df_display = df_display.dropna(subset=['Valeur (CAD)'])
            df_display = df_display[df_display['Valeur (CAD)'] > 0].reset_index(drop=True)
            
            st.dataframe(df_display, width='stretch', hide_index=True)
            
            # Afficher les avertissements pour les données manquantes
            if symboles_prix_manquants:
                with st.expander(f"⚠️ {len(symboles_prix_manquants)} symbole(s) avec prix manquant", expanded=False):
                    for symbole in symboles_prix_manquants:
                        st.caption(f"• {symbole}")
            
            if secteurs_manquants:
                with st.expander(f"ℹ️ {len(secteurs_manquants)} symbole(s) avec secteur non défini", expanded=False):
                    for symbole in secteurs_manquants:
                        st.caption(f"• {symbole}")
            
            if pays_manquants:
                with st.expander(f"ℹ️ {len(pays_manquants)} symbole(s) avec pays non défini", expanded=False):
                    for symbole in pays_manquants:
                        st.caption(f"• {symbole}")
            
            # Bouton d'export CSV
            csv = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger en CSV",
                data=csv,
                file_name=f'portfolio_{dt.date.today()}.csv',
                mime='text/csv',
            )
        else:
            st.info("Aucune donnée de portefeuille pour afficher les positions détaillées")
    
    # Sous-onglet 5: Analyse
    with subtab5:
        st.subheader("🔍 Analyse d'un titre")
        
        # CSS pour retirer la bordure du formulaire
        st.markdown("""
            <style>
                [data-testid="stForm"] {
                    border: none !important;
                    padding: 0 !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Utiliser un formulaire pour permettre la soumission avec Enter
        with st.form(key="analysis_form", clear_on_submit=False):
            col1, col2, col3 = st.columns([2, 1, 3])
            
            with col1:
                ticker_input = st.text_input(
                    "Symbole boursier (ticker)",
                    placeholder="Ex: AAPL, MSFT, VFV.TO...",
                    help="Entrez le symbole d'une action ou d'un ETF"
                )
            
            with col2:
                st.markdown("<p style='margin-bottom: 0;'>&nbsp;</p>", unsafe_allow_html=True)
                analyze_button = st.form_submit_button("🔍 Analyser", width='stretch')
        
        if analyze_button and ticker_input:
            import yfinance as yf
            
            ticker = ticker_input.strip().upper()
            
            with st.spinner(f"Analyse de {ticker} en cours..."):
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    
                    # Récupérer l'historique pour la moyenne mobile 200j
                    hist = stock.history(period="1y")
                    
                    if not hist.empty and len(hist) > 0:
                        # Calculer les moyennes mobiles
                        ma_200 = hist['Close'].rolling(window=min(200, len(hist))).mean().iloc[-1]
                        ma_50 = hist['Close'].rolling(window=min(50, len(hist))).mean().iloc[-1]
                        current_price = hist['Close'].iloc[-1]
                        
                        # Récupérer l'historique complet pour l'ATH
                        hist_all = stock.history(period="max")
                        ath = hist_all['High'].max() if not hist_all.empty else None
                        
                        # Afficher le nom si disponible
                        stock_name = info.get('longName', info.get('shortName', ticker))
                        st.markdown(f"### {stock_name} ({ticker})")
                        
                        # Métriques principales
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            subcol1, subcol2 = st.columns(2)
                            
                            with subcol1:
                                st.metric("Prix actuel", f"{current_price:.2f} $", help="Le dernier prix de clôture de l'action")
                            
                            with subcol2:
                                if ath:
                                    diff_from_ath = ((current_price - ath) / ath) * 100
                                    st.metric(
                                        "ATH",
                                        f"{ath:.2f} $",
                                        f"{diff_from_ath:+.1f}%",
                                        help="Prix le plus haut historique (All-Time High). Le % indique l'écart par rapport au prix actuel."
                                    )
                                else:
                                    st.metric("ATH", "N/A", help="Prix le plus haut historique non disponible")
                        
                        with col2:
                            # Moyennes mobiles
                            if ma_50 and ma_200:
                                subcol1, subcol2 = st.columns(2)
                                
                                with subcol1:
                                    diff_pct_50 = ((current_price - ma_50) / ma_50) * 100
                                    st.metric(
                                        "MM 50j",
                                        f"{ma_50:.2f} $",
                                        f"{diff_pct_50:+.2f}%",
                                        help="Moyenne mobile 50 jours. Indique la tendance à court terme."
                                    )
                                
                                with subcol2:
                                    diff_pct_200 = ((current_price - ma_200) / ma_200) * 100
                                    st.metric(
                                        "MM 200j",
                                        f"{ma_200:.2f} $",
                                        f"{diff_pct_200:+.2f}%",
                                        help="Moyenne mobile 200 jours. Indique la tendance à long terme. Prix au-dessus = haussier, en dessous = baissier."
                                    )
                            else:
                                st.metric("Moyennes Mobiles", "N/A", help="Moyennes mobiles 50 et 200 jours non disponibles.")
                        
                        with col3:
                            # Graphique P/E vs Forward P/E
                            pe = info.get('trailingPE', None)
                            forward_pe = info.get('forwardPE', None)
                            
                            if pe or forward_pe:
                                fig_pe = go.Figure()
                                
                                if pe:
                                    fig_pe.add_trace(go.Bar(
                                        name='P/E Actuel',
                                        x=['P/E'],
                                        y=[pe],
                                        marker_color='#667eea',
                                        text=[f'{pe:.2f}'],
                                        textposition='outside',
                                        textfont=dict(size=16, color='white'),
                                        hovertemplate='<b>P/E Actuel</b><br>%{y:.2f}<extra></extra>'
                                    ))
                                
                                if forward_pe:
                                    fig_pe.add_trace(go.Bar(
                                        name='Forward P/E',
                                        x=['Forward P/E'],
                                        y=[forward_pe],
                                        marker_color='#764ba2',
                                        text=[f'{forward_pe:.2f}'],
                                        textposition='outside',
                                        textfont=dict(size=16, color='white'),
                                        hovertemplate='<b>Forward P/E</b><br>%{y:.2f}<extra></extra>'
                                    ))
                                
                                fig_pe.update_layout(
                                    title="Ratios P/E",
                                    showlegend=False,
                                    height=220,
                                    margin=dict(l=20, r=20, t=40, b=20),
                                    xaxis=dict(showticklabels=False),
                                    yaxis=dict(
                                        title="Ratio",
                                        range=[0, max(pe if pe else 0, forward_pe if forward_pe else 0) * 1.25]
                                    ),
                                    bargap=0
                                )
                                
                                st.plotly_chart(fig_pe, width='stretch')
                                st.caption("💡 P/E élevé (>25) = surévaluation possible | P/E bas (<15) = sous-évaluation possible")
                            else:
                                st.info("📊 Ratios P/E non disponibles")
                        
                        # Section dividendes (intégrée sans séparation)
                        dividend_yield = info.get('dividendYield', None)
                        dividend_rate = info.get('dividendRate', None)
                        
                        if dividend_yield and dividend_yield > 0:
                            st.markdown("")  # Petit espace
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("💰 Rendement du dividende", f"{dividend_yield:.2f}%", help="Revenu annuel en dividendes par rapport au prix. 3-6% est considéré comme bon. >8% peut être risqué.")
                            
                            with col2:
                                if dividend_rate:
                                    st.metric("💵 Dividende annuel", f"{dividend_rate:.2f} $", help="Montant annuel total versé en dividendes par action.")
                                else:
                                    st.metric("💵 Dividende annuel", "N/A", help="Montant annuel total versé en dividendes par action.")
                            
                            with col3:
                                payout_ratio = info.get('payoutRatio', None)
                                if payout_ratio:
                                    st.metric("📊 Taux de distribution", f"{payout_ratio * 100:.2f}%", help="Proportion des bénéfices versée en dividendes. <60% = durable, >80% = risque de coupure.")
                        
                        st.markdown("---")
                        with st.expander("📋 Informations supplémentaires"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                sector = info.get('sector', 'N/A')
                                industry = info.get('industry', 'N/A')
                                market_cap = info.get('marketCap', None)
                                
                                st.write(f"**Secteur:** {sector}")
                                st.write(f"**Industrie:** {industry}")
                                if market_cap:
                                    st.write(f"**Capitalisation:** {market_cap:,.0f} $")
                            
                            with col2:
                                country = info.get('country', 'N/A')
                                currency = info.get('currency', 'N/A')
                                exchange = info.get('exchange', 'N/A')
                                
                                st.write(f"**Pays:** {country}")
                                st.write(f"**Devise:** {currency}")
                                st.write(f"**Bourse:** {exchange}")
                    
                        # Tableaux financiers annuels
                        st.markdown("---")
                        st.subheader("📊 Données financières annuelles")
                        
                        # Récupérer les données financières
                        financials = stock.financials
                        balance_sheet = stock.balance_sheet
                        cashflow = stock.cashflow
                        
                        if not financials.empty:
                            all_data = {}
                            
                            # Performance
                            if 'Total Revenue' in financials.index:
                                all_data['Chiffre d\'affaires'] = financials.loc['Total Revenue']
                            
                            if 'Net Income' in financials.index:
                                all_data['Résultat net'] = financials.loc['Net Income']
                            
                            if 'Total Revenue' in financials.index and 'Net Income' in financials.index:
                                marge = (financials.loc['Net Income'] / financials.loc['Total Revenue'])
                                all_data['Marge bénéficiaire nette'] = marge
                            
                            # Rentabilité
                            if 'Basic EPS' in financials.index:
                                all_data['Bénéfice par action (EPS)'] = financials.loc['Basic EPS']
                            
                            if not cashflow.empty and 'Free Cash Flow' in cashflow.index:
                                all_data['Flux de trésorerie disponible'] = cashflow.loc['Free Cash Flow']
                            
                            # Finance
                            if not balance_sheet.empty:
                                if 'Total Liabilities Net Minority Interest' in balance_sheet.index:
                                    all_data['Total du passif'] = balance_sheet.loc['Total Liabilities Net Minority Interest']
                                elif 'Total Debt' in balance_sheet.index:
                                    all_data['Total du passif'] = balance_sheet.loc['Total Debt']
                                
                                if 'Stockholders Equity' in balance_sheet.index:
                                    all_data['Total des capitaux propres'] = balance_sheet.loc['Stockholders Equity']
                                elif 'Total Equity Gross Minority Interest' in balance_sheet.index:
                                    all_data['Total des capitaux propres'] = balance_sheet.loc['Total Equity Gross Minority Interest']
                            
                            if all_data:
                                df_all = pd.DataFrame(all_data).T
                                
                                # Inverser l'ordre des colonnes (année la plus ancienne à gauche)
                                df_all = df_all[sorted(df_all.columns)]
                                
                                # Formater les colonnes (années)
                                df_all.columns = [col.strftime('%Y') for col in df_all.columns]
                                
                                # Créer une copie pour le formatage d'affichage
                                df_display = pd.DataFrame(index=df_all.index, columns=df_all.columns)
                                
                                # Formater les nombres pour l'affichage avec flèches et variations
                                cols = df_all.columns.tolist()
                                for i, col in enumerate(cols):
                                    for idx in df_all.index:
                                        val = df_all.loc[idx, col]
                                        if pd.notna(val):
                                            # Formater la valeur de base
                                            if 'EPS' in idx or 'Marge' in idx:
                                                formatted_val = f"{val:.2f}"
                                            else:
                                                formatted_val = f"{val:,.0f}"
                                            
                                            # Ajouter la flèche et le % si ce n'est pas la première année
                                            if i > 0:
                                                prev_val = df_all.loc[idx, cols[i-1]]
                                                if pd.notna(prev_val) and prev_val != 0:
                                                    pct_change = ((val - prev_val) / abs(prev_val)) * 100
                                                    
                                                    if val > prev_val:
                                                        df_display.loc[idx, col] = f"{formatted_val} <span style='color:#4ade80'>⬆ {pct_change:.1f}%</span>"
                                                    elif val < prev_val:
                                                        df_display.loc[idx, col] = f"{formatted_val} <span style='color:#f87171'>⬇ {abs(pct_change):.1f}%</span>"
                                                    else:
                                                        df_display.loc[idx, col] = formatted_val
                                                else:
                                                    df_display.loc[idx, col] = formatted_val
                                            else:
                                                df_display.loc[idx, col] = formatted_val
                                        else:
                                            df_display.loc[idx, col] = ""
                                
                                # Afficher le tableau avec une largeur réduite
                                col_spacer1, col_table, col_spacer2 = st.columns([0.05, 0.90, 0.05])
                                with col_table:
                                    # Créer un tableau HTML personnalisé
                                    html_table = "<table style='width:100%; border-collapse: collapse;'>"
                                    html_table += "<thead><tr style='border-bottom: 2px solid #555;'><th style='text-align:left; padding:8px;'>Métrique</th>"
                                    for col in df_display.columns:
                                        html_table += f"<th style='text-align:right; padding:8px;'>{col}</th>"
                                    html_table += "</tr></thead><tbody>"
                                    
                                    for idx in df_display.index:
                                        html_table += f"<tr style='border-bottom: 1px solid #333;'><td style='text-align:left; padding:8px;'>{idx}</td>"
                                        for col in df_display.columns:
                                            html_table += f"<td style='text-align:right; padding:8px;'>{df_display.loc[idx, col]}</td>"
                                        html_table += "</tr>"
                                    
                                    html_table += "</tbody></table>"
                                    st.markdown(html_table, unsafe_allow_html=True)
                                
                                # Guide d'interprétation
                                with st.expander("📚 Guide d'interprétation des données financières"):
                                    st.markdown("""
                                    **Chiffre d'affaires** 💰  
                                    Revenus totaux générés par l'entreprise. Une croissance constante (>10% annuel) est positive. Comparez avec les concurrents du secteur.
                                    
                                    **Résultat net** 📈  
                                    Profit après toutes les dépenses et impôts. Doit être positif et en croissance. Un résultat négatif indique une perte.
                                    
                                    **Marge bénéficiaire nette (%)** 📊  
                                    Pourcentage du revenu qui devient profit. >20% = excellente, 10-20% = bonne, 5-10% = acceptable, <5% = faible. Varie selon le secteur.
                                    
                                    **Bénéfice par action (EPS)** 💵  
                                    Profit divisé par nombre d'actions. Une croissance constante de l'EPS indique une entreprise en bonne santé. Comparez avec le prix de l'action.
                                    
                                    **Flux de trésorerie disponible** 💸  
                                    Argent disponible après investissements. Doit être positif et croissant. Un flux positif permet de payer des dividendes, racheter des actions ou investir.
                                    
                                    **Total du passif** ⚠️  
                                    Dettes et obligations totales. Comparez avec les capitaux propres. Un ratio Passif/Capitaux propres >2 peut être risqué.
                                    
                                    **Total des capitaux propres** 🏦  
                                    Valeur nette de l'entreprise. Doit augmenter avec le temps. Une croissance constante indique une accumulation de richesse pour les actionnaires.
                                    """)
                                
                                # Métriques supplémentaires
                                st.markdown("#### Ratios supplémentaires")
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    roe = info.get('returnOnEquity', None)
                                    if roe:
                                        st.metric("ROE (Return on Equity)", f"{roe * 100:.2f}%", help="Rentabilité des capitaux propres. Mesure l'efficacité à générer des profits. >15% = excellent, 10-15% = bon, <10% = faible.")
                                
                                with col2:
                                    roa = info.get('returnOnAssets', None)
                                    if roa:
                                        st.metric("ROA (Return on Assets)", f"{roa * 100:.2f}%", help="Rentabilité des actifs. Indique l'efficacité d'utilisation des actifs pour générer des profits. >5% = bon, variable selon le secteur.")
                                
                                with col3:
                                    pb_ratio = info.get('priceToBook', None)
                                    if pb_ratio:
                                        st.metric("Ratio Cours/Valeur comptable (P/B)", f"{pb_ratio:.2f}", help="Prix par rapport à la valeur comptable. <1 = sous-évalué, 1-3 = raisonnable, >3 = possiblement surévalué.")
                                
                                # Graphique Actif vs Passif
                                st.markdown("---")
                                st.markdown("#### 🏦 Comparaison Actif vs Passif")
                                
                                if not balance_sheet.empty:
                                    # Récupérer les valeurs pour toutes les années disponibles
                                    years = []
                                    assets_values = []
                                    liabilities_values = []
                                    
                                    for col in sorted(balance_sheet.columns):
                                        year = col.strftime('%Y')
                                        
                                        # Récupérer l'actif
                                        if 'Total Assets' in balance_sheet.index:
                                            asset_val = balance_sheet.loc['Total Assets', col]
                                            if pd.notna(asset_val):
                                                years.append(year)
                                                assets_values.append(asset_val)
                                                
                                                # Récupérer le passif correspondant
                                                if 'Total Liabilities Net Minority Interest' in balance_sheet.index:
                                                    liab_val = balance_sheet.loc['Total Liabilities Net Minority Interest', col]
                                                elif 'Total Debt' in balance_sheet.index:
                                                    liab_val = balance_sheet.loc['Total Debt', col]
                                                else:
                                                    liab_val = None
                                                
                                                liabilities_values.append(liab_val if pd.notna(liab_val) else 0)
                                    
                                    if years and assets_values:
                                        fig_balance = go.Figure()
                                        
                                        # Ajouter les barres d'actif
                                        fig_balance.add_trace(go.Bar(
                                            name='Total Actif',
                                            x=years,
                                            y=assets_values,
                                            marker_color='#4ade80',
                                            text=[f'{val:,.0f}' for val in assets_values],
                                            textposition='outside',
                                            textfont=dict(size=14, color='white'),
                                            hovertemplate='<b>Actif %{x}</b><br>%{y:,.0f}<extra></extra>'
                                        ))
                                        
                                        # Ajouter les barres de passif
                                        fig_balance.add_trace(go.Bar(
                                            name='Total Passif',
                                            x=years,
                                            y=liabilities_values,
                                            marker_color='#f87171',
                                            text=[f'{val:,.0f}' for val in liabilities_values],
                                            textposition='outside',
                                            textfont=dict(size=14, color='white'),
                                            hovertemplate='<b>Passif %{x}</b><br>%{y:,.0f}<extra></extra>'
                                        ))
                                        
                                        fig_balance.update_layout(
                                            barmode='group',
                                            showlegend=True,
                                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                            height=380,
                                            margin=dict(l=20, r=20, t=80, b=40),
                                            xaxis=dict(title="Année", tickangle=0),
                                            yaxis=dict(
                                                title="Montant ($)",
                                                range=[0, max(max(assets_values), max(liabilities_values)) * 1.2]
                                            )
                                        )
                                        
                                        col_spacer1, col_graph, col_spacer2 = st.columns([0.1, 0.8, 0.1])
                                        with col_graph:
                                            st.plotly_chart(fig_balance, width='stretch')
                                            
                                            # Calculer et afficher le ratio le plus récent
                                            if liabilities_values[0] and assets_values[0]:
                                                debt_to_asset = (liabilities_values[0] / assets_values[0]) * 100
                                                
                                                if debt_to_asset < 40:
                                                    st.success(f"💚 Ratio Dette/Actif ({years[0]}) : {debt_to_asset:.1f}% - Faible endettement, situation saine")
                                                elif debt_to_asset < 60:
                                                    st.info(f"💙 Ratio Dette/Actif ({years[0]}) : {debt_to_asset:.1f}% - Endettement modéré")
                                                else:
                                                    st.warning(f"⚠️ Ratio Dette/Actif ({years[0]}) : {debt_to_asset:.1f}% - Endettement élevé, surveiller de près")
                                    else:
                                        st.info("Données du bilan non disponibles pour ce graphique")
                                else:
                                    st.info("Bilan non disponible")
                            else:
                                st.info("📊 Aucune donnée financière annuelle disponible pour ce titre")
                        else:
                            st.info("📊 Aucune donnée financière annuelle disponible pour ce titre")
                    
                    else:
                        st.error(f"❌ Impossible de récupérer les données pour {ticker}")
                
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse de {ticker}: {str(e)}")
        
        elif analyze_button and not ticker_input:
            st.warning("⚠️ Veuillez entrer un symbole boursier")
    
    # Onglet Projection supprimé
