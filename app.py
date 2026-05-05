import streamlit as st

st.set_page_config(page_title="BOT NITRO | MESTRE MACA", layout="centered")

st.title("🚀 BOT NITRO | MESTRE MACA")
st.subheader("Scanner de Arbitragem Profissional")

# Entrada de Saldo
banca_total = st.number_input("Quanto deseja investir nessa oportunidade? (R$)", min_value=10.0, value=200.0)

def calcular_arbitragem(time_a, time_b, odd_a, odd_b):
    # Cálculo da Margem (Arbitragem existe se margem < 1)
    margem = (1 / odd_a) + (1 / odd_b)
    
    if margem < 1:
        lucro_porcentagem = (1 - margem) * 100
        # Cálculo de quanto apostar em cada lado para equilibrar o lucro
        aposta_a = (banca_total / (odd_a * margem))
        aposta_b = (banca_total / (odd_b * margem))
        
        retorno = aposta_a * odd_a
        lucro_real = retorno - banca_total
        
        with st.expander(f"✅ OPORTUNIDADE: {time_a} vs {time_b}", expanded=True):
            st.success(f"**LUCRO GARANTIDO: {lucro_porcentagem:.2f}%**")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(f"Apostar no {time_a}", f"R$ {aposta_a:.2f}")
                st.write(f"Odd: {odd_a}")
            with col2:
                st.metric(f"Apostar no {time_b}", f"R$ {aposta_b:.2f}")
                st.write(f"Odd: {odd_b}")
            
            st.divider()
            st.write(f"💰 **Retorno Total:** R$ {retorno:.2f}")
            st.write(f"📈 **Lucro Líquido:** R$ {lucro_real:.2f}")
    else:
        st.write(f"❌ {time_a} vs {time_b}: Sem arbitragem (Margem: {margem:.2f})")

if st.button("BUSCAR OPORTUNIDADES AGORA"):
    # Aqui simulamos os dados que viriam das APIs das Bets
    # Exemplo 1: Jogo com Arbitragem (Surebet)
    calcular_arbitragem("Coritiba", "Internacional", 2.10, 2.10)
    
    # Exemplo 2: Jogo sem Arbitragem
    calcular_arbitragem("Bahia", "Cruzeiro", 1.80, 1.90)
    
    # Exemplo 3: Outra Surebet
    calcular_arbitragem("Remo", "Palmeiras", 5.50, 1.25)

st.sidebar.info("Mestre Maca, este bot analisa as odds e calcula a divisão exata do seu dinheiro para que você não perca, independente do resultado.")
