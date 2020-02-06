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
    elif ss.find("TERMINATING") > -1 or ss.find("BLOCK") > -1:
        print bcolors.WARNING + "DEBUG:   " + ss + bcolors.ENDC
    elif ss.find("PICK") > -1 or ss.find("DROP") > -1 or ss.find("ARRIV") > -1 or ss.find(", 'E") > -1 or \
            ss.find(", 'TERM") > -1:
        print bcolors.OKGREEN + "DEBUG:   " + ss + bcolors.ENDC
    else:
        print bcolors.OKBLUE + "DEBUG:   " + ss + bcolors.ENDC


def print_info(s):
    print "INFO:    " + str(s)


def print_query(s):
    print "QUERY:   " + str(s)


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
