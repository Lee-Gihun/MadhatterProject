import csv
import json
from undirected_graph import Node, Graph
from utils import champ_id_remap, get_original_champ_id
from Models.UserInspector import UserInspector
from vector_generator import generate_user_vector

def create_remapped_id_node():
    champion_node_old_file = open('./datasets/allchampions_old_nodes.csv', 'r')
    champion_node_old_reader = csv.reader(champion_node_old_file, delimiter=',')
    champion_node_file = open('./datasets/allchampions_nodes.csv', 'w')
    champion_node_writer = csv.writer(champion_node_file, delimiter=',')

    node_old_column = next(champion_node_old_reader)

    remapped_champ_id_dict = champ_id_remap()

    CHAMP_NAME = 1
    champion_node_writer.writerow(['Id', 'Label'])
    for node_old_row in champion_node_old_reader:
        champ_name = node_old_row[CHAMP_NAME]
        original_champ_id = original_champ_id_dict[champ_name]
        remapped_champ_id = remapped_champ_id_dict[original_champ_id]

        champion_node_writer.writerow([remapped_champ_id, champ_name])

    champion_node_old_file.close()
    champion_node_file.close()

if __name__ == '__main__':
    with open('./metadata/id_to_key.json', 'r') as f:
        original_champ_id_dict = json.load(f)

    try:
        champ_node_file = open('./datasets/allchampions_nodes.csv', 'r')
        champ_node_reader = csv.reader(champ_node_file, delimiter=',')
    except FileNotFoundError:
        create_remapped_id_node()
        champ_node_file = open('./datasets/allchampions_nodes.csv', 'r')
        champ_node_reader = csv.reader(champ_node_file, delimiter=',')

    champ_edge_file = open('./datasets/allchampions_edges.csv', 'r')
    champ_edge_reader = csv.reader(champ_edge_file, delimiter=',')

    node_column = next(champ_node_reader)
    edge_column = next(champ_edge_reader)


    # read user tf idf values
    with open('./datasets/user_vectors_tf_idf.json', 'r') as f:
        user_vectors = json.load(f)

    # get champ key to name table
    with open('./metadata/key_to_id.json', 'r') as f:
        key_to_name = json.load(f)

    # make champion node
    CHAMP_NAME = 1
    champ_node_dict = dict()
    for champ_node_row in champ_node_reader:
        champ_name = champ_node_row[CHAMP_NAME]
        champ_node_dict[champ_name] = Node(champ_name, 0.0)

    # get user's tf idf value for each champion
    user_name = input('Enter user name: ')
    user_inspector = UserInspector()
    user_data = {user_name: user_inspector.user_history_collector(user_name)}
    champ_num = len(champ_node_dict)
    user_tf_idf = generate_user_vector(2, batch_data=user_data, to_file=False)[user_name]

    user_top_7 = list()
    remapped_champ_id_dict = champ_id_remap()
    for champ_idx, tf_idf in enumerate(user_tf_idf):
        if tf_idf != 0:
            original_key = get_original_champ_id(remapped_champ_id_dict, champ_idx)
            champ_name = key_to_name[str(original_key)]
            champ_node_dict[champ_name].set_tf_idf(tf_idf)
            user_top_7.append(champ_name)

    # make champion graph
    champ_graph = Graph()
    for champ_name in champ_node_dict:
        champ_graph.add_node(champ_node_dict[champ_name])

    # add edge between champion node
    SOURCE_CHAMP = 0
    TARGET_CHAMP = 1
    EDGE_WEIGHT = 2
    for champ_edge_row in champ_edge_reader:
        source_champ_node = champ_node_dict[champ_edge_row[SOURCE_CHAMP]]
        target_champ_node = champ_node_dict[champ_edge_row[TARGET_CHAMP]]
        if float(champ_edge_row[EDGE_WEIGHT]) > 0:
            weight = 1.0 / float(champ_edge_row[EDGE_WEIGHT])
        else:
            weight = 100

        champ_graph.add_edge(source_champ_node, target_champ_node, weight)


    # run dijkstra algorithm for top 7 node
    top_7_distance = dict()
    for top_7_champ_name in user_top_7:
        visited, _ = champ_graph.dijkstra(champ_node_dict[top_7_champ_name])
        top_7_distance[top_7_champ_name] = visited
        #print('=' * 20, top_7_champ_name, '=' * 20)
        #for visit_node in visited:
        #    print('{}: {}'.format(visit_node.get_name(), visited[visit_node]))

    # get average distance using TF-IDF between top 7 champion and every other champions
    overall_distance_dict = dict()
    for champ_name, champ_node in champ_node_dict.items():
        if champ_name not in user_top_7:
            for top_7_champ_name, distance in top_7_distance.items():
                # tf_idf is a TF-IDF score of this champion in top 7 champions
                tf_idf = champ_node_dict[top_7_champ_name].get_tf_idf()
                if champ_node in distance:
                    if champ_name not in overall_distance_dict:
                        overall_distance_dict[champ_name] = distance[champ_node] * tf_idf
                    else:
                        overall_distance_dict[champ_name] += distance[champ_node] * tf_idf
                #else:
                #    print('{} is not connected with {}'.format(champ_name, top_7_champ_name))

    # sort overall distance dictionary and get the closeset one
    min_distance = 1.0e5
    nearest_champ = ''
    for champ_name, distance in overall_distance_dict.items():
        if min_distance > distance:
            min_distance = distance
            nearest_champ = champ_name

    print('nearest: {}, distance: {}'.format(nearest_champ, min_distance))

    champ_node_file.close()
    champ_edge_file.close()
