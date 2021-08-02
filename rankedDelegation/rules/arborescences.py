import numpy as np
import pulp
from rankedDelegation.rules.rules import lexiMax
np.random.seed(42)


def LPArborescence(tab_edges, tab_voters):
    """
    This function compute the minimal arborescence of a network instance given as parameter

    Parameters
    ----------
    tab_edges: list
        List of edges of the network with triplet of the form (int, int, int) with id of start node, id
        of end node, and weight of the edge

    tab_voters: int list
        The list of voters

    Returns
    -------
    dict_paths
        The dict of delegation path of each voter
    dict_guru
        The dict of guru of each voter

    """

    prob = pulp.LpProblem("Borda_Arborescence", pulp.LpMinimize)

    X = [pulp.LpVariable("x_%i" % i, 0, 1, cat='Integer') for i in range(len(tab_edges))]

    optimization_sum = pulp.lpSum([X[i] * tab_edges[i][2] for i in range(len(tab_edges))])

    prob += optimization_sum

    out_edges = {}
    for i in range(len(tab_voters) - 1):
        v = tab_voters[i]
        out_edges[v] = []

    for i, edge in enumerate(tab_edges):
        v_out = edge[0]
        out_edges[v_out].append(i)

    for v_1 in range(len(tab_voters) - 1):
        node_1 = tab_voters[v_1]
        constraint_x = pulp.lpSum([X[i] for i in out_edges[node_1]])
        prob += constraint_x == 1

    solver = pulp.GUROBI_CMD(msg=False, warmStart=True)

    success = False

    while not success:

        prob.solve(solver)

        parents = {}

        for v in prob.variables():
            i = int(v.name[2:])
            if v.varValue > 1 / 2:
                parent = tab_edges[i][1]
                child = tab_edges[i][0]
                parents[child] = (parent, tab_edges[i][2])

        seen = []
        loops = []

        dict_paths = {}
        dict_gurus = {}

        for i in range(len(tab_voters) - 1):
            v_i = tab_voters[i]
            v = v_i

            if v in seen:
                continue

            current_path = []
            sequence = []
            while v not in current_path and v != -1 and v not in seen:
                current_path.append(v)
                v, new_rank = parents[v]
                if new_rank > 0:
                    sequence.append(new_rank)

            if len(loops) == 0:
                guru = current_path[-1]
                if v in seen:
                    sequence += dict_paths[v]
                    guru = dict_gurus[v]

            seen += current_path
            if v not in current_path:
                if len(loops) == 0:
                    for j in range(len(current_path)):
                        dict_paths[current_path[j]] = sequence[j:]
                        dict_gurus[current_path[j]] = guru
                continue
            else:
                first_index = current_path.index(v)
                cycle = current_path[first_index:]
                loops.append(cycle)

        if len(loops) == 0:
            success = True
        else:
            for cycle in loops:
                out_edges_cycle = []
                for i, edge in enumerate(tab_edges):
                    v_out = edge[0]
                    v_in = edge[1]
                    if v_in not in cycle and v_out in cycle:
                        out_edges_cycle.append(i)

                constraint_x = pulp.lpSum([X[i] for i in out_edges_cycle])
                prob += constraint_x >= 1

    return dict_paths, dict_gurus


def bordaArb(election):
    """
    This function apply the borda Arborescence rule for delegation

    Parameters
    ----------
    election

    Returns
    -------
    None

    """
    election.attribute_gurus(lexiMax)

    voters = election.list_voters

    tab_voters = []
    for voter in voters:
        if voter.guru is not None:
            tab_voters.append(voter.id)

    sink = -1
    tab_voters.append(sink)

    tab_edges = []
    for voter in voters:
        if voter.vote is not None:
            tab_edges.append((voter.id, sink, 0))

        if voter.guru is not None:
            for j, delegatee in enumerate(voter.delegatees):
                if delegatee.id in tab_voters:
                    tab_edges.append((voter.id, delegatee.id, j + 1))

    dict_paths, dict_gurus = LPArborescence(tab_edges, tab_voters)

    for k in dict_paths:
        voters[k].set_guru(voters[dict_gurus[k]], dict_paths[k])


