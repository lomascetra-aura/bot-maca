import streamlit as st
import requests

# Configuração da Página - Estilo Nitro
st.set_page_config(layout="wide", page_title="NITRO ENGINE | MACA")
st.title("🔥 NITRO ARB - MODO TRATOR 2026")

# --- PAINEL DE CONTROLE ---
col1, col2 = st.columns(2)
with col1:
    bankroll = st.number_input("Banca Total (R$)", value=500.0, step=50.0)
with col2:
    esporte_label = st.selectbox(
        "Alvo do Trator",
        ["NBA (Basquete)", "Tênis (ATP)", "Futebol (Brasil)", "Futebol (Inglês)", "MMA (UFC)"]
    )

# Mapeamento Base
mapa = {
    "NBA (Basquete)": "basketball_nba",
    "Tênis (ATP)": "tennis_atp", 
    "Futebol (Brasil)": "soccer_brazil_campeonato",
    "Futebol (Inglês)": "soccer_epl",
    "MMA (UFC)": "mma_mixed_martial_arts"
}

# CONFIGURAÇÕES MESTRAS
API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
# Lista atualizada: Removidas inativas (WH, Unibet, 888) e adicionada STAKE
BOOKS = "pinnacle,betfair_ex,bet365,betano,1xbet,stake,bwin,marathonbet"

def calc_stakes(bankroll, odds):
    inv = sum(1/o for o in odds)
    profit_pct = (1 - inv) * 100
    stakes = [(bankroll / o) / inv for o in odds]
    profit = (stakes[0] * odds[0]) - bankroll
    return {"profit_pct": profit_pct, "profit": profit, "stakes": stakes}

if st.button("🚀 INICIAR VARREDURA AGRESSIVA"):
    with st.spinner(f"VARRENDO {esporte_label.upper()}..."):
        
        target_sport = mapa[esporte_label]
        
        # --- LÓGICA DINÂMICA PARA TÊNIS (Busca torneio ativo) ---
        if esporte_label == "Tênis (ATP)":
            try:
                url_sports = f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}"
                all_sports = requests.get(url_sports).json()
                active_tennis = [s['key'] for s in all_sports if "tennis_atp" in s['key']]
                
                if active_tennis:
                    target_sport = active_tennis[0] 
                    st.toast(f"🎾 Torneio detetado: {target_sport}")
                else:
                    st.warning("📭 Nenhum torneio de Tênis ATP ativo no momento.")
                    st.stop()
            except Exception as e:
                st.error(f"Erro ao localizar torneios: {e}")
                st.stop()

        # Chamada principal da API
        URL = f"https://api.the-odds-api.com/v4/sports/{target_sport}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal&bookmakers={BOOKS}"
        
        try:
            response = requests.get(URL)
            res = response.json()
            
            if response.status_code != 200:
                st.error(f"⚠️ Erro na API: {res.get('msg', 'Verifique créditos ou conexão.')}")
            elif not isinstance(res, list) or len(res) == 0:
                st.warning(f"📭 Sem jogos ativos para {esporte_label} agora.")
            else:
                arbs, monitoring = [], []
                
                for game in res:
                    game_name = f"{game['home_team']} vs {game['away_team']}"
                    best_odds = {}

                    for book in game.get('bookmakers', []):
                        for market in book.get('markets', []):
                            if 'h2h' in market['key']:
                                for o in market['outcomes']:
                                    name = o['name']
                                    if name not in best_odds or o['price'] > best_odds[name]['price']:
                                        best_odds[name] = {"price": o['price'], "book": book['title']}

                    if len(best_odds) >= 2:
                        sorted_names = sorted(best_odds.keys())
                        prices = [best_odds[n]['price'] for n in sorted_names]
                        data = calc_stakes(bankroll, prices)
                        
                        item = {"game": game_name, "names": sorted_names, "best": best_odds, "arb": data}
                        
                        if data['profit_pct'] > 0:
                            arbs.append(item)
                        elif data['profit_pct'] > -5.0: # Radar mais estreito para qualidade
                            monitoring.append(item)

                # --- EXIBIÇÃO ---
                if arbs:
                    st.subheader("💰 ENTRADA CONFIRMADA (LUCRO GARANTIDO)")
                    for r in arbs:
                        with st.expander(f"✅ Lucro: {r['arb']['profit_pct']:.2f}% | {r['game']}", expanded=True):
                            st.write(f"**RETORNO LÍQUIDO: R$ {r['arb']['profit']:.2f}**")
                            cols = st.columns(len(r['names']))
                            for i, name in enumerate(r['names']):
                                info = r['best'][name]
                                aposta_valor = r['arb']['stakes'][i]
                                cols[i].metric(f"APOSTAR R$ {aposta_valor:.2f}", f"Odd {info['price']}", info['book'])
                
                st.subheader("👀 RADAR DE OPORTUNIDADES")
                if monitoring:
                    monitoring = sorted(monitoring, key=lambda x: x['arb']['profit_pct'], reverse=True)
                    for r in monitoring[:8]:
                        with st.status(f"📊 {r['arb']['profit_pct']:.2f}% | {r['game']}", expanded=False):
                            for i, name in enumerate(r['names']):
                                info = r['best'][name]
                                st.write(f"💵 **R$ {r['arb']['stakes'][i]:.2f}** no **{name}** (Odd {info['price']} na {info['book']})")
                else:
                    st.info("Nenhuma oportunidade próxima no momento.")
        
        except Exception as e:
            st.error(f"Erro no motor: {e}")

st.divider()
st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
