def find_gurus(voters):
    guru_list = []
    for voter in voters:
        if voter.vote is not None:
            guru_list.append(voter)
    return guru_list


def reverse_graph(voters):
    followers = {}
    for voter in voters:
        followers[voter.id] = []
    for voter in voters:
        for j, delegated in enumerate(voter.delegatees):
            followers[delegated.id].append([j, voter, delegated])
    return followers
