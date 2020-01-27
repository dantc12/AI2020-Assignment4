from copy import copy


class Vertex:
    def __init__(self, index, deadline, v_type, ppl_count=0, graph=None):
        self.index = index  # type: int
        self.deadline = deadline  # type: int
        # is 'S' if it's a shelter, is 'P' if people location:
        self.v_type = v_type  # type: str
        self.ppl_count = ppl_count  # type: int
        self.connected_edges = []  # type: list[Edge]
        self.graph = graph

    def add_edge(self, edge):
        self.connected_edges.append(edge)

    def pick_up(self):
        if self.is_shelter():
            raise Exception('Tried to pick up from a shelter!')
        else:
            num_of_ppl = self.ppl_count
            self.ppl_count = 0
            return num_of_ppl

    def drop_off(self, ppl_count):
        if not self.is_shelter():
            raise Exception('Tried to drop off at non shelter!')
        else:
            self.ppl_count = self.ppl_count + ppl_count
        return self.ppl_count

    def is_shelter(self):
        return self.v_type == 'S'

    def is_ppl_location(self):
        return self.v_type == 'P'

    def get_connected_vertices(self):
        res = []
        for e in self.connected_edges:
            if e.vertex_1 == self:
                res.append(e.vertex_2)
            else:
                res.append(e.vertex_1)
        return res

    def get_connected_vertices_with_weights(self):
        res = []
        for e in self.connected_edges:
            if e.vertex_1 == self:
                res.append((e.vertex_2, e.weight))
            else:
                res.append((e.vertex_1, e.weight))
        return res

    def __str__(self):
        return "V" + str(self.index)

    def __eq__(self, other):
        return self.index == other.index


class Edge:
    def __init__(self, index, vertex_1, vertex_2, weight):
        self.index = index
        self.vertex_1 = vertex_1  # type: Vertex
        self.vertex_2 = vertex_2  # type: Vertex
        self.weight = weight
        self.is_blocked = False

    def block_road(self):
        self.is_blocked = True

    def __str__(self):
        return "E" + str(self.index)

    def __eq__(self, other):
        return self.index == other.index


class Graph:
    def __init__(self, file_path):
        self.vertices = []  # type: list[Vertex]
        self.edges = []  # type: list[Edge]
        self.number_of_vertices = 0

        # Reading configuration file
        f = open(file_path, "r")
        for line in f:
            if line[0] == '#':
                line_info = line.split('  ')[0][1:]
                line_info_split = line_info.split(' ')
                if line_info[0] == 'N':  # N x
                    n = int(line_info_split[1])
                elif line_info[0] == 'V':  # Vx Dx S|Px
                    vertex_index = int(line_info_split[0][1:])  # Vx
                    vertex_deadline = int(line_info_split[1][1:])  # Dx
                    vertex_type = line_info_split[2]  # S or Px
                    if vertex_type[0] == 'P':
                        vertex_ppl_count = int(vertex_type[1:])
                        vertex_type = 'P'
                    else:
                        vertex_ppl_count = 0
                        vertex_type = vertex_type[0]  # 'S'
                    self.vertices.append(Vertex(vertex_index, vertex_deadline, vertex_type, vertex_ppl_count, self))
                elif line_info[0] == 'E':  # Ex x x Wx
                    edge_index = int(line_info_split[0][1:])  # Ex
                    edge_v1_index = int(line_info_split[1])  # x
                    edge_v2_index = int(line_info_split[2])  # x
                    edge_weight = int(line_info_split[3][1:])  # Wx
                    e = Edge(edge_index, self.vertices[edge_v1_index-1], self.vertices[edge_v2_index-1], edge_weight)
                    self.edges.append(e)
                    self.vertices[edge_v1_index-1].add_edge(e)
                    self.vertices[edge_v2_index-1].add_edge(e)

        f.close()
        if n != len(self.vertices):
            raise Exception("N is different from number of actual vertices.")

    def num_of_roads(self):
        return len(self.edges)

    def num_of_vertices(self):
        return len(self.vertices)

    def get_edge(self, v1, v2):
        for e in self.edges:
            if e.vertex_1 == v1 and e.vertex_2 == v2:
                return e
            elif e.vertex_2 == v1 and e.vertex_1 == v2:
                return e
        raise Exception("No edge between " + str(v1) + " and " + str(v2) + ".")

    def get_edge_from_string(self, str_e):
        e_index = int(str_e[1:])
        return self.edges[e_index-1]

    def get_vertex_from_string(self, str_v):
        v_index = int(str_v[1:])
        return self.vertices[v_index-1]

    def remove_blocked_edges(self):
        tmp_edges = copy(self.edges)
        for e in tmp_edges:
            if e.is_blocked:
                e.vertex_1.connected_edges.remove(e)
                e.vertex_2.connected_edges.remove(e)
                self.edges.remove(e)

    @staticmethod
    def get_connected_edges(v):
        return v.connected_edges

    @staticmethod
    def is_connected_edge(e, v):
        return e.vertex_1 == v or e.vertex_2 == v

    def get_people_array(self):
        res = [0] * len(self.vertices)
        for v in self.vertices:
            if not v.is_shelter():
                res[v.index-1] = v.ppl_count
        return res

    def get_people_array_with_shelter(self):
        res = [0] * len(self.vertices)
        for v in self.vertices:
            res[v.index-1] = v.ppl_count
        return res

    def __str__(self):
        s = str(self.vertices[0]) + "(D" + str(self.vertices[0].deadline) + ", "
        if self.vertices[0].is_shelter():
            s = s + str(self.vertices[0].v_type)
        else:
            s = s + "P" + str(self.vertices[0].ppl_count)
        s = s + ")"
        for v in self.vertices[1:]:
            s = s + ", " + str(v) + "(D" + str(v.deadline) + ", "
            if v.is_shelter():
                s = s + str(v.v_type)
            else:
                s = s + "P" + str(v.ppl_count)
            s = s + ")"
        s = s + "\n"
        s = s + str(self.edges[0]) + ": " + str(self.edges[0].vertex_1) + " -" + str(self.edges[0].weight) + "- " + \
            str(self.edges[0].vertex_2)
        for e in self.edges[1:]:
            s = s + "\n" + str(e) + ": " + str(e.vertex_1) + " -" + str(e.weight) + "- " + str(e.vertex_2)
        return s

    def print_vertices_info(self):
        for v in self.vertices:
            s = "V" + str(v.index) + ": deadline is " + str(v.deadline) + ", "
            if v.is_shelter():
                s = s + "is a shelter, "
            else:
                s = s + "has " + str(v.v_type) + " people in it, "
            s = s + "and has " + str(len(v.edges)) + " roads connected to it."
            print s
