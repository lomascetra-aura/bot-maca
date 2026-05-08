import streamlit as st
import requests

# Configuração de Interface Profissional
st.set_page_config(layout="wide", page_title="NITRO ENGINE | MACA")
st.title("🔥 NITRO ARB ENGINE - COMANDO TOTAL")

# --- PAINEL DE CONTROLE CENTRAL ---
col1, col2 = st.columns(2)
with col1:
    bankroll = st.number_input("Banca para Operação (R$)", value=500.0, step=50.0)
with col2:
    esporte_label = st.selectbox(
        "Alvo do Trator (Esporte)",
        ["Futebol (Brasil)", "NBA (Basquete)", "Tênis (ATP)", "Futebol (Inglês)", "MMA (UFC)"]
    )

# Mapeamento de Mercado
mapa = {
    "Futebol (Brasil)": "soccer_brazil_campeonato",
    "NBA (Basquete)": "basketball_nba",
    "Tênis (ATP)": "tennis_atp",
    "Futebol (Inglês)": "soccer_epl",
    "MMA (UFC)": "mma_mixed_martial_arts"
}
target_sport = mapa[esporte_label]

API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
BOOKS = "bet365,pinnacle,betano,1xbet,betfair_ex,williamhill,marathonbet,888sport,bwin,unibet"

def calc_stakes(bankroll, odds):
    inv = sum(1/o for o in odds)
    profit_pct = (1 - inv) * 100
    stakes = [(bankroll / o) / inv for o in odds]
    profit = (stakes[0] * odds[0]) - bankroll
    return {"profit_pct": profit_pct, "profit": profit, "stakes": stakes}

if st.button("🚀 INICIAR VARREDURA AGRESSIVA"):
    with st.spinner(f"VARRENDO {esporte_label.upper()}..."):
        URL = f"https://api.the-odds-api.com/v4/sports/{target_sport}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal&bookmakers={BOOKS}"
        
        try:
            res = requests.get(URL).json()
            arbs, monitoring = [], []

            for game in res:
                game_name = f"{game['home_team']} vs {game['away_team']}"
                best_odds = {}

                # Busca as melhores odds entre todas as casas
                for book in game.get('bookmakers', []):
                    for market in book.get('markets', []):
                        if market['key'] == 'h2h':
                            for o in market['outcomes']:
                                name = o['name']
                                if name not in best_odds or o['price'] > best_odds[name]['price']:
                                    best_odds[name] = {"price": o['price'], "book": book['title']}

                if len(best_odds) >= 2:
                    prices = [v['price'] for v in best_odds.values()]
                    data = calc_stakes(bankroll, prices)
                    item = {"game": game_name, "best": best_odds, "arb": data}
                    
                    if data['profit_pct'] > 0:
                        arbs.append(item)
                    elif data['profit_pct'] > -5.0:
                        monitoring.append(item)

            # --- EXIBIÇÃO DETALHADA (COMO VOCÊ PEDIU) ---
            if arbs:
                st.subheader("💰 OPORTUNIDADES DE LUCRO")
                for r in arbs:
                    with st.expander(f"✅ {r['arb']['profit_pct']:.2f}% | {r['game']}", expanded=True):
                        st.success(f"Lucro Estimado: R$ {r['arb']['profit']:.2f}")
                        cols = st.columns(len(r['best']))
                        # Aqui mostramos a odd e a casa para conferência rápida
                        for i, (name, info) in enumerate(r['best'].items()):
                            cols[i].metric(name, f"R$ {r['arb']['stakes'][i]:.2f}", f"{info['price']} na {info['book']}")
            
            st.divider()
            st.subheader("👀 RADAR DE CONFERÊNCIA (PRÓXIMOS DO LUCRO)")
            if monitoring:
                monitoring = sorted(monitoring, key=lambda x: x['arb']['profit_pct'], reverse=True)
                for r in monitoring[:10]:
                    with st.status(f"📊 {r['arb']['profit_pct']:.2f}% | {r['game']}", expanded=False):
                        # Detalhes das odds mesmo no radar para você vigiar
                        for name, info in r['best'].items():
                            st.write(f"👉 **{name}**: {info['price']} ({info['book']})")
            else:
                st.info("Nenhuma variação suspeita detectada no momento.")

        except Exception as e:
            st.error(f"Erro no motor: {e}")

st.divider()
st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
