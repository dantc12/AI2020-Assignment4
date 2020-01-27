from environment import Environment as Env
from helper_funcs import print_debug, print_query, print_info, dijkstra_without_graph

ENVIRONMENT_SETTINGS_FILE = "environment_settings1.txt"

print_query("Please enter K vehicle loss penalty value:")
inp = raw_input()
if str(inp) == '':
    env = Env(ENVIRONMENT_SETTINGS_FILE)
else:
    env = Env(ENVIRONMENT_SETTINGS_FILE, int(inp))


print_info("OUR GRAPH:")
print_info(env.graph)

print_query("Please enter number of agents in the environment:")
num_of_agents = input()
agent_options = ["HUMAN", "GREEDY", "VANDAL", "GREEDY SEARCH", "A_STAR SEARCH", "REALTIME A_STAR SEARCH"]

for i in range(num_of_agents):
    print_query("Please enter agent type:")
    for j in range(len(agent_options)):
        print_info(str(j+1) + ". " + agent_options[j])
    choice = input() - 1
    ag_type = agent_options[choice]
    print_query("Please enter starting position (starting vertex number):")
    s_vertex = env.graph.vertices[input()-1]
    env.add_agent(ag_type, s_vertex)

print "------------------------------------------------"
print_debug("STARTING SIMULATION:")
env.simulation()
