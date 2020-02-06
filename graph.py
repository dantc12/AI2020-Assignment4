from copy import copy


class Vertex:
    def __init__(self, index, v_type, graph, deadline=float("inf"), ppl_count=0):
        self.index = index  # type: int
        # Can be: 'START', 'SHELTER', or 'P' for a people location
        self.v_type = v_type  # type: str

        self.deadline = deadline
        self.ppl_count = ppl_count  # type: int

        self.connected_edges = []  # type: list[Edge]
        self.connected_vertices = []  # type: list[Vertex]
        self.graph = graph

    def add_connected_obj(self, obj):
        if isinstance(obj, Edge):
            self.connected_edges.append(obj)
        elif isinstance(obj, Vertex):
            self.connected_vertices.append(obj)
        else:
            raise Exception()

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

    def is_start(self):
        return self.v_type == 'START'

    def is_shelter(self):
        return self.v_type == 'SHELTER'

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

    def __le__(self, other):
        return self.index <= other.index

    def __lt__(self, other):
        return self.index < other.index

    def __eq__(self, other):
        return self.index == other.index


class Edge:
    def __init__(self, index, vertex_1, vertex_2, weight, block_prob):
        self.index = index
        self.vertex_1 = vertex_1  # type: Vertex
        self.vertex_2 = vertex_2  # type: Vertex
        self.weight = weight

        # TODO: is this okay? should this change according to probability?
        self.is_blocked = False
        self.block_prob = block_prob

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
        n = 0
        f = open(file_path, "r")
        for line in f:
            if line[0] == '#':
                line_info = line.split('  ')[0][1:]
                line_info_split = line_info.split(' ')
                if line_info[0] == 'N':  # N x
                    n = int(line_info_split[1])
                    # self.vertices = [None] * n
                elif line_info[0] == 'S':  # Start x|Shelter x
                    vertex_index = int(line_info_split[1])
                    if line_info_split[0] == 'Start':
                        self.vertices.append(Vertex(vertex_index, 'START', self))
                    elif line_info_split[0] == 'Shelter':
                        self.vertices.append(Vertex(vertex_index, 'SHELTER', self))
                elif line_info[0] == 'V':  # Vx Dx Px
                    vertex_index = int(line_info_split[0][1:])  # Vx
                    vertex_deadline = int(line_info_split[1][1:])  # Dx
                    vertex_ppl_count = int(line_info_split[2][1:])  # Px
                    self.vertices.append(Vertex(vertex_index, 'P', self, vertex_deadline, vertex_ppl_count))
                elif line_info[0] == 'E':  # Ex x x Wx [Bx.x]
                    self.vertices.sort()

                    edge_index = int(line_info_split[0][1:])  # Ex
                    edge_v1_index = int(line_info_split[1])  # x
                    edge_v2_index = int(line_info_split[2])  # x
                    v1 = self.vertices[edge_v1_index-1]
                    v2 = self.vertices[edge_v2_index - 1]
                    edge_weight = int(line_info_split[3][1:])  # Wx
                    edge_block_prob = 0.0
                    if len(line_info_split) == 5:
                        edge_block_prob = float(line_info_split[4][1:])

                    e = Edge(edge_index, v1, v2, edge_weight, edge_block_prob)
                    self.edges.append(e)
                    v1.add_connected_obj(e)
                    v1.add_connected_obj(v2)
                    v2.add_connected_obj(e)
                    v2.add_connected_obj(v1)

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

    # @staticmethod
    # def get_connected_edges(v):
    #     return v.connected_edges
    #
    # @staticmethod
    # def is_connected_edge(e, v):
    #     return e.vertex_1 == v or e.vertex_2 == v

    def get_people_vertices(self):
        res = []
        for v in self.vertices:
            if v.v_type == 'P':
                res.append(v)
        return res

    def get_people_array(self):
        ppl_vertices = self.get_people_vertices()
        res = [0] * len(self.vertices)
        for v in ppl_vertices:
            res[v.index-1] = v.ppl_count
        return res

    def get_people_array_with_shelter(self):
        res = [0] * len(self.vertices)
        for v in self.vertices:
            res[v.index-1] = v.ppl_count
        return res

    def get_poss_blocked_edges(self):
        res = []
        for edge in self.edges:
            if edge.block_prob != 0.0:
                res += edge
        return res

    def get_edges_blocked_status(self):
        res = [""] * len(self.edges)
        for e in self.edges:
            if e.block_prob != 0.0:
                res[e.index-1] = "U"
            else:
                if e.is_blocked:
                    res[e.index-1] = "T"
                else:
                    res[e.index-1] = "F"
        return res

    def __str__(self):
        s = str(self.vertices[0]) + "(D" + str(self.vertices[0].deadline) + ", "
        if not self.vertices[0].is_ppl_location():
            s += str(self.vertices[0].v_type)
        else:
            s += "P" + str(self.vertices[0].ppl_count)
        s += ")"
        for v in self.vertices[1:]:
            s += ", " + str(v) + "(D" + str(v.deadline) + ", "
            if not v.is_ppl_location():
                s += str(v.v_type)
            else:
                s += "P" + str(v.ppl_count)
            s += ")"
        s += "\n"
        s += str(self.edges[0]) + ": " + str(self.edges[0].vertex_1) + " -" + str(self.edges[0].weight) + "- " + \
            str(self.edges[0].vertex_2)
        if self.edges[0].block_prob != 0.0:
            s += " B" + str(self.edges[0].block_prob)
        for e in self.edges[1:]:
            s += "\n" + str(e) + ": " + str(e.vertex_1) + " -" + str(e.weight) + "- " + str(e.vertex_2)
            if e.block_prob != 0.0:
                s += " B" + str(e.block_prob)
        return s

    # def print_vertices_info(self):
    #     for v in self.vertices:
    #         s = "V" + str(v.index) + ": deadline is " + str(v.deadline) + ", "
    #         if v.is_shelter():
    #             s = s + "is a shelter, "
    #         else:
    #             s = s + "has " + str(v.v_type) + " people in it, "
    #         s = s + "and has " + str(len(v.edges)) + " roads connected to it."
    #         print s

    # def is_mpd_terminate(self, state):
    #     pass
