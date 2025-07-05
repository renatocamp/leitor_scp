import streamlit as st
import pandas as pd
import re

# Função para ler o arquivo .scp e extrair os dados
def ler_scp(arquivo):
    produtos = []
    conteudo = arquivo.read().decode('utf-8', errors='ignore')
    linhas = conteudo.splitlines()

    for linha in linhas:
        if linha.startswith('03'):
            codigo_ean = linha[21:36].strip()
            codigo_produto = linha[36:39].strip().upper()  # Corrigido para garantir 5 caracteres
            nome_completo = linha[40:81].strip()

            # Busca quantidade no nome (ex.: '50 UNID')
            match_quantidade = re.search(r'(\d+)\s*UNID', nome_completo.upper())
            quantidade = int(match_quantidade.group(1)) if match_quantidade else 0

            # Limpa nome do produto removendo quantidade e "UNID"
            nome_produto = re.sub(r'(\d+\s*UNID)', '', nome_completo, flags=re.IGNORECASE).strip()

            # Valor do produto em centavos -> reais
            valor_str = linha[89:98].strip()
            valor_centavos = int(valor_str) if valor_str.isdigit() else 0
            valor_reais = valor_centavos / 100

            produtos.append({
                'EAN/DUN': codigo_ean,
                'Cód. Produto': codigo_produto,
                'Produto': nome_produto,
                'Quantidade': quantidade,
                'Valor (R$)': valor_reais
            })

    return pd.DataFrame(produtos)

# Streamlit App
st.set_page_config(page_title="Leitor SCP", layout="wide")
st.title("📄 Leitor de Arquivo .SCP - Produtos do Pedido")

# Upload do arquivo
arquivo = st.file_uploader("📤 Faça upload do arquivo .SCP", type=['scp'])

if arquivo:
    df = ler_scp(arquivo)

    if not df.empty:
        st.success("✅ Produtos extraídos com sucesso!")
        st.dataframe(df, use_container_width=True)

        # Download CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name="produtos_extraidos.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ Nenhum produto encontrado no arquivo.")
else:
    st.info("🔍 Por favor, faça upload de um arquivo .SCP.")
