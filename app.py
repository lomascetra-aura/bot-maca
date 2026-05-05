import streamlit as st
import requests

st.set_page_config(page_title="BOT NITRO | MESTRE MACA", layout="wide")
st.title("🚀 BOT NITRO | MESTRE MACA")
st.subheader("Scanner Multi-Esportes: Foco nas Gigantes do Brasil")

# Configurações do Mestre
API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
investimento = st.number_input("Valor total para distribuir (R$)", value=200.0)

# Lista das gigantes que o senhor pediu (IDs internos da API)
GIGANTES = "bet365,betano,betfair_ex,sportingbet,pinnacle" # Pinnacle é a 'mãe' das odds estáveis

if st.button("🔍 BUSCAR LUCRO NAS GIGANTES"):
    with st.spinner("Varrendo Basquete, Tênis, MMA e Futebol..."):
        # Buscamos em todos os esportes disponíveis na API (all)
        URL = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={API_KEY}&regions=eu,us&markets=h2h&bookmakers={GIGANTES}"
        
        try:
            res = requests.get(URL).json()
            found = False
            
            for jogo in res:
                esporte = jogo['sport_title']
                home = jogo['home_team']
                away = jogo['away_team']
                
                # Coleta as melhores odds para os dois lados (ou três no caso de empate)
                best_odds = {"1": 0, "X": 0, "2": 0}
                bookies = {"1": "-", "X": "-", "2": "-"}
                
                for b in jogo['bookmakers']:
                    for m in b['markets']:
                        for o in m['outcomes']:
                            tipo = "1" if o['name'] == home else ("2" if o['name'] == away else "X")
                            if o['price'] > best_odds[tipo]:
                                best_odds[tipo] = o['price']
                                bookies[tipo] = b['title']
                
                # Cálculo de Arbitragem (Surebet)
                # Se tiver empate (futebol), divide por 3. Se não (Tênis/Basquete), divide por 2.
                if best_odds["1"] > 0 and best_odds["2"] > 0:
                    if best_odds["X"] > 0: # Tem empate
                        inv_total = (1/best_odds["1"]) + (1/best_odds["X"]) + (1/best_odds["2"])
                    else: # Sem empate (Tênis/NBA/MMA)
                        inv_total = (1/best_odds["1"]) + (1/best_odds["2"])
                    
                    if inv_total < 1.0: # LUCRO DETECTADO!
                        found = True
                        lucro_pct = (1 - inv_total) * 100
                        
                        with st.expander(f"💎 {esporte}: {home} vs {away}", expanded=True):
                            st.success(f"**LUCRO GARANTIDO: {lucro_pct:.2f}%**")
                            c1, c2, c3 = st.columns(3)
                            
                            v1 = (investimento / best_odds["1"]) / inv_total
                            c1.metric(f"No {home}", f"R$ {v1:.2f}", f"Odd {best_odds['1']} na {bookies['1']}")
                            
                            if best_odds["X"] > 0:
                                vx = (investimento / best_odds["X"]) / inv_total
                                c2.metric("No EMPATE", f"R$ {vx:.2f}", f"Odd {best_odds['X']} na {bookies['X']}")
                            
                            v2 = (investimento / best_odds["2"]) / inv_total
                            c3.metric(f"No {away}", f"R$ {v2:.2f}", f"Odd {best_odds['2']} na {bookies['2']}")
                            
                            st.write(f"💰 **Retorno Líquido:** R$ {(investimento * (lucro_pct/100)):.2f}")
            
            if not found:
                st.warning("Mercados estáveis agora. As gigantes estão com as odds alinhadas.")
                
        except Exception as e:
            st.error(f"Erro na consulta: {e}")

st.info("Dica do Mestre: Jogos de Tênis e Basquete costumam dar arbitragem mais rápida que Futebol.")
