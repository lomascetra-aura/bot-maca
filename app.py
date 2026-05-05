import streamlit as st
import requests

st.set_page_config(page_title="BOT NITRO | MESTRE MACA", layout="wide")
st.title("🚀 BOT NITRO | MESTRE MACA")

API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
investimento = st.number_input("Valor para investir (R$)", value=200.0)

if st.button("🔍 ESCANEAR OPORTUNIDADES"):
    with st.spinner("Varrendo as casas de apostas..."):
        # Puxando jogos do Brasileirão e Internacionais
        URL = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
        res = requests.get(URL).json()
        
        if not res:
            st.warning("Nenhum dado recebido. Verifique a chave API.")
        
        for jogo in res[:15]: # Analisa os primeiros 15 jogos
            home = jogo['home_team']
            away = jogo['away_team']
            
            # Pegando as melhores odds
            best_odds = {"1": 0, "X": 0, "2": 0}
            bookies = {"1": "-", "X": "-", "2": "-"}
            
            for b in jogo['bookmakers']:
                for o in b['markets'][0]['outcomes']:
                    tipo = "1" if o['name'] == home else ("2" if o['name'] == away else "X")
                    if o['price'] > best_odds[tipo]:
                        best_odds[tipo] = o['price']
                        bookies[tipo] = b['title']
            
            # Cálculo de Margem
            if best_odds["1"] > 0 and best_odds["X"] > 0 and best_odds["2"] > 0:
                margem = (1/best_odds["1"]) + (1/best_odds["X"]) + (1/best_odds["2"])
                lucro_potencial = (1 - margem) * 100
                
                with st.container():
                    st.subheader(f"🏟️ {home} vs {away}")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.write(f"**{home}**")
                        st.info(f"Odd: {best_odds['1']}\n\n({bookies['1']})")
                    with col2:
                        st.write("**Empate**")
                        st.info(f"Odd: {best_odds['X']}\n\n({bookies['X']})")
                    with col3:
                        st.write(f"**{away}**")
                        st.info(f"Odd: {best_odds['2']}\n\n({bookies['2']})")
                    with col4:
                        if margem < 1:
                            st.success(f"💎 ARBITRAGEM!\n\nLucro: {lucro_potencial:.2f}%")
                            v1 = (investimento / best_odds["1"]) / margem
                            v2 = (investimento / best_odds["X"]) / margem
                            v3 = (investimento / best_odds["2"]) / margem
                            st.write(f"Aposte: R${v1:.2f} | R${v2:.2f} | R${v3:.2f}")
                        else:
                            st.warning(f"Margem: {margem:.2f}\n\nSem Surebet agora")
                st.divider()
