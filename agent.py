from copy import copy, deepcopy

from graph import Edge
from graph import Vertex
from helper_funcs import print_debug, print_query, print_info, dijkstra, get_min_index


class Agent:
    def __init__(self, index, initial_state):
        self.index = index  # type: int
        self.curr_state = initial_state  # type: AgentState

        self.seq = []

    def formulate_goal(self, state):
        return None

    def formulate_problem(self, state, goal):
        return None

    def action(self, percept):
        return None

    def traverse(self, e, dest_v):
        """
        :type e: graph.Edge
        :type dest_v: graph.Vertex
        """
        if e.is_blocked:
            print_debug("TRIED TO TRAVERSE A BLOCKED ROAD " + str(e))
        else:
            print_debug("AGENT " + str(self) + " TRAVERSING TO " + str(dest_v) + " THROUGH " + str(e) + ".")
            print_debug("WILL TAKE " + str(e.weight) + " TIME.")
            self.curr_state.curr_location = e
            self.curr_state.is_traversing = True
            self.curr_state.traverse_dest = dest_v
            self.curr_state.traverse_timer = e.weight

    def is_traversing(self):
        return self.curr_state.is_traversing

    def traverse_update(self):
        if self.curr_state.traverse_timer == 0:  # Arrived
            print_debug("AGENT " + str(self) + " ARRIVED AT " + str(self.curr_state.traverse_dest) +
                        " AT TIME " + str(self.curr_state.time))
            self.curr_state.state_traverse_update()
        else:
            print_debug("AGENT " + str(self) + " TRAVERSING ON " + str(self.curr_state.curr_location) +
                        " TOWARDS " + str(self.curr_state.traverse_dest) + " AT TIME " + str(self.curr_state.time))

    def at_vertex_auto_actions(self):
        if self.curr_state.curr_location.is_shelter():  # Dropping off
            p_dropping_off = self.curr_state.p_carrying
            if p_dropping_off > 0:
                print_debug("AGENT " + str(self) + " DROPPING OFF " + str(p_dropping_off) + " PEOPLE AT " +
                            str(self.curr_state.curr_location))
                self.curr_state.curr_location.drop_off(p_dropping_off)
                self.curr_state.p_saved = self.curr_state.p_saved + p_dropping_off
                self.curr_state.p_carrying = 0
        else:  # Picking up
            ppl_count = self.curr_state.curr_location.pick_up()
            if ppl_count > 0:
                print_debug("AGENT " + str(self) + " PICKING UP " + str(ppl_count) + " PEOPLE FROM " +
                            str(self.curr_state.curr_location))
                self.curr_state.p_carrying = self.curr_state.p_carrying + ppl_count

    def terminate(self):
        print_debug("AGENT " + str(self) + " IS TERMINATING ON " + str(self.curr_state.curr_location))
        self.curr_state.is_terminated = True
        ppl_on_agent = self.curr_state.p_carrying
        self.curr_state.p_carrying = 0
        return ppl_on_agent

    def hurricane_check(self):
        return self.curr_state.state_hurricane_check()

    def __str__(self):
        return "A" + str(self.index)


class HumanAgent(Agent):
    def __init__(self, index, initial_state):
        Agent.__init__(self, index, initial_state)

    def action(self, percept):
        ag_env = percept
        ag_location = self.curr_state.curr_location

        # Now to the actual action
        print_debug("HUMAN AGENT " + str(self) + " ACTION:")
        print_info("PRINTING STATE OF " + str(self) + ":")
        print_info(self.curr_state)
        print_query("Please enter next move:")
        input_action = str(raw_input())
        return input_action


class GreedyAgent(Agent):
    def __init__(self, index, initial_state):
        Agent.__init__(self, index, initial_state)

    def formulate_goal(self, state):
        return None

    def formulate_problem(self, state, goal):
        return None

    def action(self, percept):
        ag_env = percept
        self.curr_state.v_people = ag_env.get_people_array_considering_deadlines()  # Updating people status for myself
        print_debug("GREEDY AGENT " + str(self) + " ACTION:")
        curr_graph = deepcopy(ag_env.graph)
        curr_graph.remove_blocked_edges()
        curr_vertex = curr_graph.vertices[self.curr_state.curr_location.index-1]
        if not curr_vertex.get_connected_vertices():
            return "TERMINATE"
        distances, paths = dijkstra(curr_graph, curr_vertex)
        distances[curr_vertex.index - 1] = float("inf")

        if self.curr_state.p_carrying > 0:
            print_debug("LOOKING FOR CLOSEST SHELTER")
            for v in curr_graph.vertices:
                if not v.is_shelter():
                    distances[v.index - 1] = float("inf")
        else:
            print_debug("LOOKING FOR CLOSEST PEOPLE LOCATION")
            for v in curr_graph.vertices:
                if v.is_shelter():
                    distances[v.index - 1] = float("inf")
                elif v.ppl_count == 0:
                    distances[v.index - 1] = float("inf")

        min_dist_index = get_min_index(distances)
        min_dist_v_index = min_dist_index + 1

        if distances[min_dist_index] == float("inf"):  # We have nowhere to go!
            return "TERMINATE"

        print_debug("AIMING FOR V" + str(min_dist_v_index) + " at distance " + str(distances[min_dist_index]))
        next_move_v_index = paths[min_dist_index][1].index
        print_debug("NEXT MOVE IS TO V" + str(next_move_v_index))
        return "V" + str(next_move_v_index)


class VandalAgent(Agent):
    def __init__(self, index, initial_state):
        Agent.__init__(self, index, initial_state)
        self.no_ops_timer = len(self.curr_state.v_people)  # V
        self.block_timer = 0

    def formulate_goal(self, state):
        return None

    def formulate_problem(self, state, goal):
        return None

    def action(self, percept):
        ag_env = percept
        print_debug("VANDAL AGENT " + str(self) + " ACTION:")
        if self.no_ops_timer > 0:
            self.no_ops_timer = self.no_ops_timer - 1
            return None
        else:
            curr_graph_without_blocks = deepcopy(ag_env.graph)
            curr_graph_without_blocks.remove_blocked_edges()
            connected_edges = self.curr_state.curr_location.connected_edges
            connected_edges_without_blocks = \
                curr_graph_without_blocks.vertices[self.curr_state.curr_location.index-1].connected_edges
            if not connected_edges or not connected_edges_without_blocks:
                print_debug("NO ROADS FROM HERE.")
                return "TERMINATE"

            if self.block_timer == 0:
                weights = [connected_edges_without_blocks[i].weight for i in range(len(connected_edges_without_blocks))]
                min_weight_index = get_min_index(weights)

                target_edge = connected_edges_without_blocks[min_weight_index]
                real_target_edge = ag_env.graph.edges[target_edge.index-1]
                print_debug("BLOCKING EDGE " + str(real_target_edge))
                real_target_edge.block_road()
                self.block_timer = 1
                return None
            else:
                weights = [connected_edges_without_blocks[i].weight for i in range(len(connected_edges_without_blocks))]
                min_weight_index = get_min_index(weights)

                target_edge = connected_edges_without_blocks[min_weight_index]
                real_target_edge = ag_env.graph.edges[target_edge.index - 1]
                self.block_timer = 0
                self.reset_no_ops_timer()
                return str(real_target_edge)

    def at_vertex_auto_actions(self):
        return None

    def reset_no_ops_timer(self):
        self.no_ops_timer = len(self.curr_state.v_people)  # V


class AgentState:
    def __init__(self, s_vertex, v_people, k_value, p_carrying=0, p_saved=0, time=0, is_terminated=False):
        # Starting agent vertex
        self.curr_location = s_vertex       # type: Vertex|Edge
        # An array (!) of the amount of people TO SAVE in every vertex
        self.v_people = v_people            # type: list[int]
        self.p_carrying = p_carrying        # type: int
        self.p_saved = p_saved              # type: int
        self.time = time                    # type: int
        self.is_terminated = is_terminated  # type: bool

        self.is_traversing = False
        self.traverse_dest = None  # type: Vertex
        self.traverse_timer = 0

        # The amount of ppl to save in the game
        self.ppl2save = sum(v_people)
        self.k_value = k_value

    def time_update(self):
        self.time = self.time + 1
        if self.is_traversing:
            self.traverse_timer = self.traverse_timer - 1

    def state_terminate(self):
        self.is_terminated = True

    def state_traverse(self, e, dest_v=None):
        if not dest_v:
            if self.curr_location == e.vertex_1:
                dest_v = e.vertex_2
            else:
                dest_v = e.vertex_1
        self.time += e.weight
        self.curr_location = dest_v

    def state_traverse_update(self):
        if self.traverse_timer == 0:
            self.is_traversing = False
            self.curr_location = self.traverse_dest
            self.traverse_dest = None

    def state_pickup_loadoff_update(self):
        if not self.is_traversing:
            # Pick up
            if not self.curr_location.is_shelter():
                self.p_carrying += self.v_people[self.curr_location.index-1]
                self.v_people[self.curr_location.index-1] = 0
            # Load off
            else:
                self.p_saved += self.p_carrying
                self.p_carrying = 0

    def state_hurricane_check(self):
        location = self.curr_location
        if isinstance(location, Edge):
            return self.time > location.vertex_1.deadline or \
                   self.time > location.vertex_2.deadline
        else:
            return self.time > location.deadline

    def state_v_people_update(self):
        for v in self.curr_location.graph.vertices:
            if v.deadline < self.time:
                self.v_people[v.index-1] = 0

    def __str__(self):
        return "(" + str(self.curr_location) + ", " + str(self.p_carrying) + ", " + str(self.p_saved) + ", " + \
               str(self.time) + ", " + str(self.is_terminated) + ")"
