import streamlit as st
import requests

st.set_page_config(page_title="BOT NITRO | MACA", layout="wide")
st.title("🔥 MODO AGRESSIVO: LUCRO GARANTIDO")
st.subheader("Maca, o trator está na pista. Foco em Arbitragem Real.")

# Chave e Arsenal
API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
GIGANTES = "bet365,betano,betfair_ex,pinnacle,1xbet,williamhill,marathonbet,draftkings"

investimento = st.number_input("Banca para Operação (R$)", value=500.0)

# Botão de Varredura
if st.button("🚀 EXECUTAR VARREDURA AGRESSIVA"):
    with st.spinner("Varrendo Mercados LIVE e Upcoming..."):
        # MUDANÇA NÍVEL 0: Buscando eventos AO VIVO (In-play) onde o spread aparece mais
        URL = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h,totals&bookmakers={GIGANTES}"
        
        try:
            res = requests.get(URL).json()
            found = False
            
            for jogo in res:
                home = jogo['home_team']
                away = jogo['away_team']
                
                for market_data in jogo['bookmakers'][0]['markets']:
                    m_type = market_data['key'] # h2h ou totals
                    
                    # Coleta a MELHOR odd do mercado
                    best = {}
                    bookie = {}
                    
                    for b in jogo['bookmakers']:
                        for m in b['markets']:
                            if m['key'] == m_type:
                                for o in m['outcomes']:
                                    # Chave única para o resultado (Vitoria, Empate, Over 2.5, etc)
                                    key = f"{o['name']}_{o.get('point', '')}"
                                    if key not in best or o['price'] > best[key]:
                                        best[key] = o['price']
                                        bookie[key] = b['title']

                    # Cálculo da Arbitragem
                    if len(best) >= 2:
                        inv = sum(1/v for v in best.values())
                        
                        # Se inv < 1.0, temos lucro! Baixamos para 0.999 para pegar TUDO
                        if inv < 0.999:
                            found = True
                            lucro_percent = (1 - inv) * 100
                            lucro_abs = (investimento / inv) - investimento
                            
                            with st.expander(f"💰 {lucro_percent:.2f}% LUCRO: {home} vs {away} ({m_type})", expanded=True):
                                st.success(f"RETORNO: R$ {lucro_abs:.2f} | INV: {inv:.4f}")
                                cols = st.columns(len(best))
                                for i, (label, price) in enumerate(best.items()):
                                    valor_aposta = (investimento / price) / inv
                                    cols[i].metric(f"{label}", f"R$ {valor_aposta:.2f}", f"Odd {price} na {bookie[label]}")
            
            if not found:
                st.info("Mercado em equilíbrio. Tentando expandir filtros...")
        except Exception as e:
            st.error(f"Erro no motor: {e}")

st.divider()
st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
