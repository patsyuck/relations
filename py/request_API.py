# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 14:47:41 2021
Здійснює пошук групи контрагентів, її редагування та візуалізацію
@author: o.patsiuk
"""
import pandas as pd
import networkx as nx
#from networkx.readwrite.edgelist import read_edgelist
from networkx.readwrite.json_graph import node_link_data, node_link_graph
from networkx.classes.function import subgraph, degree
from networkx.algorithms.components import node_connected_component
#from networkx.algorithms.operators.binary import union
#import matplotlib.pyplot as plt
import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

def read_json(json_name):
    with open(json_name, 'r') as infile:
        data = json.load(infile)
    g = node_link_graph(data, directed=True) # directed or undirected
    return g

def write_json(g, json_name):
    data = node_link_data(g)
    with open(json_name, 'w') as outfile:
        json.dump(data, outfile)

def get_subgraph(g, prop, value):
    if prop == "group_name" or prop == "group":
        nodes = []
        for node in list(g.nodes):
            if g.nodes[node][prop] == value:
                nodes.append(node)
        return g.subgraph(nodes)
    else: # цю гілку ретельно переглянути, дописати try..except
        labels = {}
        for item, data in g.nodes(data=True):
            if data[prop] != None:
                labels[data[prop]] = item
        node = labels[value] # для prop=="name" доробити lowercase
        return subgraph(g, node_connected_component(g.to_undirected(), node))

def nodes_color(g):
    data = pd.read_excel('../excel/dict/colours_dict.xlsx')
    dict_colour = dict(zip(data.colour_code, data.colour))
    for i in list(g.nodes):
        g.nodes[i]['colour'] = dict_colour[g.nodes[i]['colour']]
    return g

def nodes_degree(g):
    dct = dict(degree(g.to_undirected()))
    for i in dct:
        g.nodes[i]['degree'] = dct[i]
    return g

def name2node(g, name):
    for node in list(g.nodes):
        if g.nodes[node]["name"] == name:
            return node
    return None

def code2node(g, code):
    for node in list(g.nodes):
        if g.nodes[node]["code"] == code:
            return node
    return None

def okpo2node(g, okpo):
    for node in list(g.nodes):
        if g.nodes[node]["okpo"] == okpo:
            return node
    return None

# зробити так, щоб назва групи запам'ятовувалась при пошуку або створенні
def add_item(g, group_name, name, code, okpo, vis=True):
    dict_group = pd.read_excel('../excel/dict/groups_dict.xlsx')
    group = int(dict_group[dict_group['group_name'] == group_name]['group'])
    nodes = []
    for node in list(g.nodes):
        if g.nodes[node]['group_name'] == group_name:
            nodes.append(int(node.split('_')[-1]))
    if nodes != []:
        id_new = max(nodes) + 1
    else:
        id_new = 1
    g.add_node(group_name + '_' + str(id_new), group=group, group_name=group_name, colour='white', name=name, 
               code=code, okpo=okpo, degree=0)
    if vis:
        write_json(g, '../user/subgraph.json') # оновлюємо підграф юзера

def add_link(g, node_output, node_input, link, dict_color, vis=True):
    if node_output in list(g.nodes) and node_input in list(g.nodes):
        g.add_edge(node_output, node_input, link=link, color=dict_color[link], 
            key=sum([1 if v == node_input else 0 for (u, v) in list(g.edges([node_output]))]))
        if link in ["family", "address", "business"]:
            g.add_edge(node_input, node_output, link=link, color=dict_color[link], 
                key=sum([1 if v == node_output else 0 for (u, v) in list(g.edges([node_input]))]))
        if vis:
            g = nodes_degree(g)
            write_json(g, '../user/subgraph.json') # оновлюємо підграф юзера
    else:
        if node_output not in list(g.nodes):
            print('Спочатку додайте контрагента {0} до групи!'.format(node_output))
        if node_input not in list(g.nodes):
            print('Спочатку додайте контрагента {0} до групи!'.format(node_input))

def remove_item(g, node, vis=True):
    lst = nx.all_neighbors(g, node)
    g.remove_node(node)
    if vis:
        g = nodes_degree(g)
        lst_del = [item for item in set(lst) if g.nodes[item]['degree'] == 0]
        for item in lst_del:
            g.remove_node(item)
        write_json(g, '../user/subgraph.json') # оновлюємо підграф юзера
    else:
        dct = dict(degree(g.to_undirected()))
        lst_del = [item for item in set(lst) if dct[item] == 0]
        for item in lst_del:
            g.remove_node(item)

def remove_link(g, node_output, node_input, link, vis=True, remove_nodes=True):
    if link != "all":
        for i in range(max([w for (u, v, w) in list(g.edges) if u == node_output and v == node_input]) + 1):
            if g.edges[node_output, node_input, i]["link"] == link:
                g.remove_edge(node_output, node_input, key=i)
                break
        if link in ["family", "address", "business"]:
            for i in range(max([w for (u, v, w) in list(g.edges) if u == node_input and v == node_output]) + 1):
                if g.edges[node_input, node_output, i]["link"] == link:
                    g.remove_edge(node_input, node_output, key=i)
                    break
    else:
        for i in range(max([w for (u, v, w) in list(g.edges) if u == node_output and v == node_input]) + 1):
            g.remove_edge(node_output, node_input, key=i)
        second_list = [w for (u, v, w) in list(g.edges) if u == node_input and v == node_output]
        if second_list != []:
            for i in range(max(second_list) + 1):
                g.remove_edge(node_input, node_output, key=i)
    if vis:
        g = nodes_degree(g)
        if remove_nodes:
            if g.nodes[node_output]['degree'] == 0:
                remove_item(g, node_output, vis)
            if g.nodes[node_input]['degree'] == 0:
                remove_item(g, node_input, vis)
        write_json(g, '../user/subgraph.json') # оновлюємо підграф юзера
    else:
        if remove_nodes:
            dct = dict(degree(g.to_undirected()))
            if dct[node_output] == 0:
                remove_item(g, node_output, vis)
            if dct[node_input] == 0:
                remove_item(g, node_input, vis)

def change_link(g, node_output, node_input, link_old, link_new, dict_color, vis=True):
    remove_link(g, node_output, node_input, link_old, vis, remove_nodes=False)
    add_link(g, node_output, node_input, link_new, dict_color, vis)
    if vis:
        write_json(g, '../user/subgraph.json') # оновлюємо підграф юзера

def save_changes(dict_color):
    g = read_json('../json/graph.json')
    if os.path.exists('../json/graph_old.json'):
        os.remove('../json/graph_old.json')
    os.rename('../json/graph.json', '../json/graph_old.json')
    with open('../user/temp.jsonl', 'r', encoding='utf-8') as json_file:
        json_list = list(json_file)
    for json_str in json_list:
        request = json.loads(json_str)
        if request["operation"] == "add_item":
            add_item(g, request["group"], request["name"], request["code"], request["okpo"], vis=False)
        elif request["operation"] == "add_link":
            add_link(g, request["node1"], request["node2"], request["link"], dict_color, vis=False)
        elif request["operation"] == "remove_item":
            remove_item(g, request["node"], vis=False)
        elif request["operation"] == "remove_link":
            remove_link(g, request["node1"], request["node2"], request["link"], vis=False)
        elif request["operation"] == "change":
            change_link(g, request["node1"], request["node2"], request["link1"], request["link2"], dict_color, vis=False)
        #else:
        #    print('Error! Such an operation does not exist.')
    write_json(g, '../json/graph.json')
    os.remove('../user/subgraph.json') # очищуємо каталог юзера
    os.remove('../user/temp.jsonl') # очищуємо каталог юзера

# на майбутнє -- пошук периметру (зафарбувати вершини в певний колір?)
        
@app.route('/', methods=['POST', 'GET'])
def main():
    posted = request.get_json()
    colors = pd.read_excel('../excel/dict/colors_dict.xlsx')
    dict_color = dict(zip(colors.link, colors.color)) # кольори ребер
    if posted["action"] == "search":
        prop = posted["property"]
        value = posted["value"]
        try:
            g = read_json('../json/graph.json') # зчитуємо весь граф
            if value != "all": # якщо шукаємо тільки заданий підграф
                g = get_subgraph(g, prop, value)
            # на майбутнє -- відразу замінити назви кольорів на "людські"
            g = nodes_color(g) # розфарбовуємо вершини
            g = nodes_degree(g) # обчислюємо степені вершин
            write_json(g, '../user/subgraph.json') # підграф для юзера
            open('../user/temp.jsonl', 'w').close() # файл для запитів
            ret = {'Status code': 200}
        except:
            ret = {'Status code': 500}
        return jsonify(ret)
    elif posted["action"] == "create":
        try: # треба перевіряти, чи не існує групи з такою ж назвою
            dict_group = pd.read_excel('../excel/dict/groups_dict.xlsx')
            group = max(dict_group['group'])
            dict_group = dict_group.append(
                {'group': group + 1, 'group_name': posted["group_name"]}, 
                ignore_index=True)
            dict_group.to_excel('../excel/dict/groups_dict.xlsx', index=False)
            g = nx.MultiDiGraph()
            write_json(g, '../user/subgraph.json') # файл для графа групи
            open('../user/temp.jsonl', 'w').close() # файл для запитів
            ret = {'Status code': 200}
        except:
            ret = {'Status code': 500}
        return jsonify(ret)
    elif posted["action"] == "editing":
        operation = posted["operation"]
        if operation != "save": # додаємо запит юзера до списку змін
            with open('../user/temp.jsonl', 'a', encoding='utf-8') as file:
                json.dump(posted, file)
                file.write('\n')
        # переходимо до обробки запиту і візуалізації зміни на підграфі
        g = read_json('../user/subgraph.json') # зчитуємо підграф юзера
        if operation == "add_item": # {add_item, group_name, name, code, okpo}
            try:
                add_item(g, posted["group"], posted["name"], posted["code"], posted["okpo"])
                ret = {'Status code': 200}
            except:
                ret = {'Status code': 500}
        elif operation == "add_link": # {add_link, item_1, item_2, link, one-sided/two-sided}
            try:
                add_link(g, posted["node1"], posted["node2"], posted["link"], dict_color)
                ret = {'Status code': 200}
            except:
                ret = {'Status code': 500}
        elif operation == "remove_item": # {remove_item, item} = remove(item) + remove(all its links)
            try:
                remove_item(g, posted["node"])
                ret = {'Status code': 200}
            except:
                ret = {'Status code': 500}
        elif operation == "remove_link": # {remove_link, item_1, item_2, link}
            try:
                remove_link(g, posted["node1"], posted["node2"], posted["link"])
                ret = {'Status code': 200}
            except:
                ret = {'Status code': 500}
        elif operation == "change": # {change, item_1, item_2, link_old, link_new} = remove_link(link_old) + add_link(link_new)
            try:
                change_link(g, posted["node1"], posted["node2"], posted["link1"], posted["link2"], dict_color)
                ret = {'Status code': 200}
            except:
                ret = {'Status code': 500}
        elif operation == "save": # {save} -- оновлюємо весь граф
            try:
                save_changes(dict_color)
                ret = {'Status code': 200}
            except:
                ret = {'Status code': 500}
        else:
            ret = {'Status code': 500}
        return jsonify(ret)
    else:
        print('Such action does not exist')
        ret = {'Status code': 500}
        return jsonify(ret)


if __name__ == '__main__':
    app.run(debug=False)
    #app.run(host='0.0.0.0', debug=False)