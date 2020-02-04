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

print_query("Please enter starting position (starting vertex number):")
s_vertex = env.graph.vertices[0]
env.add_agent(ag_type, s_vertex)

print "------------------------------------------------"
print_debug("STARTING SIMULATION:")
env.simulation()
