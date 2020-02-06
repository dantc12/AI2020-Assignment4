class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_debug(s):
    # return None
    ss = str(s)
    if ss.find("HURRICANE") > -1:
        print bcolors.FAIL + "DEBUG:   " + ss + bcolors.ENDC
    elif ss.find("TERM") > -1 or ss.find("BLOCK") > -1:
        print bcolors.WARNING + "DEBUG:   " + ss + bcolors.ENDC
    elif ss.find("PICK") > -1 or ss.find("DROP") > -1 or ss.find("ARRIV") > -1 or ss.find("GOAL") > -1:
        print bcolors.OKGREEN + "DEBUG:   " + ss + bcolors.ENDC
    else:
        print bcolors.OKBLUE + "DEBUG:   " + ss + bcolors.ENDC


def print_info(s):
    print "INFO:    " + str(s)


def print_query(s):
    print "QUERY:   " + str(s)


# def get_min_index(arr):
#     min_index = 0
#     min_val = arr[0]
#     for i in range(1, len(arr)):
#         if arr[i] < min_val:
#             min_index = i
#             min_val = arr[i]
#     return min_index


def TrueFalseArrayCombinations(length):
    if length == 0:
        return []
    elif length == 1:
        return [["T"], ["F"]]
    else:
        res = []
        shorter_combs = TrueFalseArrayCombinations(length - 1)
        for comb in shorter_combs:
            res += [comb + ["T"], comb + ["F"]]
        return res

# def dijkstra(g, source_vertex):
#     """
#     :type g: graph.Graph
#     :type source_vertex: graph.Vertex
#     """
#     # Get index of source_vertex (or maintain int passed in)
#     source_vertex_index = source_vertex.index-1
#     # Make an array keeping track of distance from source_vertex to any source_vertex
#     # in g.vertices. Initialize to infinity for all vertices but the
#     # starting source_vertex, keep track of "path" which relates to distance.
#     # Index 0 = distance, index 1 = source_vertex hops
#     dist = [0] * len(g.vertices)  # type: list[int]
#     paths = [[0]] * len(g.vertices)  # type: list[list[int]]
#     for i in range(len(dist)):
#         dist[i] = float("inf")
#         paths[i] = [g.vertices[source_vertex_index]]
#
#     dist[source_vertex_index] = 0
#     # Queue of all vertices in the graph
#     # Note the integers in the queue correspond to indices of vertex
#     # locations in the g.vertices array
#     queue = [i for i in range(len(g.vertices))]
#     # Set of numbers seen so far
#     seen = set()
#     while len(queue) > 0:
#         # Get vertex in queue that has not yet been seen
#         # that has smallest distance to starting source_vertex
#         min_dist = float("inf")
#         min_vertex_index = -1
#         for n in queue:
#             if dist[n] < min_dist and n not in seen:
#                 min_dist = dist[n]
#                 min_vertex_index = n
#
#         if min_vertex_index == -1:
#             break
#         # Add min distance source_vertex to seen, remove from queue
#         queue.remove(min_vertex_index)
#         seen.add(min_vertex_index)
#         # Get all next hops
#         connected_vertices = g.vertices[min_vertex_index].get_connected_vertices_with_weights()
#         # For each connection, update its path and total distance from
#         # source_vertex if the total distance is less than the current distance
#         # in dist array
#         for (vertex, weight) in connected_vertices:
#             tot_dist = weight + min_dist
#             if tot_dist < dist[vertex.index-1]:
#                 dist[vertex.index-1] = tot_dist
#                 paths[vertex.index-1] = list(paths[min_vertex_index])
#                 paths[vertex.index-1].append(vertex)
#     return dist, paths
#
#
# def dijkstra_without_graph(source_vertex, v_count):
#     """
#     :type v_count: int
#     :type source_vertex: graph.Vertex
#     """
#     # Get index of source_vertex (or maintain int passed in)
#     source_vertex_index = source_vertex.index-1
#     # Make an array keeping track of distance from source_vertex to any source_vertex
#     # in g.vertices. Initialize to infinity for all vertices but the
#     # starting source_vertex, keep track of "path" which relates to distance.
#     # Index 0 = distance, index 1 = source_vertex hops
#     dist = [0] * v_count  # type: list[int]
#     paths = [[0]] * v_count  # type: list[list[int]]
#     g_vertices = [0] * v_count
#     g_vertices[source_vertex.index-1] = source_vertex
#     for i in range(len(dist)):
#         dist[i] = float("inf")
#         paths[i] = [source_vertex]
#
#     dist[source_vertex_index] = 0
#     # Queue of all vertices in the graph
#     # Note the integers in the queue correspond to indices of vertex
#     # locations in the g.vertices array
#     queue = [i for i in range(v_count)]
#     # Set of numbers seen so far
#     seen = set()
#     while len(queue) > 0:
#         # Get vertex in queue that has not yet been seen
#         # that has smallest distance to starting source_vertex
#         min_dist = float("inf")
#         min_vertex_index = -1
#         for n in queue:
#             if dist[n] < min_dist and n not in seen:
#                 min_dist = dist[n]
#                 min_vertex_index = n
#
#         if min_vertex_index == -1:
#             break
#         # Add min distance source_vertex to seen, remove from queue
#         queue.remove(min_vertex_index)
#         seen.add(min_vertex_index)
#         # Get all next hops
#         # print_debug(str([str(v) for v in g_vertices]))
#         connected_vertices = g_vertices[min_vertex_index].get_connected_vertices_with_weights()
#         for v, w in connected_vertices:
#             g_vertices[v.index-1] = v
#         # For each connection, update its path and total distance from
#         # source_vertex if the total distance is less than the current distance
#         # in dist array
#         for (vertex, weight) in connected_vertices:
#             tot_dist = weight + min_dist
#             if tot_dist < dist[vertex.index-1]:
#                 dist[vertex.index-1] = tot_dist
#                 paths[vertex.index-1] = list(paths[min_vertex_index])
#                 paths[vertex.index-1].append(vertex)
#     return g_vertices, dist, paths
