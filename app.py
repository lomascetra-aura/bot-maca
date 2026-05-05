import streamlit as st
import requests

# Configuração da página para ficar bonita no celular
st.set_page_config(page_title="BOT NITRO | MESTRE MACA", layout="wide")
st.title("🚀 BOT NITRO | MESTRE MACA")
st.subheader("Calculadora de Lucro Real (11 Gigantes)")

# --- DADOS DO MESTRE ---
API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
investimento = st.number_input("Valor total para investir (R$)", value=200.0)

# Lista das 11 Gigantes (Foco em segurança e Brasil)
GIGANTES = "bet365,betano,betfair_ex,sportingbet,pinnacle,novibet,kto,esportesdasorte,superbet,stake,luckbet"

if st.button("🔍 BUSCAR OPORTUNIDADES REAIS"):
    with st.spinner("Varrendo mercados..."):
        # Buscando jogos futuros (Pré-jogo) para ter 3-5 min de calma
        URL = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={API_KEY}&regions=eu,us&markets=h2h&bookmakers={GIGANTES}"
        
        try:
            res = requests.get(URL).json()
            found = False
            
            for jogo in res:
                home = jogo['home_team']
                away = jogo['away_team']
                esporte = jogo['sport_title']
                
                best_odds = {"1": 0, "X": 0, "2": 0}
                bookies = {"1": "-", "X": "-", "2": "-"}
                
                for b in jogo['bookmakers']:
                    for o in b['markets'][0]['outcomes']:
                        tipo = "1" if o['name'] == home else ("2" if o['name'] == away else "X")
                        # Filtro de segurança contra odds erradas (acima de 30.0)
                        if 1.01 < o['price'] < 30.0:
                            if o['price'] > best_odds[tipo]:
                                best_odds[tipo] = o['price']
                                bookies[tipo] = b['title']

                if best_odds["1"] > 0 and best_odds["2"] > 0:
                    # Cálculo de Arbitragem (Surebet)
                    if best_odds["X"] > 0: # Futebol
                        margem = (1/best_odds["1"]) + (1/best_odds["X"]) + (1/best_odds["2"])
                    else: # Tênis/NBA
                        margem = (1/best_odds["1"]) + (1/best_odds["2"])

                    # SÓ MOSTRA SE O LUCRO FOR REAL (Margem abaixo de 0.99 para sobrar dinheiro)
                    if margem < 0.995:
                        found = True
                        lucro_total = (investimento / margem) - investimento
                        
                        with st.expander(f"💎 {esporte}: {home} vs {away}", expanded=True):
                            st.success(f"💰 Lucro Mínimo Garantido: R$ {lucro_total:.2f}")
                            c1, c2, c3 = st.columns(3)
                            
                            v1 = (investimento / best_odds["1"]) / margem
                            c1.metric(home, f"R$ {v1:.2f}", f"Odd {best_odds['1']} ({bookies['1']})")
                            
                            if best_odds["X"] > 0:
                                vx = (investimento / best_odds["X"]) / margem
                                c2.metric("Empate", f"R$ {vx:.2f}", f"Odd {best_odds['X']} ({bookies['X']})")
                            
                            v2 = (investimento / best_odds["2"]) / margem
                            c3.metric(away, f"R$ {v2:.2f}", f"Odd {best_odds['2']} ({bookies['2']})")

            if not found:
                st.info("Buscando... Nenhuma brecha de lucro real agora.")
                
        except Exception:
            st.error("Erro na API. Verifique sua cota mensal.")

st.divider()
st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
