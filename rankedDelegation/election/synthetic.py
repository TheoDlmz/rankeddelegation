from rankedDelegation.election.profile import Election, Voter
import numpy as np


def election_popularity(n_voters=1000, p_casting=0.2, n_delegatees=4, popularity_factor=1):
    """
    Create a synthetic delegation network with the popularity-based model. In this model, we
    add edges one by one and we delegates with higher probability to voters who have already a lot
    of support (rich get richer principle)

    Parameters
    ----------
    n_voters
        Number of voters in the election

    p_casting
        Proportion of casting voters in the election

    n_delegatees
        Average number of delegatees per delegating voters

    popularity_factor
        Popularity factor of the model

    Returns
    -------
    Election
        An election with popularity-based delegation

    """
    e = Election()
    p = 1- p_casting
    for i in range(n_voters):
        x = np.random.choice([0, 1, 2], p=[p, (1 - p) / 2, (1 - p) / 2])
        if x == 0:
            v = Voter()
        else:
            v = Voter(vote=x)
        e.add_voter(v)

    L = e.list_voters
    delegatees = [[] for i in range(n_voters)]
    n_edges = 0
    proba = np.ones(n_voters)
    while n_edges < n_voters * p * n_delegatees:
        r_1 = np.random.randint(n_voters)
        if L[r_1].vote is not None:
            continue

        proba_curr = np.copy(proba)
        proba_curr[r_1] = 0
        proba_curr **= popularity_factor
        proba_curr /= proba_curr.sum()

        r_2 = np.random.choice(n_voters, p=proba_curr)

        if r_1 == r_2 or L[r_2] in delegatees[r_1]:
            continue
        else:
            delegatees[r_1].append(L[r_2])
            proba[r_2] += 1
            n_edges += 1

    for voter in L:
        voter.delegate(delegatees[voter.id])

    return e


def election_friendship(n_voters=1000, p_casting=0.2, n_friends=4, friends_factor=1):
    """
    Create a synthetic delegation network with the friendship-based model. In this model, first
    create a network with G(n,p) model then we attribute delegatees with probability based on the
    number of common friends.

    Parameters
    ----------
    n_voters
        Number of voters in the election

    p_casting
        Proportion of casting voters in the election

    n_friends
        Average number of friends per voters

    friends_factor
        The friends factor used in the model

    Returns
    -------
    Election

    """
    M_isedges = np.random.rand(n_voters, n_voters) < n_friends / (n_voters - 1)
    M_edges = np.zeros((n_voters, n_voters))
    p = 1 - p_casting

    for i in range(n_voters):
        for j in range(i + 1, n_voters):
            if M_isedges[i, j]:
                M_edges[j, i] = 1
                M_edges[i, j] = 1

    common_friends = M_edges.dot(M_edges.T)

    e = Election()
    for i in range(n_voters):
        x = np.random.choice([0, 1, 2], p=[p, (1 - p) / 2, (1 - p) / 2])
        if x == 0:
            v = Voter()
        else:
            v = Voter(vote=x)
        e.add_voter(v)

    L = e.list_voters
    for i, voter in enumerate(L):
        if voter.vote is not None:
            continue
        list_delegatees = []
        proba = []
        for j in range(n_voters):
            if M_edges[i, j]:
                list_delegatees.append(j)
                proba.append((common_friends[i, j] + 1) ** friends_factor)
        if len(list_delegatees) == 0:
            continue
        proba = np.array(proba)
        proba /= proba.sum()
        ordering = np.random.choice(list_delegatees, p=proba, replace=False, size=len(proba))

        list_output = []
        for ind in ordering:
            list_output.append(L[ind])
        voter.delegate(list_output)

    return e


def matrix_dist(pos):
    n = len(pos)
    M = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            M[i, j] = np.sqrt((pos[i][0] - pos[j][0]) ** 2 + (pos[i][1] - pos[j][1]) ** 2)
            M[j, i] = np.sqrt((pos[i][0] - pos[j][0]) ** 2 + (pos[i][1] - pos[j][1]) ** 2)

    return M


def election_spatial(n_voters=1000, p_casting=0.8, n_delegatees=4, distrib_x="gauss", distrib_y="gauss"):
    """
    Create a synthetic delegation network with the spatial model. In this model, first we put every voter
    on a 2D plane, then each delegating voter delegates to the voters the closest to him.

    Parameters
    ----------
    n_voters
        Number of voters in the election

    p_casting
        Proportion of casting voters in the election

    n_delegatees
        Number of delegatees per voters

    distrib_x
        Distribution for the x coordinate (either "gauss" or "uniform")

    distrib_y
        Distribution for the y coordinate (either "gauss" or "uniform")

    Returns
    -------
    election: Election
        The Election with voters
    pos: list
        The list of position of voters on the spatial plane

    """

    distribs = [distrib_x, distrib_y]
    p = 1 - p_casting
    pos = []
    all_pos = []
    for j in range(2):
        if distribs[j] == "uniform":
            all_pos.append(np.random.rand(n_voters))
        elif distribs[j] == "gauss":
            all_pos.append(np.random.normal(size=n_voters))

    e = Election()
    for i in range(n_voters):
        x = np.random.choice([0, 1, 2], p=[p, (1 - p) / 2, (1 - p) / 2])
        if x == 0:
            v = Voter()
        else:
            v = Voter(vote=x)
        e.add_voter(v)
        pos_v = [all_pos[0][i], all_pos[1][i]]
        pos.append(pos_v)

    M = matrix_dist(pos)
    L = e.list_voters
    for i in range(n_voters):
        if L[i].vote is not None:
            continue
        order = np.argsort(M[i])[1:1 + n_delegatees]
        L[i].delegate([L[x] for x in order])

    return e, pos
