# a interface de rede nao fica atualizada com todas as redes disponiveis
# entao precisa executar o arquivo 'iwlist.sh' que forçara manter a interface de rede atualizada
# assim, o 'Cell' escaneara a interface corretamente
# lembre de colocar a interface de rede corre parametro do 'Cell'
# comando linux: ip a
import pickle
import os
import time
from wifi import Cell
from datetime import date
import pandas as pd
# from wifi_scan import listar_wifis #lib do carlos

def dump_file(data): # cria e/ou salva arquivo com seus dados
    with open('wifi_dict' + '.pkl', 'wb') as p_dump:
        pickle.dump(data, p_dump, pickle.HIGHEST_PROTOCOL)

def map_4_dict(wf_map): # converte o 'map' para 'dict', para podemos manipula-lo mais facilmente
    wf_dict = {} # usamos 'dict' caso tenha ssid reptido sera sobreescrito
    for wifi in wf_map:
        wf_dict[wifi.ssid] = {}
        wf_dict[wifi.ssid]['quality'] = get_qualidade(wifi.quality)
        wf_dict[wifi.ssid]['frequency'] = str(wifi.frequency)
    return wf_dict

def get_qualidade(quality): # retorna valor inteiro da qualidade 
    quality_clean = str(quality).split('/') 
    return int(quality_clean[0]) # sem normalização, melhor guardar o dado bruto
    # return int(q[0]) / 70 # com um tipo normalização, multiplica por 70 que volta ao dado original

def get_data_hora():
    horario = time.strftime("%H:%M:%S")
    hoje = date.today()
    return str(hoje) +'_'+ str(horario)

def preenche_dict_wifis(perssistencia, SEGUNDOS, CICLOS, comodo):
    wait = (SEGUNDOS*CICLOS)/60
    print('aguarde pelo menos '+ str(wait) +' minuto(s) no comodo '+ comodo +', coletando e processando...')
    for i in range(CICLOS): # qtd de vezes que vamos executar a coleta de dados
        wf_map = Cell.all('wlp3s0') # scanner
        wf_map = list(wf_map)
        if wf_map:
            wf_dict = map_4_dict(wf_map)# 'dict' de wifis que foram encontrados neste ciclo do scanner
            
            if 'classe' not in perssistencia[0]:
                perssistencia[0]['classe'] = [comodo]
            else:
                perssistencia[0]['classe'].append(comodo)

            if 'data_hora' not in perssistencia[0]:
                perssistencia[0]['data_hora'] = [get_data_hora()]
            else:
                perssistencia[0]['data_hora'].append(get_data_hora())

            for wifi in wf_dict:
                if str.startswith(wf_dict[wifi]['frequency'], '2'): # somente as redes WIFI 2GHZ
                    if wifi in perssistencia[0]:
                    	# o wifi ja esta no dict, só add novo valor de quality deste novo ciclo
                        perssistencia[0][wifi].append(wf_dict[wifi]['quality']) #ligados pela ordem de inserção 
                    else:
                    	#primeira vez que a rede wifi apareceu
                        zeros_a_esquerda = [0] * perssistencia[1] # [0] multiplocado pela quantidade de ciclos
                        zeros_a_esquerda.append(wf_dict[wifi]['quality']) # add qualidade 
                        perssistencia[0][wifi] = zeros_a_esquerda # cria posicao no 'dict' com seu valor

            for perssistido in perssistencia[0]:
                if perssistido not in wf_dict: # se o wifi que ja foi armazenao nao estiver com na lista de wifis atual
                    if perssistido != 'classe' and perssistido != 'data_hora':
                        perssistencia[0][perssistido].append(0) # add zero a direta, representando a falta

            perssistencia[1] += 1 # quantidade de cliclos +1

        wait -= SEGUNDOS/60
        print('Faltam pelo menos '+str(wait)+' minuto(s)...')
        time.sleep(SEGUNDOS) # tempo de esperar em cada coleta de 

    return perssistencia

def principal():
    CICLOS = 100 # quantidade de cliclos que vai executar em cada comodo
    SEGUNDOS = 3 # tempo de esperar em cada ciclo de coleta de wifis escaneados pela lib
    folder_dir = os.listdir('.') # diretorio corrente
    perssistencia = [{}, 0] # estrutura de dados dict que armazena tudo, e contador de ciclos global

    print('Digite o nome do comodo: sala, varanda, quarto')
    comodo = input()
    
    # se o 'wifi_dict.pkl' ainda nao esta criado no diretorio atual
    if 'wifi_dict.pkl' not in folder_dir: 
        dump_file(perssistencia)# crie, e inicia com o 'perssistencia' inicializado

    # carrega dados gravados no arquivo, para poder ser manipulado
    with open('wifi_dict' + '.pkl', 'rb') as f:
        perssistencia = pickle.load(f) 

    perssistencia = preenche_dict_wifis(perssistencia, SEGUNDOS, CICLOS, comodo)
    dump_file(perssistencia) # salva no arquivo

    print("____________________________ WIFI DICT ________________________________")
    print(perssistencia[0])
    print("____________________________ WIFI DataFrame ________________________________")
    #print(f"Quantidade de cliclos {perssistencia[1]}")
    df = pd.DataFrame(perssistencia[0])
    print(df)

principal()