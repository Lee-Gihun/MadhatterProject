class Node:
    def __init__(self, name, tf_idf):
        self.name = name
        self.tf_idf = tf_idf

    def get_name(self):
        return self.name

    def set_tf_idf(self, tf_idf):
        self.tf_idf = tf_idf

    def get_tf_idf(self):
        return self.tf_idf

class Graph:
    def __init__(self):
        self.node_dict = dict()

    def add_node(self, node):
        if isinstance(node, Node):
            self.node_dict[node] = dict()

    def add_edge(self, node1, node2, weight):
        """
        Edge must be added after all nodes are added to graph
        """
        if (node1 not in self.node_dict) or \
           (node2 not in self.node_dict):
               print("You need to add nodes to the graph first")
               return

        if (node1 in self.node_dict[node2]) and \
           (node2 in self.node_dict[node1]):
               print('node {} and {} are already connected'.format(node1.get_name(), node2.get_name()))
               return

        self.node_dict[node1][node2] = weight
        self.node_dict[node2][node1] = weight

    def graph_size(self):
        return len(self.node_dict)

    def print_graph(self):
        for node in self.node_dict:
            print('{}: '.format(node.get_name()), end='')
            print('{', end='')
            for neighbor in self.node_dict[node]:
                print('{}: {}, '.format(neighbor.get_name(), self.node_dict[node][neighbor]), end='')

            print('}')

    def dijkstra(self, init_node):
        """
        graph: Graph object
        init_node: Starting point in graph
        """
        if not isinstance(init_node, Node):
            print('invalid node input')
            return False

        visited = {init_node: 0}
        prev_node = {init_node: None}

        nodes = set(self.node_dict.keys())

        # start from init_node
        while nodes:
            min_neighbor = None
            for node in nodes:
                if node in visited:
                    if min_neighbor is None:
                        min_neighbor = node
                    elif visited[node] < visited[min_neighbor]:
                        min_neighbor = node

            if min_neighbor is None:
                break

            nodes.remove(min_neighbor)
            current_weight = visited[min_neighbor]

            # find neighbor and distance from this node
            for neighbor_node in self.node_dict[min_neighbor]:
                weight = current_weight + self.node_dict[min_neighbor][neighbor_node]
                if neighbor_node not in visited or weight < visited[neighbor_node]:
                    visited[neighbor_node] = weight
                    prev_node[neighbor_node] = min_neighbor

        return visited, prev_node


if __name__ == '__main__':
    graph = Graph()

    node1 = Node('a', 0)
    node2 = Node('b', 0)
    node3 = Node('c', 0)
    node4 = Node('d', 0)
    node5 = Node('e', 0)
    node6 = Node('f', 0)
    node7 = Node('g', 0)

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_node(node4)
    graph.add_node(node5)
    graph.add_node(node6)
    graph.add_node(node7)

    graph.add_edge(node1, node2, 6)
    graph.add_edge(node1, node3, 2)
    graph.add_edge(node1, node4, 16)
    graph.add_edge(node1, node7, 14)

    graph.add_edge(node2, node3, 7)
    graph.add_edge(node2, node4, 5)
    graph.add_edge(node2, node5, 4)

    graph.add_edge(node3, node5, 3)
    graph.add_edge(node3, node6, 8)

    graph.add_edge(node4, node5, 4)
    graph.add_edge(node4, node7, 3)

    graph.add_edge(node5, node7, 10)

    graph.add_edge(node6, node7, 1)

    graph.print_graph()

    visited, prev_node = graph.dijkstra(node1)
    print('=' * 20, 'Visited', '=' * 20)
    for visit_node in visited:
        print('{}: {}'.format(visit_node.get_name(), visited[visit_node]))

    print('=' * 20, 'Prev Node', '=' * 20)
    for node in prev_node:
        if prev_node[node] == None:
            print('{}: {}'.format(node.get_name(), 'None'))
        else:
            print('{}: {}'.format(node.get_name(), prev_node[node].get_name()))
