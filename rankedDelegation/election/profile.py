from rankedDelegation.utils.cached import DeleteCacheMixin, cached_property
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

    def attribute_gurus(self, rule):
        self.delete_cache()
        for voter in self.list_voters:
            voter.reset()
        rule(self.list_voters)

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
