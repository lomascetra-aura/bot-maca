import streamlit as st
import requests
import time

st.set_page_config(page_title="BOT NITRO | MESTRE MACA", layout="wide")
st.title("🚀 BOT NITRO | MESTRE MACA")
st.subheader("Scanner de Elite: 11 Gigantes (Incluindo Luck.bet)")

API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
investimento = st.number_input("Valor total para distribuir (R$)", value=100.0)

# Lista atualizada com 11 casas (Incluindo Luck.bet e as Gigantes)
# Nota: Na API, algumas casas podem usar IDs específicos. Mantive as mais estáveis.
GIGANTES = "bet365,betano,betfair_ex,sportingbet,pinnacle,novibet,kto,esportesdasorte,superbet,stake,luckbet"

if st.button("🔍 ESCANEAR MERCADO AGORA"):
    progresso = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Conectando à Luck.bet e outras 10 gigantes...")
    progresso.progress(20)
    
    # Busca por jogos futuros (estabilidade de 3-5 min)
    URL = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={API_KEY}&regions=eu,us&markets=h2h&bookmakers={GIGANTES}"
    
    try:
        res = requests.get(URL).json()
        progresso.progress(60)
        status_text.text("Buscando diamantes no Basquete, Tênis e Futebol...")
        
        found = False
        
        for jogo in res:
            esporte = jogo['sport_title']
            home = jogo['home_team']
            away = jogo['away_team']
            
            best_odds = {"1": 0, "X": 0, "2": 0}
            bookies = {"1": "-", "X": "-", "2": "-"}
            
            for b in jogo['bookmakers']:
                for m in b['markets']:
                    for o in m['outcomes']:
                        tipo = "1" if o['name'] == home else ("2" if o['name'] == away else "X")
                        if o['price'] > best_odds[tipo]:
                            best_odds[tipo] = o['price']
                            bookies[tipo] = b['title']
            
            if best_odds["1"] > 0 and best_odds["2"] > 0:
                # Cálculo automático para 2 ou 3 resultados
                if best_odds["X"] > 0:
                    inv_total = (1/best_odds["1"]) + (1/best_odds["X"]) + (1/best_odds["2"])
                else:
                    inv_total = (1/best_odds["1"]) + (1/best_odds["2"])
                
                # Só mostra se der LUCRO (Menor que 1.0)
                if inv_total < 1.0:
                    found = True
                    lucro_pct = (1 - inv_total) * 100
                    
                    with st.expander(f"💎 {esporte}: {home} vs {away}", expanded=True):
                        st.success(f"**LUCRO GARANTIDO: {lucro_pct:.2f}%**")
                        c1, c2, c3 = st.columns(3)
                        
                        v1 = (investimento / best_odds["1"]) / inv_total
                        c1.metric(f"{home}", f"R$ {v1:.2f}", f"Odd {best_odds['1']} na {bookies['1']}")
                        
                        if best_odds["X"] > 0:
                            vx = (investimento / best_odds["X"]) / inv_total
                            c2.metric("EMPATE", f"R$ {vx:.2f}", f"Odd {best_odds['X']} na {bookies['X']}")
                        
                        v2 = (investimento / best_odds["2"]) / inv_total
                        c3.metric(f"{away}", f"R$ {v2:.2f}", f"Odd {best_odds['2']} na {bookies['2']}")
        
        progresso.progress(100)
        status_text.text("Varredura completa!")
        
        if not found:
            st.warning("Mercado equilibrado no momento. As 11 casas estão alinhadas.")
            
    except Exception as e:
        st.error(f"Erro na conexão: {e}")

st.divider()
st.caption("Monitorando: Bet365, Betano, Betfair, Sportingbet, Pinnacle, Novibet, KTO, Esportes da Sorte, Superbet, Stake e Luck.bet.")
