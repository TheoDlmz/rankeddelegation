from rankedDelegation.utils.cached import DeleteCacheMixin, cached_property
from rankedDelegation.rules.arborescences import minimalArborescence
import numpy as np


class Voter:
    """
    Class of a voter.

    Parameters
    ----------
    vote
        The vote of the voter if it is a casting voter
    Attributes
    ----------
    vote
        The vote of the voter. Is different than None iff the voter
        is a casting voter
    delegatees
        The order list of delegatees of the voter.
    guru
        The guru of the voter
    path_to_guru
        The path from the voter to its guru.
    id
        The id of the voter

    """
    def __init__(self, vote=None):
        self.vote = vote
        self.id = None
        self.delegatees = []
        self.path_to_guru = []
        self.guru = None

    def reset(self):
        """
        This function reset the guru of the voter.

        Returns
        -------
        Voter
            The object itself.
        """
        self.path_to_guru = []
        self.guru = None
        return self

    def delegate(self, voter_list):
        """
        This function can be used to set the ordered list of delegatees.

        Parameters
        ----------
        voter_list
            The ordered list of delegatees.
        Returns
        -------
        Voter
            The object itself.
        """
        self.delegatees = voter_list
        return self

    def set_guru(self, guru, path_to_guru=[]):
        """
        This function can be used by a voting rule to set the guru of the voter.
        Parameters
        ----------
        guru
            The guru of the voter.
        path_to_guru
            The path of ranks to the guru.
        Returns
        -------
        Voter
            The object itself.
        """
        self.guru = guru
        self.path_to_guru = path_to_guru
        return self

    def set_id(self, id_voter):
        """
        This function can be used to change the id of the voter.

        Parameters
        ----------
        id_voter
            The new id of the voter.

        Returns
        -------
        Voter
            The object itself.
        """
        self.id = id_voter
        return self


class Election(DeleteCacheMixin):
    def __init__(self):
        self.list_voters = []

    def add_voter(self, voter):
        voter.set_id(len(self.list_voters))
        self.list_voters.append(voter)

    def attribute_gurus(self, rule=None):
        self.delete_cache()
        for voter in self.list_voters:
            voter.reset()
        if rule is not None:
            rule(self)

    @cached_property
    def votes(self):
        votes_list = []
        for voter in self.list_voters:
            if voter.guru is None:
                continue
            votes_list.append(voter.guru.vote)
        return votes_list

    @cached_property
    def results(self):
        votes = self.votes
        count = [[votes.count(x), x] for x in set(votes)]
        return count

    @cached_property
    def winner(self):
        results = self.results
        return max(results)[1]

    @cached_property
    def max_rank(self):
        max_rank = 0
        for voter in self.list_voters:
            if len(voter.path_to_guru) > 0:
                max_rank = max(max_rank, max(voter.path_to_guru))
        return max_rank

    @cached_property
    def max_length(self):
        max_length = 0
        for voter in self.list_voters:
            max_length = max(max_length, len(voter.path_to_guru))
        return max_length

    @cached_property
    def max_power(self):
        dict_power = {}
        for voter in self.list_voters:
            if voter.guru is not None:
                guru_id = voter.guru.id
                if guru_id not in dict_power:
                    dict_power[guru_id] = 0
                dict_power[guru_id] += 1
        max_power = max([dict_power[k] for k in dict_power])
        return max_power

    @cached_property
    def sum_rank(self):
        sum_rank = 0
        for voter in self.list_voters:
            if len(voter.path_to_guru) > 0:
                sum_rank += voter.path_to_guru[0]
        return sum_rank

    @cached_property
    def max_sum(self):
        max_sum = 0
        for voter in self.list_voters:
            if len(voter.path_to_guru) > 0:
                max_sum = max(max_sum, np.sum(voter.path_to_guru))
        return max_sum


    @cached_property
    def unpopularity(self):
        voters = self.list_voters

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

            elif voter.guru is not None:
                choice = voter.path_to_guru[0]
                for j, delegatee in enumerate(voter.delegatees):
                    if delegatee.id in tab_voters:
                        rank = 2
                        if j+1 < choice:
                            rank = 1
                        elif j+1 > choice:
                            rank = 3
                        tab_edges.append((voter.id, delegatee.id, rank))

        dict_paths, dict_gurus = minimalArborescence(tab_edges, tab_voters)
        total = 0
        for k in dict_paths:
            if len(dict_paths[k]) > 0:
                total += dict_paths[k][0] - 2
        return -total
