from automatizacao import OtimizandoRotas

if __name__=='__main__':  
    
    # enderecos = ['R. Condor, 99 casa 3 - Vila Bosque, Maringá - PR, 87050-310 ',
    #             'R. Profa. Maria de Lourdes Antunes Planas, 225 - Jardim Oriental, Maringá - PR, 87024-214',
    #             'Viela José Ferreira Maia, 207 - Vila Esperanca, Maringá - PR, 87020-730,',
    #             'Av. Humaitá, 727 - Zona 04, Maringá - PR, 87014-200',
    #             'R. Pioneiro Marcelino Girotto, 185 - Jardim Itália II, Maringá - PR, 87060-655']
    
    enderecos = ['Praça da Catedral, s/n - Zona 02, Maringá - PR, 87010-530',
                'Av. Pioneiro Maurício Mariani, 671 - Jardim Itaipu, Maringá - PR, 87065-510',
                'Praça Nossa Sra. Aparecida - Vila Esperanca, Maringá - PR, 87020-790',
                'Av. Rio Branco, 1000 - Zona 05, Maringá - PR, 87015-380',
                'Av. Londrina, 1700 - Jardim Independencia, Sarandi - PR, 87114-010',
                'Praça Emíliano Perneta, s/n - Vila Operária, Maringá - PR, 87050-070']
    
        
    buscarota = OtimizandoRotas(mode = 'tempo')
    # buscarota.inicializar_driver()


    distancia_pares, tempo_pares = buscarota.gera_pares(enderecos)
    solucao = buscarota.gera_otimizacao(enderecos)
    buscarota.mostra_rota_otimizada(enderecos)
    otimizacao = buscarota.gera_otimizacao(enderecos)
    buscarota.adiciona_destino(endereco=end3, num_box=1)
    buscarota.verifica_endereco()
