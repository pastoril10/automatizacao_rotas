from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys


from time import sleep
import pulp
import itertools

class OtimizandoRotas:
    '''Tipo de conducao pode ser: Carro, Motocicleta, A pé, Bicicleta'''
    
    def __init__(self, tipo_conducao='Carro', mode='distância'):
        self.destinos = []
        self.solucao = []
        self.distancia_pares = {} 
        self.tempo_pares = {}
        self.driver = None
        self.url = 'https://www.google.com/maps/'
        self.tipo_conducao = tipo_conducao
        self.mode = mode
        self.service = Service(ChromeDriverManager().install())
         
    def inicializar_driver(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.driver.implicitly_wait(2)
        self.driver.get(url = self.url)
                            
    def adiciona_destino(self, endereco, num_box=1):
        try: 
            if not self.verifica_aba_de_rotas():
                barra_de_busca = self.driver.find_element(By.ID, 'searchboxinput')
                barra_de_busca.clear()
                barra_de_busca.send_keys(endereco)
                barra_de_busca.send_keys(Keys.RETURN)       
            else:
                xpath = '//div[contains(@id, "directions-searchbox")]//input'
                boxs = self.driver.find_elements(By.XPATH, xpath)
                box_display = [box for box in boxs if box.is_displayed()]
                if len(box_display) >= num_box:
                    box_end = box_display[num_box - 1]
                    box_end.send_keys(Keys.CONTROL + 'a')
                    box_end.send_keys(Keys.DELETE)
                    box_end.send_keys(endereco)
                    box_end.send_keys(Keys.RETURN)      
                else:
                    print('Não conseguimos adicionar o endereço!')   
        except Exception as er:
            print(f'Erro do tipo ',er.__str__())                
                
    def verifica_endereco(self):
        if not self.driver:
            self.inicializar_driver() 
        xpath = '//div[@class="Q2vNVc" and contains(text(), "O Google Maps não encontrou")]'
        if self.driver.find_elements(By.XPATH, xpath):
            return False
        else:
            return True
                
    def verifica_aba_de_rotas(self):
        xpath = '//button[@aria-label="Fechar rotas"]'
        botao_rotas = self.driver.find_elements(By.XPATH, xpath) 
        return len(botao_rotas) > 0
                
    def busca_rotas(self):
        xpath = '//button[@data-value="Rotas"]'
        wait = WebDriverWait(self.driver, timeout=10)
        botao_rotas = wait.until(ec.presence_of_element_located((By.XPATH, xpath)))
        botao_rotas.click()

        xpath = '//button[@aria-label="Fechar rotas"]'
        wait = WebDriverWait(self.driver, timeout=10)
        botao_rotas = wait.until(ec.presence_of_element_located((By.XPATH, xpath)))
        
    def adiciona_caixa_destino(self):
        xpath = '//span[text()="Adicionar destino"]'
        wait = WebDriverWait(self.driver, timeout=5)
        wait.until(ec.visibility_of_element_located((By.XPATH, xpath)))
        
        adiciona_destino = self.driver.find_element(By.XPATH, xpath)
        adiciona_destino.click()
        
    def selecionar_tipo_conducao(self):
        xpath = f'//img[@aria-label="{self.tipo_conducao}"]'
        wait = WebDriverWait(self.driver, timeout=5)
        botao_tipo_conducao = wait.until(ec.presence_of_element_located((By.XPATH, xpath)))
        botao_tipo_conducao.click()

    def tempo_total(self):
            xpath = '//div[@id="section-directions-trip-0"]//div[contains(text(), "min") or contains(text(), "h")]'
            wait = WebDriverWait(self.driver, timeout=5)
            tempo_total = wait.until(ec.presence_of_element_located((By.XPATH, xpath)))
            
            tempo_texto = tempo_total.text
    
            if 'h' in tempo_texto:
                horas, minutos = tempo_texto.split(' h ')
                tempo_em_minutos = int(horas) * 60 + int(minutos.replace(' min', ''))
            else:
                tempo_em_minutos = int(tempo_texto.replace(' min', ''))

            return tempo_em_minutos
    
    def distancia_total(self):
        xpath = '//div[@id="section-directions-trip-0"]//div[contains(text(), "km")]'
        wait = WebDriverWait(self.driver, timeout=5)
        distancia_total = wait.until(ec.presence_of_element_located((By.XPATH, xpath)))
        return float(distancia_total.text.replace(' km', '').replace(',','.'))

    def gera_pares(self, enderecos: list) -> dict:   
        if not self.driver:
            self.inicializar_driver()   
        self.adiciona_destino(endereco=enderecos[0], num_box=1)
        self.busca_rotas()
        self.selecionar_tipo_conducao()
        try:
            for i, end1 in enumerate(enderecos):
                self.adiciona_destino(endereco=end1, num_box=1)
                for j, end2 in enumerate(enderecos):
                    if i != j:
                        self.adiciona_destino(end2, 2)
                        distancia = self.distancia_total()
                        tempo = self.tempo_total()
                        self.distancia_pares[f'{i}_{j}'] = distancia
                        self.tempo_pares[f'{i}_{j}'] = tempo
                        sleep(2)
            self.driver.close()
        except Exception as err:
            print(f'Endereço não encontrado: {end2} ')        
        return self.distancia_pares, self.tempo_pares
    
    def __get_values__(self, end1, end2):
        if self.mode == 'distância':
            return self.distancia_pares[f'{end1}_{end2}']
        
        elif self.mode == 'tempo':
            return self.tempo_pares[f'{end1}_{end2}']
        
    def gera_otimizacao(self, enderecos: list):            
        prob = pulp.LpProblem('TSP', pulp.LpMinimize)

        x = pulp.LpVariable.dicts('x', [(i, j) for i in range(len(enderecos)) for j in range(len(enderecos)) if i != j], cat='Binary')

        prob += pulp.lpSum([self.__get_values__(i, j) * x[(i, j)] for i in range(len(enderecos)) for j in range(len(enderecos)) if i != j])

        for i in range(len(enderecos)):
            prob += pulp.lpSum([x[(i, j)] for j in range(len(enderecos)) if i != j]) == 1
            prob += pulp.lpSum([x[(j, i)] for j in range(len(enderecos)) if i != j]) == 1
    
        for k in range(len(enderecos)):
            for S in range(2, len(enderecos)):
                for subset in itertools.combinations([i for i in range(len(enderecos)) if i != k], S):
                    prob += pulp.lpSum([x[(i, j)] for i in subset for j in subset if i != j]) <= len(subset) - 1
        
        prob.solve(pulp.PULP_CBC_CMD())

        
        cidade_inicial = 0
        proxima_cidade = cidade_inicial
        while True:
            for j in range(len(enderecos)):
                if j != proxima_cidade and x[(proxima_cidade), j].value() == 1:
                    self.solucao.append((proxima_cidade, j))
                    proxima_cidade = j
                    break
            if proxima_cidade == cidade_inicial:
                break
            
        print('Rota')    
        for i in range(len(self.solucao)):
            # print(self.solucao[i][0], '->>', self.solucao[i][1])        
            print(enderecos[self.solucao[i][0]], '->>', enderecos[self.solucao[i][1]])        
        return self.solucao
        
    def mostra_rota_otimizada(self, enderecos):
        self.inicializar_driver()
        self.adiciona_destino([enderecos[0]], 1)
        self.busca_rotas()
        for i in range(len(self.solucao)):
            self.adiciona_destino(enderecos[self.solucao[i][0]], i+1)
            self.adiciona_caixa_destino()
            
        self.adiciona_destino(enderecos[0], len(enderecos) + 1)
        texto = f'A distância total será de {self.distancia_total()} km e o tempo será de {self.tempo_total()} min'
        print(texto)
        sleep(10)
        self.driver.close()
        return texto
        

    # def mostra_rota_otimizada(self, enderecos):
    #     self.inicializar_driver()
    #     for i in range(len(self.solucao)):
    #         self.adiciona_destino(enderecos[self.solucao[i][0]], i+1)
    #         self.adiciona_caixa_destino()
            
    #     self.adiciona_destino(enderecos[0], len(enderecos) + 1)
    #     print(f'A distância total será de {self.distancia_total()} km e o tempo será de {self.tempo_total()} min')
    #     self.tempo_total()
    #     sleep(60)


# if __name__=='__main__':
#     try:
#         service = Service(ChromeDriverManager().install())
#         driver = webdriver.Chrome(service=service)
#         driver.implicitly_wait(2)
#         driver.get(url = 'https://www.google.com/maps/') 
#     except Exception as err:
#         print(err.__str__)
            
# enderecos = ['R. Condor, 99 casa 3 - Vila Bosque, Maringá - PR, 87050-310 ',
#             'R. Profa. Maria de Lourdes Antunes Planas, 225 - Jardim Oriental, Maringá - PR, 87024-214',
#             'Viela José Ferreira Maia, 207 - Vila Esperanca, Maringá - PR, 87020-730,',
#             'Av. Humaitá, 727 - Zona 04, Maringá - PR, 87014-200',
#             'R. Pioneiro Marcelino Girotto, 185 - Jardim Itália II, Maringá - PR, 87060-655']

# enderecos = ['Praça da Catedral, s/n - Zona 02, Maringá - PR, 87010-530',
#             'Av. Pioneiro Maurício Mariani, 671 - Jardim Itaipu, Maringá - PR, 87065-510',
#             'Praça Nossa Sra. Aparecida - Vila Esperanca, Maringá - PR, 87020-790',
#             'Av. Rio Branco, 1000 - Zona 05, Maringá - PR, 87015-380',
#             'Av. Londrina, 1700 - Jardim Independencia, Sarandi - PR, 87114-010',
#             'Praça Emíliano Perneta, s/n - Vila Operária, Maringá - PR, 87050-070']
    
# buscarota = OtimizandoRotas(mode = 'tempo')
# # buscarota.inicializar_driver()


# distancia_pares, tempo_pares = buscarota.gera_pares(enderecos)
# solucao = buscarota.gera_otimizacao(enderecos)
# buscarota.mostra_rota_otimizada(enderecos)
# otimizacao = buscarota.gera_otimizacao(enderecos)
# buscarota.adiciona_destino(endereco=end3, num_box=1)
# buscarota.verifica_endereco()

