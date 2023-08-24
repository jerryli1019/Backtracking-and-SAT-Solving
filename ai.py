from __future__ import print_function
from game import sd_peers, sd_spots, sd_domain_num, init_domains, \
    restrict_domain, SD_DIM, SD_SIZE
import random, copy

class AI:
    def __init__(self):
        pass

    def solve(self, problem):
        assign_function = {}
        domains = init_domains()
        restrict_domain(domains, problem) 
        decision_stack = []

        while True:
            assign_function, domains = self.propagate(sd_peers, assign_function, domains)
            if "Conflict" not in assign_function.keys():
                all_assign = True
                for spot in sd_spots:
                    if spot not in assign_function.keys():
                        all_assign = False
                        break
                if all_assign:
                    solution = {}
                    for key, val in assign_function.items():
                        if key != "Conflict":
                            solution[key] = [val]
                    return solution
                else:
                    assign_function, x = self.make_decision(assign_function, domains)
                    decision_stack += [(copy.deepcopy(assign_function), x, copy.deepcopy(domains))]
            else:
                if len(decision_stack) == 0:
                    return None
                else:
                    assign_function, domains = self.backtrack(decision_stack)

    def propagate(self, sd_peers, assign_function, domains):
        while True:
            for key, val in domains.items():
                if len(val) == 1:
                    assign_function[key] = val[0]
            for key, val in assign_function.items():
                if len(domains[key]) > 1:
                    domains[key] = [assign_function[key]]
            for key, val in domains.items():
                if len(val) == 0:
                    assign_function["Conflict"] = True
                    return assign_function, domains
            consist = True
            for key, val in domains.items():
                for peer in sd_peers[key]:
                    if len(domains[peer]) == 1 and domains[peer][0] in domains[key]:
                        domains[key].remove(domains[peer][0])
                        consist = False
            if consist:
                return assign_function, domains
    
    def make_decision(self, assign_function, domains):
        min_len_dom = float('inf')
        spot_with_smallest_dom = None
        for spot in sd_spots:
            if spot not in assign_function.keys():
                len_dom = len(domains[spot])
                if len_dom < min_len_dom:
                    min_len_dom = len_dom
                    spot_with_smallest_dom = spot
        assign_function[spot_with_smallest_dom] = random.choice(domains[spot_with_smallest_dom])
        return assign_function, spot_with_smallest_dom
    
    def backtrack(self, decision_stack):
        assign_function, x, domains = decision_stack.pop()
        a = assign_function.pop(x)
        domains[x].remove(a)
        return assign_function, domains

    def sat_encode(self, problem):
        text = ""
        ncl = 0

        for r in range(1, SD_SIZE**2+1, 1):
            b = 9*(r-1) + 1
            text += "{} {} {} {} {} {} {} {} {} 0\n".format(b, b+1, b+2, b+3, b+4, b+5, b+6, b+7, b+8)
            ncl += 1

        for i in range(SD_SIZE):
            for j in range(SD_SIZE):
                for r in range(1, SD_SIZE + 1):
                    for c in range(r + 1, SD_SIZE + 1):
                        text += "{} {} 0\n".format(-(i*SD_SIZE**2+j*SD_SIZE+r), -(i*SD_SIZE**2+j*SD_SIZE+c))
                        ncl += 1

        for i in range(1, 1+81*8+1, 81):
            for j in range(i, i+9, 1):
                text += "{} {} {} {} {} {} {} {} {} 0\n".format(j, j+9, j+18, j+27, j+36, j+45, j+54, j+63, j+72)
                ncl += 1

        for i in range(1, 82, 1):
            text += "{} {} {} {} {} {} {} {} {} 0\n".format(i, i+81, i+81*2, i+81*3, i+81*4, i+81*5, i+81*6, i+81*7, i+81*8)
            ncl += 1

        def one_grid(c_start, c_end):
            text = ""
            for i in range(c_start, c_end+1, 1):
                text += "{} {} {} {} {} {} {} {} {} 0\n".format(i, i+9, i+18, i+81, i+81+9, i+81+18, i+81*2, i+81*2+9, i+81*2+18)
            return text

        for i in [1, 1+3*9, 1+6*9, 1+27*9, 1+27*9+3*9, 1+27*9+6*9, 1+54*9, 1+54*9+3*9, 1+54*9+6*9]:
            text += one_grid(i, i+8)
            ncl += 9

        domains = init_domains()
        restrict_domain(domains, problem) 
        for key, val in domains.items():
            if len(val) == 1:
                text += "{} 0\n".format(key[0]*SD_SIZE**2 + key[1]*SD_SIZE + val[0])
                ncl += 1

        text = "p cnf {} {}\n".format(SD_SIZE**3, ncl) + text
        return text

    def sat_decode(self, assignments):
        domains = {}
        for key, val in assignments.items():
            if val:
                i = (key - 1)//SD_SIZE**2
                j = ((key - 1)//SD_SIZE)%SD_SIZE
                a = key - i*SD_SIZE**2 - j*SD_SIZE
                domains[(i,j)] = [a]
        return domains
