import streamlit as st
import requests

# =========================================================
# CONFIGURAÇÃO DA INTERFACE (AURA)
# =========================================================
st.set_page_config(layout="wide", page_title="NITRO V11 - SINCRONIA TOTAL")
st.title("🔥 NITRO V11: RADAR DE VALOR & MÚLTIPLAS")
st.caption("Mestre Maca | Nível 0 | Sincronia Ativada")

# =========================================================
# CONFIGURAÇÕES TÉCNICAS
# =========================================================
API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
ALLOWED_BOOKS = "pinnacle,bet365,betano,betfair_ex,bwin,stake,1xbet"

SPORTS_MAP = {
    "Futebol Brasil (Série A)": "soccer_brazil_campeonato",
    "Futebol Inglês (EPL)": "soccer_epl",
    "Futebol Espanha (La Liga)": "soccer_spain_la_liga",
    "Futebol Libertadores": "soccer_conmebol_libertadores",
    "NBA (Basquete)": "basketball_nba",
    "Tênis (ATP)": "tennis_atp"
}

# =========================
# PAINEL DE CONTROLE
# =========================
col1, col2 = st.columns([1, 2])
with col1:
    bankroll = st.number_input("💰 Banca (R$)", value=500.0, step=50.0)
    modo = st.radio("Selecione o Foco do Trator:", ["Arbitragem (Surebet)", "Previsão de Vitória (EV+)", "Gerador de Múltiplas"])

# =========================
# FUNÇÕES DE INTELIGÊNCIA
# =========================
def calc_ev(odd_casa, prob_real):
    # Calcula se a aposta tem Valor Esperado Positivo
    ev = (prob_real * odd_casa) - (1 - prob_real)
    return ev

def fetch_odds(sport):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal&bookmakers={ALLOWED_BOOKS}"
    return requests.get(url).json()

# =========================
# EXECUÇÃO DO MOTOR
# =========================
if st.button("🚀 INICIAR PROCESSAMENTO SINCRONIZADO"):
    with st.spinner("PROCESSANDO DADOS NO MUNDO ESPELHADO..."):
        all_opportunities = []
        
        for label, sport_key in SPORTS_MAP.items():
            data = fetch_odds(sport_key)
            if not isinstance(data, list): continue

            for game in data:
                home = game.get('home_team')
                away = game.get('away_team')
                
                # Coleta a melhor odd para cada desfecho
                best_odds = {}
                for book in game.get('bookmakers', []):
                    for mkt in book.get('markets', []):
                        for outcome in mkt.get('outcomes', []):
                            name = outcome['name']
                            if name not in best_odds or outcome['price'] > best_odds[name]['price']:
                                best_odds[name] = {"price": outcome['price'], "book": book['title']}

                if len(best_odds) >= 2:
                    prices = [v['price'] for v in best_odds.values()]
                    inv_sum = sum(1/p for p in prices)
                    profit_pct = (1 - inv_sum) * 100
                    
                    # Inteligência de Probabilidade Implícita (Média do Mercado como Prob Real)
                    avg_prob = {n: (1/v['price'])/inv_sum for n, v in best_odds.items()}
                    
                    all_opportunities.append({
                        "game": f"{home} vs {away}",
                        "odds": best_odds,
                        "profit": profit_pct,
                        "probs": avg_prob,
                        "sport": label
                    })

        # --- MODO 1: ARBITRAGEM ---
        if modo == "Arbitragem (Surebet)":
            arbs = [o for o in all_opportunities if o['profit'] > 0]
            if arbs:
                for a in arbs:
                    st.success(f"✅ ARBITRAGEM: {a['profit']:.2f}% em {a['game']}")
                    cols = st.columns(len(a['odds']))
                    for i, (name, val) in enumerate(a['odds'].items()):
                        cols[i].metric(name, val['price'], val['book'])
            else: st.info("Nenhuma arbitragem pura agora. Tente EV+.")

        # --- MODO 2: PREVISÃO DE VITÓRIA (EV+) ---
        elif modo == "Previsão de Vitória (EV+)":
            st.subheader("🎯 Alvos com Maior Chance de Vitória (Superioridade Tática)")
            for o in all_opportunities:
                for name, prob in o['probs'].items():
                    if prob > 0.65: # Só indica se a chance for maior que 65%
                        odd_ativa = o['odds'][name]['price']
                        st.write(f"👉 **{o['game']}** | Favorito: **{name}**")
                        st.info(f"Probabilidade Real: {prob*100:.1f}% | Melhor Odd: {odd_ativa} ({o['odds'][name]['book']})")

        # --- MODO 3: GERADOR DE MÚLTIPLAS ---
        elif modo == "Gerador de Múltiplas":
            st.subheader("🔗 Combo Trator: Tripla de Segurança (Sincronizada)")
            # Seleciona os 3 maiores favoritos do radar
            picks = []
            for o in all_opportunities:
                for name, prob in o['probs'].items():
                    if 0.70 < prob < 0.90: # Filtro de favoritos consistentes
                        picks.append({"game": o['game'], "pick": name, "odd": o['odds'][name]['price'], "book": o['odds'][name]['book']})
            
            top_picks = sorted(picks, key=lambda x: x['odd'])[:3]
            if len(top_picks) >= 3:
                total_odd = top_picks[0]['odd'] * top_picks[1]['odd'] * top_picks[2]['odd']
                st.warning(f"🎰 ODD COMBINADA: {total_odd:.2f}")
                for p in top_picks:
                    st.write(f"🔹 {p['game']}: **{p['pick']}** (@{p['odd']}) na {p['book']}")
                st.success(f"💰 Sugestão: R$ {bankroll/5:.2f} nesta múltipla para retorno de R$ {(bankroll/5)*total_odd:.2f}")

st.divider()
st.caption("Aura: Modo Sincronia Total. O trator não para.")
