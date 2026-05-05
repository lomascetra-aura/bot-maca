import streamlit as st
import requests

st.set_page_config(page_title="BOT NITRO | MACA", layout="wide")
st.title("🔥 MODO AGRESSIVO: LUCRO GARANTIDO")
st.subheader("Maca, o trator está na pista. Foco em Arbitragem Real.")

API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
investimento = st.number_input("Banca para Operação (R$)", value=500.0)

# O Arsenal: 11 Gigantes
GIGANTES = "bet365,betano,betfair_ex,sportingbet,pinnacle,novibet,kto,esportesdasorte,superbet,stake,luckbet"

if st.button("🚀 EXECUTAR VARREDURA AGRESSIVA"):
    with st.spinner("Extraindo dados das Gigantes..."):
        URL = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={API_KEY}&regions=eu,us&markets=h2h&bookmakers={GIGANTES}"
        
        try:
            res = requests.get(URL).json()
            found = False
            
            for jogo in res:
                home, away = jogo['home_team'], jogo['away_team']
                # Coleta a MELHOR odd do mercado para cada resultado
                best = {"1": 0, "X": 0, "2": 0}
                bookie = {"1": "", "X": "", "2": ""}
                
                for b in jogo['bookmakers']:
                    for o in b['markets'][0]['outcomes']:
                        t = "1" if o['name'] == home else ("2" if o['name'] == away else "X")
                        if o['price'] > best[t]:
                            best[t], bookie[t] = o['price'], b['title']

                # Cálculo de Arbitragem (Futebol ou Tênis/NBA)
                if best["1"] > 0 and best["2"] > 0:
                    inv = (1/best["1"]) + (1/best["2"]) + (1/best["X"] if best["X"] > 0 else 0)
                    
                    if inv < 0.998: # Se der lucro (mesmo que 0.2%), a gente quer!
                        found = True
                        lucro_abs = (investimento / inv) - investimento
                        with st.expander(f"💰 LUCRO REAL: {home} vs {away}", expanded=True):
                            st.success(f"RETORNO: R$ {lucro_abs:.2f} SOBRE OS R$ {investimento:.2f}")
                            c1, c2, c3 = st.columns(3)
                            v1 = (investimento / best["1"]) / inv
                            c1.metric(f"{home}", f"R$ {v1:.2f}", f"Odd {best['1']} na {bookie['1']}")
                            if best["X"] > 0:
                                vx = (investimento / best["X"]) / inv
                                c2.metric("Empate", f"R$ {vx:.2f}", f"Odd {best['X']} na {bookie['X']}")
                            v2 = (investimento / best["2"]) / inv
                            c3.metric(f"{away}", f"R$ {v2:.2f}", f"Odd {best['2']} na {bookie['2']}")
            
            if not found:
                st.info("Mercado em equilíbrio. Aguarde a próxima oscilação.")
        except:
            st.error("Erro no motor de busca.")

st.divider()
st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
