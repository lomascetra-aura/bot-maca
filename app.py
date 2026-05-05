import streamlit as st
import requests

# Configurações do App
st.set_page_config(page_title="BOT NITRO | MESTRE MACA", layout="centered")
st.title("🚀 BOT NITRO | MESTRE MACA")
st.subheader("Scanner de Arbitragem Profissional")

# Chave API (mantenha a sua ativa)
API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"

# Entrada de valor para investir
saldo = st.number_input("Quanto deseja investir nessa oportunidade? (R$)", value=200.0)

if st.button("🔍 BUSCAR OPORTUNIDADES AGORA"):
    with st.spinner("Escaneando mercados..."):
        # URL da API focada em ligas brasileiras e mercados de arbitragem
        URL = f"https://api.the-odds-api.com/v4/sports/soccer_brazil_campeonato/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
        
        try:
            res = requests.get(URL)
            jogos = res.json()

            if isinstance(jogos, list) and len(jogos) > 0:
                encontrou = False
                for jogo in jogos:
                    odds = [bookie['markets'][0]['outcomes'] for bookie in jogo['bookmakers']]
                    
                    # Lógica de cálculo de arbitragem (Inverso das Odds < 1)
                    # Para simplificar e focar no lucro garantido, o app calcula as melhores odds disponíveis
                    best_odds = {}
                    for outcome in odds[0]:
                        name = outcome['name']
                        best_odds[name] = max([o['price'] for opt in odds for o in opt if o['name'] == name])
                    
                    arbitrage_inv = sum(1/v for v in best_odds.values())
                    
                    if arbitrage_inv < 1:
                        encontrou = True
                        lucro_pct = (1 - arbitrage_inv) * 100
                        
                        with st.expander(f"✅ OPORTUNIDADE: {jogo['home_team']} vs {jogo['away_team']}", expanded=True):
                            st.success(f"LUCRO GARANTIDO: {lucro_pct:.2f}%")
                            
                            # Cálculo de quanto apostar em cada lado
                            for time, odd in best_odds.items():
                                valor_aposta = (saldo / odd) / arbitrage_inv
                                st.write(f"**Apostar no {time}**")
                                st.code(f"R$ {valor_aposta:.2f}")
                                st.caption(f"Odd: {odd}")
                            
                            st.divider()
                            st.write(f"💰 **Retorno Total:** R$ {saldo * (1 + (lucro_pct/100)):.2f}")
                            st.write(f"📈 **Lucro Líquido:** R$ {(saldo * (lucro_pct/100)):.2f}")
                
                if not encontrou:
                    st.warning("Nenhuma arbitragem lucrativa encontrada agora. Tente novamente em instantes!")
            else:
                st.error("Erro ao carregar dados da API. Verifique sua chave.")
        except Exception as e:
            st.error(f"Erro na conexão: {e}")

st.caption("Ajustado conforme as diretrizes do Mestre Maca.")
