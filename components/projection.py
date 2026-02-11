import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def format_qc(valeur, decimales=0):
    """Formate un chiffre au standard Québec : 1 000,00 $"""
    # Formatage de base avec virgule comme séparateur de milliers et point pour décimales
    s = f"{valeur:,.{decimales}f}"
    # On remplace la virgule par un espace (milliers) et le point par une virgule (décimales)
    # On utilise des caractères temporaires pour ne pas tout mélanger
    s = s.replace(",", " ").replace(".", ",")
    return f"{s} $"

def render(total_portfolio_value):
    """Affiche la calculette d'intérêts composés au format Québec."""
    
    st.header("💰 Projection de croissance", divider="blue")
    
    _, main_col, _ = st.columns([1, 4, 1])
    
    with main_col:
        st.subheader("Paramètres de projection")
        col_a, col_b = st.columns(2)
        
        with col_a:
            initial_amount = st.number_input(
                "Placement initial ($)",
                min_value=0.0,
                value=float(total_portfolio_value),
                step=1000.0,
                format="%.0f"
            )
            monthly_contribution = st.number_input(
                "Versements réguliers par mois ($)",
                min_value=0.0,
                value=500.0,
                step=100.0,
                format="%.0f"
            )
        
        with col_b:
            annual_rate = st.number_input(
                "Taux d'intérêt annuel (%)",
                min_value=0.0,
                max_value=30.0,
                value=7.0,
                step=0.5,
                format="%.1f"
            )
            years = st.slider(
                "Période (années)",
                min_value=1,
                max_value=60,
                value=20,
                step=1
            )

        # --- Calculs ---
        monthly_rate = annual_rate / 100 / 12
        months = years * 12
        data = []
        current_value = initial_amount
        total_contributions = initial_amount
        
        for month in range(months + 1):
            data.append({
                'Mois': month,
                'Année': month / 12,
                'Valeur_Totale': current_value,
                'Contributions': total_contributions,
                'Intérêts': current_value - total_contributions
            })
            if month < months:
                current_value = current_value * (1 + monthly_rate) + monthly_contribution
                total_contributions += monthly_contribution
        
        df = pd.DataFrame(data)
        final_value = df.iloc[-1]['Valeur_Totale']
        final_contributions = df.iloc[-1]['Contributions']
        final_interest = df.iloc[-1]['Intérêts']

        # Étape 2 : Section Résultats avec formatage Québec
        st.markdown("---")
        st.subheader("📊 Résultats de la simulation")
        
        res_col1, res_col2, res_col3 = st.columns(3)
        
        with res_col1:
            st.metric("Valeur finale", format_qc(final_value), delta=format_qc(final_interest))
        
        with res_col2:
            st.metric("Total investi", format_qc(final_contributions))
            
        with res_col3:
            st.metric("Intérêts gagnés", format_qc(final_interest))
            
        if final_contributions > 0:
            interest_ratio = (final_interest / final_contributions) * 100
            st.progress(min(interest_ratio / 100, 1.0))
            # Formatage de la légende avec la virgule pour le pourcentage
            ratio_str = f"{interest_ratio:.1f}".replace(".", ",")
            st.caption(f"Le gain représente **{ratio_str} %** du capital investi.")

    # Graphique
    st.markdown("---")
    fig = go.Figure()

    # Ajout des traces
    # Note : On garde %{y:,.0f} $ pour le montant et on peut personnaliser 
    # le libellé de l'axe X via layout.xaxis.tickformat
    fig.add_trace(go.Scatter(
        x=df['Année'], 
        y=df['Contributions'], 
        name='Capital versé', 
        stackgroup='one', 
        fillcolor='rgba(99, 110, 250, 0.5)',
        hovertemplate='%{y:,.0f} $'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Année'], 
        y=df['Intérêts'], 
        name='Intérêts accumulés', 
        stackgroup='one', 
        fillcolor='rgba(0, 204, 150, 0.5)',
        hovertemplate='%{y:,.0f} $'
    ))
    
    fig.update_layout(
        title=f"Projection de la croissance du portefeuille sur {years} ans",
        hovermode='x unified',
        height=500,
        margin=dict(l=20, r=20, t=60, b=100),
        
        separators=", ",
        
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.4, 
            xanchor="center",
            x=0.5
        ),
        
        # Configuration de l'axe X pour le Hover et les graduations
        xaxis=dict(
            title="Temps",
            ticksuffix=" an(s)", # Ajoute "an(s)" aux chiffres sur l'axe
            hoverformat=".0f"    # Arrondi à l'année entière dans le hover
        ),
        
        yaxis=dict(
            ticksuffix=" $",
            tickformat=",.0f" 
        )
    )
    
    # On affiche avec la config locale fr
    # L'utilisation de hovermode='x unified' affichera l'année en haut de l'étiquette
    st.plotly_chart(fig, width='stretch', config={'locale': 'fr'})