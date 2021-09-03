from rankedDelegation.election.profile import Election, Voter
import numpy as np


def election_prominence_real(data, p_casting=0.2):
    """
    Create a delegation network with the prominence-based method using a real network. In this method, we
    add edges one by one and we delegates with higher probability to voters who have already a lot
    of support (rich get richer principle)

    Parameters
    ----------
    data
        The real network on which we perform an election
    p_casting
        Proportion of casting voters in the election
    Returns
    -------
    Election
        An election with popularity-based delegation

    """
    n = data["nb_nodes"]
    list_edges = data["edges"]
    popularity = data["in"]
    p = 1 - p_casting

    e = Election()
    outedges_dict = {}
    for (a, b) in list_edges:
        if a not in outedges_dict:
            outedges_dict[a] = []
        outedges_dict[a].append(b)

    # Add casting voters
    for i in (range(n)):
        x = np.random.choice([0, 1, 2], p=[p, (1 - p) / 2, (1 - p) / 2])
        if x == 0:
            v = Voter()
        else:
            v = Voter(vote=x)
        e.add_voter(v)

    # Add edges
    L = e.list_voters
    delegatees_list = [[] for i in range(n)]

    for r_1 in (range(n)):
        if L[r_1].vote is not None or r_1 not in outedges_dict:
            continue
        delegatees = outedges_dict[r_1]
        proba = popularity[delegatees]
        proba /= proba.sum()
        ordering = np.random.choice(delegatees, p=proba, replace=False, size=len(proba))
        for ind in ordering:
            delegatees_list[r_1].append(L[ind])

    for voter in L:
        voter.delegate(delegatees_list[voter.id][:50])

    return e


def get_friends(list_edges):
    friends = {}
    for [a,b] in list_edges:
        if a not in friends:
            friends[a] = []
        if b not in friends:
            friends[b] = []
        friends[a].append(b)
        friends[b].append(a)
    return friends


def list_common_friends(a, friends):
    friends_a  = friends[a]
    list_common = []
    for x in friends_a:
        c = 1
        friends_x = friends[x]
        for b in friends_x:
            if b in friends_a:
                c += 1
        list_common.append(c)
    return np.array(list_common, dtype=float)


def election_friendship_real(data, p_casting=0.2):
    """
    Create a delegation network with the friendship-based method using a real network. In this method, first
    create a network with G(n,p) model then we attribute delegatees with probability based on the
    number of common friends.

    Parameters
    ----------
    data
        The real network on which we perform an election
    p_casting
        Proportion of casting voters in the election


    Returns
    -------
    Election

    """
    list_edges = data["edges"]
    n = data["nb_nodes"]
    e = Election()
    p = 1 - p_casting

    friends = get_friends(list_edges)

    # We add the voter and pick the casting voters
    for i in (range(n)):
        x = np.random.choice([0, 1, 2], p=[p, (1 - p) / 2, (1 - p) / 2])
        if x == 0:
            v = Voter()
        else:
            v = Voter(vote=x)
        e.add_voter(v)

    L = e.list_voters
    delegatees_list = [[] for i in range(n)]
    n_edges = 0

    for r_1 in (range(n)):

        if L[r_1].vote is not None or r_1 not in friends:
            continue

        delegatees = friends[r_1]
        proba = list_common_friends(r_1, friends)
        proba /= np.sum(proba)
        ordering = np.random.choice(delegatees, p=proba, replace=False, size=len(proba))
        for ind in ordering:
            delegatees_list[r_1].append(L[ind])

    c = 0
    for voter in L:
        voter.delegate(delegatees_list[voter.id][:50])
        if len(delegatees_list[voter.id]) > 50:
            c += len(delegatees_list[voter.id]) - 50

    return e


def election_weight_real(data, p_casting=0.8):
    n = data["nb_nodes"]
    list_edges = data["edges"]
    p = 1 - p_casting

    e = Election()
    outedges_dict = {}
    for (a, b, score) in (list_edges):
        if score <= 0:
            continue
        if a not in outedges_dict:
            outedges_dict[a] = [[] for i in range(11)]
        outedges_dict[a][score].append(b)

    # Add casting voters
    for i in (range(n)):
        x = np.random.choice([0, 1, 2], p=[p, (1 - p) / 2, (1 - p) / 2])
        if x == 0:
            v = Voter()
        else:
            v = Voter(vote=x)
        e.add_voter(v)

    # Add edges
    L = e.list_voters
    delegatees_list = [[] for _ in range(n)]

    for r_1 in (range(n)):
        if L[r_1].vote is not None or r_1 not in outedges_dict:
            continue

        ordering = []
        for i in range(10, 0, -1):
            tab = outedges_dict[r_1][i]
            np.random.shuffle(tab)
            for x in tab:
                ordering.append(x)

        for ind in ordering:
            delegatees_list[r_1].append(L[ind])

    for voter in L:
        voter.delegate(delegatees_list[voter.id])

    return e
