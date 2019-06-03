import csv
import json

import vector_generator
from undirected_graph import Node, Graph
from utils import champ_id_remap, get_original_champ_id
from Models.UserInspector import UserInspector

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

class ChampionGraph():
    def __init__(self, user_name):
        self.user_name = user_name
        self.champ_node_dict = self.__get_champion_node()
        self.champ_graph = self.__get_champion_graph()
        self.champ_num = len(self.champ_node_dict)

        # add champion correleation edge to graph
        self.__add_champion_edge()

        # original champion ID dictionary from Riot
        with open('./metadata/id_to_key.json', 'r') as f:
            self.original_champ_id_dict = json.load(f)

        # get champ key to name table
        with open('./metadata/key_to_id.json', 'r') as f:
            self.key_to_name = json.load(f)

    def __get_champion_node(self):
        champ_node_dict = dict()

        # read champion node data
        try:
            champ_node_file = open('./datasets/allchampions_nodes.csv', 'r')
            champ_node_reader = csv.reader(champ_node_file, delimiter=',')
        except FileNotFoundError:
            create_remapped_id_node()
            champ_node_file = open('./datasets/allchampions_nodes.csv', 'r')
            champ_node_reader = csv.reader(champ_node_file, delimiter=',')

        # skip first line
        node_column = next(champ_node_reader)

        CHAMP_NAME = 1
        for champ_node_row in champ_node_reader:
            champ_name = champ_node_row[CHAMP_NAME]
            champ_node_dict[champ_name] = Node(champ_name, 0.0)

        champ_node_file.close()

        return champ_node_dict

    def __get_champion_graph(self):
        champ_graph = Graph()

        # add champion node to graph
        for champ_name in self.champ_node_dict:
            champ_graph.add_node(self.champ_node_dict[champ_name])

        return champ_graph

    def __add_champion_edge(self):
        # read champion relationship (edge of graph) data
        champ_edge_file = open('./datasets/allchampions_edges.csv', 'r')
        champ_edge_reader = csv.reader(champ_edge_file, delimiter=',')

        # skip first line of csv file
        edge_column = next(champ_edge_reader)

        # add edge
        SOURCE_CHAMP = 0
        TARGET_CHAMP = 1
        EDGE_WEIGHT = 2
        for champ_edge_row in champ_edge_reader:
            source_champ_node = self.champ_node_dict[champ_edge_row[SOURCE_CHAMP]]
            target_champ_node = self.champ_node_dict[champ_edge_row[TARGET_CHAMP]]
            if float(champ_edge_row[EDGE_WEIGHT]) > 0:
                weight = 1.0 / float(champ_edge_row[EDGE_WEIGHT])
            else:
                weight = 100

            self.champ_graph.add_edge(source_champ_node, target_champ_node, weight)

        champ_edge_file.close()

    def __del__(self):
        pass

    def _get_user_tf_idf(self):
        user_inspector = UserInspector()
        user_data = {self.user_name: user_inspector.user_history_collector(self.user_name)}
        user_tf_idf = vector_generator.generate_user_vector(2, batch_data=user_data, to_file=False)[self.user_name]

        return user_tf_idf

    def _get_user_top_7_list(self, user_tf_idf):
        user_top_7 = list()
        remapped_champ_id_dict = champ_id_remap()
        for champ_idx, tf_idf in enumerate(user_tf_idf):
            if tf_idf != 0:
                original_key = get_original_champ_id(remapped_champ_id_dict, champ_idx)
                champ_name = self.key_to_name[str(original_key)]
                self.champ_node_dict[champ_name].set_tf_idf(tf_idf)
                user_top_7.append(champ_name)

        return user_top_7

    def _champion_dijkstra(self, user_top_7):
        top_7_distance = dict()
        for top_7_champ_name in user_top_7:
            visited, _ = self.champ_graph.dijkstra(self.champ_node_dict[top_7_champ_name])
            top_7_distance[top_7_champ_name] = visited
            #print('=' * 20, top_7_champ_name, '=' * 20)
            #for visit_node in visited:
            #    print('{}: {}'.format(visit_node.get_name(), visited[visit_node]))

        return top_7_distance

    def _get_overall_distance(self, user_top_7, top_7_distance):
        overall_distance_dict = dict()

        for champ_name, champ_node in self.champ_node_dict.items():
            if champ_name not in user_top_7:
                for top_7_champ_name, distance in top_7_distance.items():
                    # tf_idf is a TF-IDF score of this champion in top 7 champions
                    tf_idf = self.champ_node_dict[top_7_champ_name].get_tf_idf()
                    if champ_node in distance:
                        if champ_name not in overall_distance_dict:
                            overall_distance_dict[champ_name] = distance[champ_node] * tf_idf
                        else:
                            overall_distance_dict[champ_name] += distance[champ_node] * tf_idf

        return overall_distance_dict

    def _print_nearest_champion(self, overall_distance_dict):
        # sort overall distance dictionary and get the closeset one
        min_distance = 1.0e5
        nearest_champ = ''
        for champ_name, distance in overall_distance_dict.items():
            if min_distance > distance:
                min_distance = distance
                nearest_champ = champ_name

        print('nearest: {}, distance: {}'.format(nearest_champ, min_distance))

    def get_champion_distance(self):
        # get user's tf idf value for each champion
        user_tf_idf = self._get_user_tf_idf()

        # make user top 7 champions list
        user_top_7 = self._get_user_top_7_list(user_tf_idf)

        # run dijkstra algorithm for top 7 node
        top_7_distance = self._champion_dijkstra(user_top_7)

        # get overall distance using TF-IDF between top 7 champion and every other champions
        overall_distance_dict = self._get_overall_distance(user_top_7, top_7_distance)

        return overall_distance_dict

if __name__ == '__main__':
    user_name = input('Enter user name: ')
    champion_graph = ChampionGraph(user_name)
    champion_distance = champion_graph.get_champion_distance()
    print(champion_distance)
