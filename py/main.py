import pandas as pd
import json
from networkx.readwrite.json_graph import node_link_data, node_link_graph
from networkx.classes.function import degree
from ring_parser import Parser
from card_processor import Processor

# словник кольорів для вершин-юросіб
dict_colours = {'припинено': 'red', 'в стані припинення': 'orange', 
                'зареєстровано, свідоцтво про державну реєстрацію недійсне': 'yellow', 
                'зареєстровано': 'green', 'скасовано': 'blue'}
# словник кольорів для типів зв'язків
dict_colors = {'benef': 'magenta', 'high': 'red', 'medium': 'yellow', 'small': 'green', 'undefined': 'black', 'head': 'blue'}

def relation_type(part):
    if part >= 0.5:
        return 'high'
    elif part >= 10:
        return 'medium'
    elif part > 0:
        return 'small'
    else:
        return 'undefined'
    
def read_json(json_name):
    with open(json_name, 'r') as infile:
        data = json.load(infile)
    g = node_link_graph(data, directed=True) # directed or undirected
    return g

def write_json(g, json_name, graph=True):
    if graph:
        g = node_link_data(g)
    with open(json_name, 'w') as outfile:
        json.dump(g, outfile)
        
def nodes_degree(g):
    dct = dict(degree(g.to_undirected()))
    for i in dct:
        g.nodes[i]['degree'] = dct[i]
    return g

def main(start, level):
    # задаємо початкові значення словників та списків
    dict_find = dict() # словник знайдених контрагентів
    dict_firm = dict() # словник назва фірми --> ЄДРПОУ
    list_type = [] # список зв'язків між знайденими контрагентами
    list_head = [] # список голів фірм
    list_temp = [] # список контрагентів на поточному рівні
    list_next = [] # список контрагентів наступного рівня -- кортежі: назва фірми або П.І.Б., регіон (-1 для фірми)
    i = 0 # лічильник (номер рівня відносно початкового об'єкта)
    # запускаємо процес (цикл із передумовою, обмеження за кількістю рівнів)
    list_next.append((start, 0)) # 0 -- для вказівки на те, що нам не важливо, з якого регіону дана фірма
    while (i < level) and (len(list_next) > 0):
        list_temp = list_next.copy()
        list_next = []
        for obj in list_temp:
            parser = Parser(obj[0]) # ініціюємо парсер
            resp = parser.getData() # витягуємо з сайту ring.org.ua дані по даному об'єкту
            num = resp[0] # кількість знайдених фірм, пов'язаних із даним об'єктом (ЄДРПОУ, назва фірми, П.І.Б.)
            if num != 0:
                list_obj = resp[1] # список даних по знайдених фірмах
                for n in range(num):
                    edrpou = list_obj[n]['full_edrpou'] # підтягуємо ЄДРПОУ фірми (що робити, якщо його немає?)
                    if edrpou not in set(dict_find.keys()): # якщо ми ще не обробляли інформацію про дану фірму
                        if obj[1] == -1: # додаємо інформацію про засновників фірми та нові об'єкти для пошуку
                            # тут передаємо другим аргументом для перевірки рядок -- назву фірми
                            processor = Processor(list_obj[n], obj[0]) # ініціюємо обробник картки фірми
                        elif len(obj) == 2: # додаємо те ж саме, тільки для фірм із певної області
                            # тут передаємо другим аргументом ціле число -- номер регіону (або 0)
                            processor = Processor(list_obj[n], obj[1]) # ініціюємо обробник картки фірми
                        else: # а тут додаємо третім аргументом ще й адресу засновника
                            processor = Processor(list_obj[n], obj[1], obj[2]) # ініціюємо обробник картки фірми
                        dict_find, dict_firm, list_type, list_head, list_next = processor.addCardData(
                            dict_find, dict_firm, list_type, list_head, list_temp, list_next) # обробляємо картку
            else:
                if resp[1] == ['error']:
                    print('Error request for object = ', obj[0])
        i += 1
    # після формування словників та списків здійснюємо їх обробку, формуємо граф і записуємо його до json-файлу
    G = {"directed": True, "multigraph": True, "graph": {}}
    df_types = pd.DataFrame(list_type, columns=['Founder', 'EDRPOU', 'Founder_part', 'Is_benef'])
    df_heads = pd.DataFrame(list_head, columns=['Head', 'EDRPOU'])
    nodes = []
    ident = 0
    for key, value in dict_find.items():
        ident += 1
        if len(value) > 0: # знайдений контрагент -- юрособа
            edrpou = key
            name = value[1]
            colour = dict_colours[value[2]]
        else: # знайдений контрагент -- фізособа
            edrpou = ''
            name = key
            colour = 'white'
        nodes.append({'id': ident, 'colour': colour, 'name': name, 'edrpou': edrpou})
    other = set(df_types['Founder']) - (set([x['name'] for x in nodes]) | set([x['edrpou'] for x in nodes]))
    #ident = len(nodes)
    for item in other:
        ident += 1
        nodes.append({'id': ident, 'colour': 'black', 'name': item, 'edrpou': ''})
    G["nodes"] = nodes
    df_nodes = pd.DataFrame(nodes)
    df_nodes['value'] = df_nodes[['name', 'edrpou']].apply(
        lambda x: x['edrpou'] if x['edrpou'] != '' else x['name'], axis=1)
    df_nodes = df_nodes[['id', 'value']]
    df_types = df_types.merge(df_nodes.rename(columns={'value': 'Founder'}), how='left', on='Founder').rename(
        columns={'id': 'source'})
    df_types = df_types.merge(df_nodes.rename(columns={'value': 'EDRPOU'}), how='left', on='EDRPOU').rename(
        columns={'id': 'target'})
    df_types['type'] = df_types['Founder_part'].apply(lambda x: relation_type(x))
    df_ben = df_types[df_types['Is_benef'] == 1][['source', 'target']].reset_index(drop=True)
    df_ben['type'] = 'benef'
    df_types = df_types[['source', 'target', 'type']]
    df_heads = df_heads.merge(df_nodes[['id', 'value']].rename(columns={'value': 'Head'}), how='left', on='Head').rename(
        columns={'id': 'source'})
    df_heads = df_heads.merge(df_nodes[['id', 'value']].rename(columns={'value': 'EDRPOU'}), how='left', on='EDRPOU').rename(
        columns={'id': 'target'}) 
    df_heads = df_heads[['source', 'target']]
    df_heads['type'] = 'head'
    df_type = pd.concat([df_types, df_ben, df_heads], ignore_index=True)
    df_type = df_type.sort_values(by=['source', 'target']).reset_index(drop=True)
    df_type['color'] = df_type['type'].map(dict_colors)
    keys = [0]
    key = 0
    source = df_type['source'][0]
    target = df_type['target'][0]
    for i in range(1, len(df_type)):
        source_new = df_type['source'][i]
        target_new = df_type['target'][i]
        if (target_new == target) and (source_new == source):
            key += 1
        else:
            key = 0
        keys.append(key)
        source = source_new
        target = target_new
    df_type['key'] = keys
    links = []
    for i in range(len(df_type)): # for JSON, type of integers must be int, not int64!!!
        links.append({'source': int(df_type['source'][i]), 'target': int(df_type['target'][i]), 
                      'color': df_type['color'][i], 'key': int(df_type['key'][i])})
    G["links"] = links
    write_json(G, '../json/graph.json', graph=False)
    G = read_json('../json/graph.json')
    G = nodes_degree(G)
    write_json(G, '../json/graph.json')
    
    
# testing
if __name__ == '__main__':
    main('31382665', 3)