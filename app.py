import streamlit as st
import requests

st.set_page_config(page_title="BOT NITRO MACA", layout="centered")
st.title("🚀 BOT NITRO | MESTRE MACA")

# Sua chave já configurada
API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"

saldo = st.number_input("Saldo por Casa (R$):", value=200.0)

if st.button("🔄 BUSCAR OPORTUNIDADES AGORA"):
    with st.spinner("Scanner em ação..."):
        # Busca focada no Brasileirão e ligas principais
        url = f"https://api.the-odds-api.com/v4/sports/soccer_brazil_campeonato/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
        try:
            res = requests.get(url).json()
            if res and isinstance(res, list):
                for jogo in res[:5]:
                    st.success(f"🏟️ {jogo['home_team']} vs {jogo['away_team']}")
                    st.write(f"Odds: {jogo['bookmakers'][0]['markets'][0]['outcomes'][0]['price']} | {jogo['bookmakers'][0]['markets'][0]['outcomes'][1]['price']}")
            else:
                st.info("Nenhuma oportunidade lucrativa encontrada agora. Tente mais tarde!")
        except:
            st.error("Erro na ligação. Verifique se a chave API ainda é válida.")
