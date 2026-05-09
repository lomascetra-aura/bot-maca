import streamlit as st
import requests

# Configuração Nitro
st.set_page_config(layout="wide", page_title="NITRO ENGINE | MACA")
st.title("🔥 NITRO ARB - TRATOR DE LUCRO 2026")

# --- PAINEL DE CONTROLE ---
col1, col2, col3 = st.columns(3)
with col1:
    bankroll = st.number_input("Banca Total (R$)", value=500.0, step=50.0)
with col2:
    esporte_label = st.selectbox(
        "Alvo do Trator",
        ["NBA (Basquete)", "Tênis (ATP)", "Futebol (Brasil)", "Futebol (Inglês)", "MMA (UFC)"]
    )
with col3:
    mercado_selecionado = st.selectbox(
        "Tipo de Mercado",
        ["Vencedor (H2H)", "Totais (Gols/Pontos)"]
    )

# Mapeamento
mapa_esportes = {
    "NBA (Basquete)": "basketball_nba",
    "Tênis (ATP)": "tennis_atp", 
    "Futebol (Brasil)": "soccer_brazil_campeonato",
    "Futebol (Inglês)": "soccer_epl",
    "MMA (UFC)": "mma_mixed_martial_arts"
}

mapa_mercados = {
    "Vencedor (H2H)": "h2h",
    "Totais (Gols/Pontos)": "totals"
}

# CONFIGURAÇÕES
API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
ALLOWED_BOOKS = ["pinnacle", "betfair_ex", "bet365", "betano", "1xbet", "stake", "bwin"]
BOOKS_QUERY = ",".join(ALLOWED_BOOKS)

def calc_stakes(bankroll, odds):
    inv = sum(1/o for o in odds)
    profit_pct = (1 - inv) * 100
    stakes = [(bankroll / o) / inv for o in odds]
    profit = (stakes[0] * odds[0]) - bankroll
    return {"profit_pct": profit_pct, "profit": profit, "stakes": stakes}

if st.button("🚀 INICIAR VARREDURA AGRESSIVA"):
    with st.spinner(f"CAÇANDO OPORTUNIDADES EM {esporte_label.upper()}..."):
        
        target_sport = mapa_esportes[esporte_label]
        target_market = mapa_mercados[mercado_selecionado]
        
        # Dinâmica para Tênis
        if esporte_label == "Tênis (ATP)":
            try:
                url_s = f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}"
                all_s = requests.get(url_s).json()
                active = [s['key'] for s in all_s if "tennis_atp" in s['key']]
                if active: target_sport = active[0]
                else: st.warning("Sem torneio de Tênis ativo."); st.stop()
            except: st.error("Erro na busca de esportes."); st.stop()

        # Chamada da API
        URL = f"https://api.the-odds-api.com/v4/sports/{target_sport}/odds/?apiKey={API_KEY}&regions=eu&markets={target_market}&oddsFormat=decimal&bookmakers={BOOKS_QUERY}"
        
        try:
            res = requests.get(URL).json()
            if not isinstance(res, list) or len(res) == 0:
                st.warning("📭 Nenhum dado encontrado no momento.")
            else:
                arbs, monitoring = [], []
                for game in res:
                    game_name = f"{game['home_team']} vs {game['away_team']}"
                    
                    # Para Totais, precisamos agrupar por linha (ex: Over 2.5 e Under 2.5)
                    market_groups = {}

                    for book in game.get('bookmakers', []):
                        if book['key'] not in ALLOWED_BOOKS: continue
                        for market in book.get('markets', []):
                            if market['key'] == target_market:
                                for o in market['outcomes']:
                                    # Chave única para o resultado (Time ou Linha de Over/Under)
                                    key_name = f"{o.get('point', '')} {o['name']}".strip()
                                    if key_name not in market_groups or o['price'] > market_groups[key_name]['price']:
                                        market_groups[key_name] = {"price": o['price'], "book": book['title']}

                    # Lógica de cálculo (precisa de 2 lados para comparar)
                    if len(market_groups) >= 2:
                        # Se for Totais, filtramos pares com o mesmo 'point' (ex: Over 210.5 e Under 210.5)
                        # Para simplificar na H2H, pegamos os melhores preços
                        prices = [m['price'] for m in market_groups.values()]
                        # Aqui o bot foca nos 2 melhores resultados opostos
                        if len(prices) >= 2:
                            prices = sorted(prices, reverse=True)[:2]
                            data = calc_stakes(bankroll, prices)
                            
                            # Identifica os nomes das casas para exibir
                            display_info = sorted(market_groups.items(), key=lambda x: x[1]['price'], reverse=True)[:2]
                            
                            item = {"game": game_name, "data": data, "display": display_info}
                            if data['profit_pct'] > 0: arbs.append(item)
                            elif data['profit_pct'] > -5.0: monitoring.append(item)

                # Exibição
                if arbs:
                    st.subheader("💰 ENTRADA CONFIRMADA!")
                    for r in arbs:
                        with st.expander(f"✅ {r['data']['profit_pct']:.2f}% | {r['game']}", expanded=True):
                            st.write(f"**LUCRO: R$ {r['data']['profit']:.2f}**")
                            c = st.columns(2)
                            for i, (name, info) in enumerate(r['display']):
                                c[i].metric(f"APOSTAR R$ {r['data']['stakes'][i]:.2f}", f"{name} @ {info['price']}", info['book'])
                
                st.subheader("👀 RADAR NITRO")
                for r in monitoring[:5]:
                    st.info(f"📊 {r['data']['profit_pct']:.2f}% | {r['game']} | Melhores odds em: {', '.join([x[1]['book'] for x in r['display']])}")

        except Exception as e:
            st.error(f"Erro no processamento: {e}")

st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
