import streamlit as st
import httpx
import uuid
from datetime import datetime
import asyncio
import json


st.set_page_config(
    page_title="Signa Chatbot",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

API_URL = "http://localhost:8000"

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    
if "messages" not in st.session_state:
    st.session_state.messages = []


async def send_message(query: str, session_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/chat",
            json={
                "query": query,
                "session_id": session_id
            },
            timeout=30.0
        )
        return response.json()


async def check_health():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/health", timeout=5.0)
            return response.json()
        except:
            return None


def format_product_display(products):
    if not products:
        return ""
    
    product_text = "\n\n**🛍️ Produtos encontrados:**\n"
    for i, product in enumerate(products, 1):
        name = product.get('name', 'Produto sem nome')
        price = product.get('price', 0)
        url = product.get('url', '#')
        colors = product.get('colors', [])
        
        product_text += f"\n{i}. **{name}**"
        if price:
            product_text += f" - €{price:.2f}"
        if colors:
            colors_str = ", ".join(colors[:3])
            if len(colors) > 3:
                colors_str += "..."
            product_text += f" (Cores: {colors_str})"
        product_text += f"\n   🔗 [Ver produto]({url})"
    
    return product_text


def main():
    st.title("🛍️ Assistente Virtual Signa")
    st.markdown("Procure produtos da Signa por categoria, cor, preço e muito mais!")
    
    health_status = asyncio.run(check_health())
    
    if health_status and health_status.get("status") == "healthy":
        products_count = health_status.get("products_count", 0)
        categories_count = health_status.get("categories_count", 0)
        st.sidebar.success(f"✅ Sistema online\n\n📦 {products_count} produtos\n📁 {categories_count} categorias")
    else:
        st.sidebar.error("❌ Sistema offline")
        st.error("O serviço está temporariamente indisponível. Inicie o servidor API primeiro.")
        st.code("python -m presentation.api.main")
        return
        
    with st.sidebar:
        st.markdown("### 💡 Sobre")
        st.markdown(
            "Este chatbot ajuda-o a encontrar produtos no catálogo da Signa. "
            "Pode pesquisar por nome, cor, categoria ou preço."
        )
        
        st.markdown("### 🔍 Exemplos de pesquisas")
        example_questions = [
            "tem caneca azul?",
            "mochilas baratas",
            "bolsas verdes",
            "produtos de tecnologia",
            "o que é a Signa?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"ex_{question}"):
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()
                
        st.markdown("---")
        if st.button("🗑️ Limpar conversa"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            asyncio.run(clear_session())
            st.rerun()
            
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            if message["role"] == "assistant" and "products" in message:
                products = message.get("products", [])
                if products:
                    st.markdown("**🛍️ Produtos encontrados:**")
                    
                    cols = st.columns(min(len(products), 2))
                    for i, product in enumerate(products[:4]):
                        col_idx = i % 2
                        with cols[col_idx]:
                            st.markdown(f"**{product.get('name', 'Produto')}**")
                            if product.get('price'):
                                st.markdown(f"💰 €{product['price']:.2f}")
                            if product.get('colors'):
                                colors_str = ", ".join(product['colors'][:3])
                                st.markdown(f"🎨 {colors_str}")
                            if product.get('url'):
                                st.markdown(f"🔗 [Ver produto]({product['url']})")
                            st.markdown("---")
            
            if message["role"] == "assistant" and "search_link" in message and message["search_link"]:
                st.markdown(f"🔗 [Ver mais produtos similares]({message['search_link']})")
                    
    if prompt := st.chat_input("Escreva a sua pergunta aqui... (ex: 'caneca azul', 'mochilas baratas')"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("A processar..."):
                response = asyncio.run(send_message(prompt, st.session_state.session_id))
                
            if "error" in response:
                st.error(f"Erro: {response['error']}")
            else:
                st.markdown(response["answer"])
                
                products = response.get("products", [])
                search_link = response.get("search_link")
                
                if products:
                    st.markdown("**🛍️ Produtos encontrados:**")
                    
                    cols = st.columns(min(len(products), 2))
                    for i, product in enumerate(products[:4]):
                        col_idx = i % 2
                        with cols[col_idx]:
                            st.markdown(f"**{product.get('name', 'Produto')}**")
                            if product.get('price'):
                                st.markdown(f"💰 €{product['price']:.2f}")
                            if product.get('colors'):
                                colors_str = ", ".join(product['colors'][:3])
                                st.markdown(f"🎨 {colors_str}")
                            if product.get('url'):
                                st.markdown(f"🔗 [Ver produto]({product['url']})")
                            st.markdown("---")
                
                if search_link:
                    st.markdown(f"🔗 [Ver mais produtos similares]({search_link})")
                
                confidence = response.get("confidence", 0)
                confidence_emoji = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.4 else "🔴"
                st.caption(f"{confidence_emoji} Confiança: {confidence:.0%}")
                
                message_data = {
                    "role": "assistant",
                    "content": response["answer"],
                    "products": products,
                    "search_link": search_link,
                    "confidence": confidence
                }
                st.session_state.messages.append(message_data)


async def clear_session():
    async with httpx.AsyncClient() as client:
        try:
            await client.delete(f"{API_URL}/sessions/{st.session_state.session_id}")
        except:
            pass


if __name__ == "__main__":
    main()