import streamlit as st
from automatizacao import OtimizandoRotas

st.set_page_config(layout='wide', page_title='Otimizando rotas')

tipo_conducao = st.sidebar.selectbox('Tipo de condução:', ['Carro', 'Motocicleta'])
mode = st.sidebar.selectbox('Modo usado para cálculo:', ['Tempo', 'Distância'])
st.session_state.otimizacao_bem_sucedida = False
st.session_state.status = False
st.write(f'O tipo de deslocamento é {tipo_conducao.lower()} e o modo de cálculo é {mode.lower()}')

buscarota = OtimizandoRotas()

def clear_text():
    endereco = st.session_state.end_input
    if endereco:
        if endereco in st.session_state.enderecos:
            st.warning("O endereço que está tentando inserir já existe.")
        else:
            st.session_state.enderecos.append(endereco)
            st.session_state.end_input = ""

def remove_address(address):
    st.session_state.enderecos.remove(address)

def verificar_enderecos(enderecos):
    global buscarota  
    for endereco in enderecos:
        buscarota.adiciona_destino(endereco=endereco, num_box=1)
        if not buscarota.verifica_endereco():
            st.warning(f"O endereço '{endereco}' não foi encontrado.")
            return False
    st.success(f"Endereços validados com sucesso")
    return True

def otimizar_rotas(lista_enderecos, tipo_conducao, mode):
    global buscarota 
    buscarota = OtimizandoRotas(tipo_conducao=tipo_conducao, mode=mode.lower())
    distancia_pares, tempo_pares = buscarota.gera_pares(lista_enderecos)
    if not distancia_pares or not tempo_pares:
        st.error("Não foi possível gerar pares de distância/tempo. Verifique os endereços inseridos.")
        return None
    otimizacao = buscarota.gera_otimizacao(lista_enderecos)
    if otimizacao:
        st.success("Rota otimizada gerada com sucesso!")
        for i, (origem, destino) in enumerate(otimizacao):
            posicao = i+1
            st.write(f"Trecho {posicao}:")
            st.write(f"{lista_enderecos[origem]} ---->> {lista_enderecos[destino]}")
            st.write(f"----------------------------------------------")
            
        st.session_state.otimizacao_bem_sucedida = True
        return otimizacao  
    st.error("Falha ao otimizar as rotas. Por favor, tente novamente.")
    return None

if 'enderecos' not in st.session_state:
    st.session_state.enderecos = []

if 'end_input' not in st.session_state:
    st.session_state.end_input = ""

endereco_container = st.container()
with endereco_container:
    endereco = st.text_input(label='Endereço:', key='end_input')
    st.button('Adicionar Endereço', on_click=clear_text)
    st.write("### Endereços Inseridos:")

    for num, address in enumerate(st.session_state.enderecos):
        posicao = num+1
        if num == 0:
            if st.button(f"End{posicao} --> {address} **(Endereço de origem)**", on_click=remove_address, args=(address,), help=f"Excluir End{posicao}"):
                st.session_state.enderecos.remove(address)
        else:
            if st.button(f"End{posicao} --> {address}", on_click=remove_address, args=(address,), help=f"Excluir End{posicao}"):
                st.session_state.enderecos.remove(address)
                    
if st.session_state.enderecos:     
    if len(st.session_state.enderecos) >= 2:        
        st.session_state.otimizar = st.button('Otimizar rotas')  
        if st.session_state.otimizar:
            with st.spinner('Otimizando rotas...'):
                otimizacao = otimizar_rotas(list(st.session_state.enderecos), tipo_conducao, mode)
                                   

if st.session_state.otimizacao_bem_sucedida == True:
    lista_enderecos = list(st.session_state.enderecos)
    texto = buscarota.mostra_rota_otimizada(lista_enderecos)
    st.write(texto)
