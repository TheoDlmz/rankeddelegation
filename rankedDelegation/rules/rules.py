from rankedDelegation.rules.utils import *
import numpy as np

def naive_BFD(voters):
    for voter in voters:
        if voter.vote is not None:
            voter.set_guru(voter)
        else:
            seen = []
            queue = [([], voter)]
            found = False
            while not found and len(queue) > 0:
                path, curr = queue[0]
                seen.append(curr.id)
                queue = queue[1:]
                if curr.vote is not None:
                    voter.set_guru(curr, path)
                    found = True
                else:
                    for i, delegatee in enumerate(curr.delegatees):
                        if delegatee.id in seen:
                            continue
                        else:
                            queue.append((path + [i + 1], delegatee))


def naive_DFD(voters):
    for voter in voters:
        if voter.vote is not None:
            voter.set_guru(voter)
        else:
            seen = []
            queue = [([], voter)]
            found = False
            while not found and len(queue) > 0:
                path, curr = queue[-1]
                seen.append(curr.id)
                queue = queue[:-1]
                if curr.vote is not None:
                    voter.set_guru(curr, path)
                    found = True
                else:
                    for i, delegatee in enumerate(curr.delegatees[::-1]):
                        if delegatee.id in seen:
                            continue
                        else:
                            queue.append((path + [len(curr.delegatees) - i], delegatee))


def diffusion(voters):
    gurus = find_gurus(voters)
    followers = reverse_graph(voters)

    queue = []
    for g in gurus:
        queue.extend(followers[g.id])
        g.set_guru(g)

    while len(queue) > 0:
        x = min([element[0] for element in queue])
        n_queue = len(queue)
        next_queue = []
        for i, element in enumerate(queue[::-1]):
            rank, voter, delegatee = element
            if voter.guru is not None:
                queue.pop(n_queue - 1 - i)
            elif rank == x:
                voter.set_guru(delegatee.guru, path_to_guru=[rank + 1] + delegatee.path_to_guru)
                queue.pop(n_queue - 1 - i)
                next_queue.extend(followers[voter.id])
        queue.extend(next_queue)


def maxsum(voters):
    gurus = find_gurus(voters)
    followers = reverse_graph(voters)

    queue = []
    for g in gurus:
        queue.extend(followers[g.id])
        g.set_guru(g)

    while len(queue) > 0:
        min_sum = min([element[0] + 1 + np.sum(element[2].path_to_guru) for element in queue])
        n_queue = len(queue)
        next_queue = []
        for i, element in enumerate(queue[::-1]):
            rank, voter, delegatee = element
            if voter.guru is not None:
                if np.sum(voter.path_to_guru) == min_sum and voter.path_to_guru[0] > rank:
                    voter.path_to_guru[0] = rank
                    voter.guru = delegatee.guru
                queue.pop(n_queue - 1 - i)
            elif rank + 1 + np.sum(element[2].path_to_guru) == min_sum:
                voter.set_guru(delegatee.guru, path_to_guru=[rank + 1] + delegatee.path_to_guru)
                queue.pop(n_queue - 1 - i)
                next_queue.extend(followers[voter.id])
        queue.extend(next_queue)


def lexrank(voters):
    gurus = find_gurus(voters)
    followers = reverse_graph(voters)

    queue = []
    for g in gurus:
        queue.extend(followers[g.id])
        g.set_guru(g)

    while len(queue) > 0:
        all_paths = [[element[0] + 1] + element[2].path_to_guru for element in queue]
        all_paths = [sorted(x)[::-1] for x in all_paths]
        min_path = min(all_paths)
        n_queue = len(queue)
        next_queue = []
        for i, element in enumerate(queue[::-1]):
            rank, voter, delegatee = element
            if voter.guru is not None:
                if sorted(voter.path_to_guru)[::-1] == min_path and voter.path_to_guru[0] > rank:
                    voter.path_to_guru[0] = rank
                    voter.guru = delegatee.guru
                queue.pop(n_queue - 1 - i)
            elif sorted([rank + 1] + element[2].path_to_guru)[::-1] == min_path:
                voter.set_guru(delegatee.guru, path_to_guru=[rank + 1] + delegatee.path_to_guru)
                queue.pop(n_queue - 1 - i)
                next_queue.extend(followers[voter.id])
        queue.extend(next_queue)