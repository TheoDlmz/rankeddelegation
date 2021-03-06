def find_gurus(voters):
    """
    This function creates a list of the guru's in the given voter list.
    Parameters
    ----------
    voters: list
        The voter list.
    Return
    ----------
    list
        A list of the guru's in the voter list.

    """
    guru_list = []
    for voter in voters:
        if voter.vote is not None:
            guru_list.append(voter)
    return guru_list


def reverse_graph(voters):
    """
    This function return the set of in-neighbours of every node in a delegation graph

    Parameters
    ----------
    voters: a list of Voter

    Returns
    -------
    dict
        A dict containing the list of the in-neighbours of every node in
        a delegation graph, with the rank of each edge.

    """
    followers = {}
    for voter in voters:
        followers[voter.id] = []
    for voter in voters:
        for j, delegated in enumerate(voter.delegatees):
            followers[delegated.id].append([j, voter, delegated])
    return followers
