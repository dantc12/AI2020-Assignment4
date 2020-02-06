from graph import Edge, Vertex
from helper_funcs import print_debug


class Agent:
    def __init__(self, index, initial_state):
        self.index = index  # type: int
        self.curr_state = initial_state  # type: AgentState

        self.seq = []

    # def formulate_goal(self, state):
    #     return None
    #
    # def formulate_problem(self, state, goal):
    #     return None

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


class ValueIterationAgent(Agent):
    def __init__(self, index, initial_state):
        Agent.__init__(self, index, initial_state)

    def action(self, percept):
        ag_env = percept
        action = ag_env.getBestPolicy(self.curr_state)
        return action


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
