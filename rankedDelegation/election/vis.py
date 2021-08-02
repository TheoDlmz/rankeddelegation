import numpy as np
import random
import matplotlib.pyplot as plt


def plot_network(pos, election, plot_edges=False, color_clusters=False, dict_colors=None):
    color = []
    gurus = []
    not_gurus = []
    if dict_colors is None:
        dict_colors = {}
        for v in election.list_voters:
            if v.vote is not None:
                dict_colors[v.id] = "#" + ''.join([random.choice('123456789ABCDE') for _ in range(6)])

    for v in election.list_voters:
        if color_clusters:
            if v.vote is None:
                not_gurus.append(v.id)
                if v.guru is None:
                    color.append("k")
                else:
                    color.append(dict_colors[v.guru.id])
            else:
                gurus.append(v.id)
                color.append(dict_colors[v.id])
        else:
            if v.vote is None:
                not_gurus.append(v.id)
                color.append("k")
            else:
                gurus.append(v.id)
                color.append("r")
    pos = np.array(pos)
    _ = plt.subplots(figsize=(15, 8))
    if plot_edges:
        for v in election.list_voters:
            delegatees = v.delegatees
            for d in delegatees:
                plt.plot(pos[[v.id, d.id], 0], pos[[v.id, d.id], 1], "k", linewidth=.2)

    plt.scatter(pos[gurus, 0], pos[gurus, 1], color=list(np.array(color)[gurus]), marker="*", s=150, zorder=5,
                label="casting voters")
    plt.scatter(pos[not_gurus, 0], pos[not_gurus, 1], color=list(np.array(color)[not_gurus]),
                marker="o", s=30, zorder=3,
                label="delegating")

    plt.legend()
    plt.show()
    return dict_colors
