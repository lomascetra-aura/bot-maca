import streamlit as st
import requests

st.set_page_config(page_title="BOT NITRO | MESTRE MACA", layout="wide")
st.title("🚀 BOT NITRO | MESTRE MACA")

API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8" # Sua chave
investimento = st.number_input("Valor total da operação (R$)", value=200.0)

if st.button("🔍 ESCANEAR MERCADO AGORA"):
    with st.spinner("Procurando brechas nas casas..."):
        # Buscando odds de futebol (H2H inclui o empate)
        URL = f"https://api.the-odds-api.com/v4/sports/soccer_brazil_campeonato/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
        res = requests.get(URL).json()
        
        found = False
        for jogo in res:
            # Pegamos as melhores odds para Casa, Empate e Fora entre todas as casas
            best_odds = {"1": 0, "X": 0, "2": 0}
            bookies = {"1": "", "X": "", "2": ""}
            
            for bookmaker in jogo['bookmakers']:
                for outcome in bookmaker['markets'][0]['outcomes']:
                    name = outcome['name']
                    price = outcome['price']
                    
                    # Identifica se é Casa, Fora ou Empate
                    tipo = "1" if name == jogo['home_team'] else ("2" if name == jogo['away_team'] else "X")
                    
                    if price > best_odds[tipo]:
                        best_odds[tipo] = price
                        bookies[tipo] = bookmaker['title']

            # Cálculo da Arbitragem (Surebet) para 3 resultados
            if best_odds["1"] > 0 and best_odds["X"] > 0 and best_odds["2"] > 0:
                probabilidade = (1/best_odds["1"]) + (1/best_odds["X"]) + (1/best_odds["2"])
                
                if probabilidade < 1.0: # Lucro garantido!
                    found = True
                    lucro = (1 - probabilidade) * 100
                    st.success(f"💎 OPORTUNIDADE DETECTADA: {jogo['home_team']} vs {jogo['away_team']}")
                    st.write(f"📈 **Lucro Real: {lucro:.2f}%**")
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        v = (investimento / best_odds["1"]) / probabilidade
                        st.metric(f"No {jogo['home_team']}", f"R$ {v:.2f}")
                        st.caption(f"Odd {best_odds['1']} na {bookies['1']}")
                    with c2:
                        v = (investimento / best_odds["X"]) / probabilidade
                        st.metric("No EMPATE", f"R$ {v:.2f}")
                        st.caption(f"Odd {best_odds['X']} na {bookies['X']}")
                    with c3:
                        v = (investimento / best_odds["2"]) / probabilidade
                        st.metric(f"No {jogo['away_team']}", f"R$ {v:.2f}")
                        st.caption(f"Odd {best_odds['2']} na {bookies['2']}")
                    st.divider()

        if not found:
            st.warning("Mercado equilibrado. Sem brechas de lucro 100% garantido neste segundo.")
