import streamlit as st
from azure.storage.blob import BlobServiceClient    
import os
import pymssql
import uuid
import json
from dotenv import load_dotenv

load_dotenv()
blob_connection_string = os.getenv("BLOB_CONNECTION_STRING")
container_name = os.getenv("BLOB_CONTAINER_NAME")
account_name = os.getenv("BLOB_ACCOUNT_NAME")
sql_server = os.getenv("SQL_SERVER")
sql_database = os.getenv("SQL_DATABASE")
sql_user = os.getenv("SQL_USER")
sql_password = os.getenv("SQL_PASSWORD")

st.title("Cadastro de Produtos")

product_name = st.text_input("Nome do Produto")
product_price = st.number_input("Preço do Produto", min_value=0.00, format="%.2f")
product_description = st.text_area("Descrição do Produto")
product_image = st.file_uploader("Foto do Produto", type=["jpg", "jpeg", "png"]) 

#save image on blob storage
def upload_blob(file):
    blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_name = str(uuid.uuid4()) + file.name
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file.read(), overwrite=True)
    image_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}"
    return image_url

def insert_product(name, price, description, image_url):
    try:
        conn = pymssql.connect(server=sql_server, user=sql_user, password=sql_password, database=sql_database)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Produtos (nome, preco, descricao, imagem_url) VALUES (%s, %s, %s, %s)", (name, price, description, image_url))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao inserir produto: {e}")
        return False

 
def list_products():
    try:
        conn = pymssql.connect(server=sql_server, user=sql_user, password=sql_password, database=sql_database)
        cursor = conn.cursor()
        cursor.execute("SELECT nome, preco, descricao, imagem_url FROM Produtos")
        products = cursor.fetchall()
        conn.close()
        return products
    except Exception as e:
        st.error(f"Erro ao listar produtos: {e}")
        return []

def list_products_screen():
    products = list_products()
    if products:
    # Define o número de cards por linha
        cards_por_linha = 3
        # Cria as colunas iniciais
        cols = st.columns(cards_por_linha)
        for i, product in enumerate(products):
            col = cols[i % cards_por_linha]
            with col:
                st.markdown(f"### {product[0]}")  # Nome do produto']}")
                st.write(f"**Descrição:** {product[2]}")
                st.write(f"**Preço:** R$ {product[1]:.2f}")
                if product[3]:
                    html_img = f'<img src="{product[3]}" width="200" height="200" alt="Imagem do produto">'
                    st.markdown(html_img, unsafe_allow_html=True)
                st.markdown("---")
            # A cada 'cards_por_linha' produtos, se ainda houver produtos, cria novas colunas
            if (i + 1) % cards_por_linha == 0 and (i + 1) < len(products):
                cols = st.columns(cards_por_linha)
    else:
        st.info("Nenhum produto encontrado.")

if st.button("Cadastrar Produto"):
        if product_image is not None:
            image_url = upload_blob(product_image)
            insert_product(product_name, product_price, product_description, image_url)
            st.success("Produto cadastrado com sucesso!")
        else:
            st.warning("Por favor, selecione uma foto para o produto.")

    
st.header("Produtos Cadastrados")    


if st.button("Listar Produtos"):
    list_products_screen()


    
        