import json
import pandas as pd
from networkx.readwrite.json_graph import node_link_data, node_link_graph
from networkx.classes.function import degree

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

#def read_json(json_name):
#    with open(json_name, 'r') as infile:
#        data = json.load(infile)
#    g = node_link_graph(data, directed=True) # directed or undirected
#    return g

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

class Graph():
    def __init__(self, list_type, list_head, dict_find):
        self.dict = {"directed": True, "multigraph": True, "graph": {}}
        self.types = pd.DataFrame(list_type, columns=['Founder', 'EDRPOU', 'Founder_part', 'Is_benef'])
        self.heads = pd.DataFrame(list_head, columns=['Head', 'EDRPOU'])
        self.dict_find = dict_find
        
    def addNodes(self):
        nodes = []
        ident = 0
        for key, value in self.dict_find.items():
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
        other = set(self.types['Founder']) - (set([x['name'] for x in nodes]) | set([x['edrpou'] for x in nodes]))
        #ident = len(nodes)
        for item in other:
            ident += 1
            nodes.append({'id': ident, 'colour': 'black', 'name': item, 'edrpou': ''})
        self.dict["nodes"] = nodes
    
    def addLinks(self):
        df_nodes = pd.DataFrame(self.dict["nodes"])
        df_nodes['value'] = df_nodes[['name', 'edrpou']].apply(
            lambda x: x['edrpou'] if x['edrpou'] != '' else x['name'], axis=1)
        df_nodes = df_nodes[['id', 'value']]
        df_types = self.types.merge(df_nodes.rename(columns={'value': 'Founder'}), 
                                    how='left', on='Founder').rename(columns={'id': 'source'})
        df_types = df_types.merge(df_nodes.rename(columns={'value': 'EDRPOU'}), 
                                  how='left', on='EDRPOU').rename(columns={'id': 'target'})
        df_types['type'] = df_types['Founder_part'].apply(lambda x: relation_type(x))
        df_ben = df_types[df_types['Is_benef'] == 1][['source', 'target']].reset_index(drop=True)
        df_ben['type'] = 'benef'
        df_types = df_types[['source', 'target', 'type']]
        df_heads = self.heads.merge(df_nodes[['id', 'value']].rename(columns={'value': 'Head'}), 
                                  how='left', on='Head').rename(columns={'id': 'source'})
        df_heads = df_heads.merge(df_nodes[['id', 'value']].rename(columns={'value': 'EDRPOU'}), 
                                  how='left', on='EDRPOU').rename(columns={'id': 'target'}) 
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
        self.dict["links"] = links
    
    def createJson(self, name='../json/graph.json'):
        G = node_link_graph(self.dict, directed=True)
        G = nodes_degree(G)
        write_json(G, name)
        

#tests
if __name__ == '__main__':
    from ring_parser import Parser # for testing only
    from card_processor import Processor # for testing only
    start = '36492837' # "Бон Буассон"
    parser = Parser(start)
    processor = Processor(parser.getData()[1][0]) # для прикладу беремо першу зі списку знайдених фірм
    # на вхід подаємо dict_find, dict_firm, list_type, list_head, list_temp, list_next
    result = processor.addCardData(dict(), dict(), [], [], [(start, 0)], [], False)
    # на вхід подаємо list_type, list_head, dict_find
    graph = Graph(result[2], result[3], result[0])
    graph.addNodes()
    graph.addLinks()
    graph.createJson('../json/graph_proba.json')