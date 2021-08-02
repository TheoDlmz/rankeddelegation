from rankedDelegation.utils.cached import DeleteCacheMixin, cached_property
from rankedDelegation.rules.arborescences import LPArborescence
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

    Examples
    --------
    >>> voters = [Voter() for _ in range(5)]
    >>> voters[0].delegate([voters[i] for i in [2,4,3]]).delegatees
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
    """
    This class run an election with liquid democracy

    Attributes
    ----------
    list_voters: list
        The list of the voters
    """
    def __init__(self):
        self.list_voters = []

    def add_voter(self, voter):
        """
        Add one voter to the election

        Parameters
        ----------
        voter: Voter
            The voter to add

        Returns
        -------
        None

        """
        voter.set_id(len(self.list_voters))
        self.list_voters.append(voter)

    def attribute_gurus(self, rule=None):
        """
        Attribute gurus to voters with some rule

        Parameters
        ----------
        rule: function
            The rule to use to attibute gurus to voters

        Returns
        -------
            None

        """
        self.delete_cache()
        for voter in self.list_voters:
            voter.reset()
        if rule is not None:
            rule(self)

    @cached_property
    def votes(self):
        """
        Get the results of the election as a list of voters

        Returns
        -------
        list
            The list of votes

        """
        votes_list = []
        for voter in self.list_voters:
            if voter.guru is None:
                continue
            votes_list.append(voter.guru.vote)
        return votes_list

    @cached_property
    def isolated_voters(self):
        """
        Count the number of isolated voters, i.e. voters that cannot reach any guru.

        Returns
        -------
        int
            The number of isolated voters
        """
        count = 0
        for voter in self.list_voters:
            if voter.guru is None:
                count += 1
        return count

    @cached_property
    def abstaining_voters(self):
        """
        Count the number of abstaining voters, i.e. voters that do not indicates any vote
        or delegatees

        Returns
        -------
        int
            The number of abstaining voters

        """
        count = 0
        for voter in self.list_voters:
            if (voter.vote is None) and (len(voter.delegatees) == 0):
                count +=1
        return count

    @cached_property
    def results(self):
        """
        Return the results of the election

        Returns
        -------
        list
            List with pairs (score, value)

        """
        votes = self.votes
        count = [[votes.count(x), x] for x in set(votes)]
        return count

    @cached_property
    def winner(self):
        """
        Return the winner of the election

        Returns
        -------
        Object
            The winner of the election

        """
        results = self.results
        return max(results)[1]

    @cached_property
    def max_rank(self):
        """
        compute the maximal rank over all paths in the delegation graph

        Returns
        -------
        int
            The maximal rank

        """
        max_rank = 0
        for voter in self.list_voters:
            if len(voter.path_to_guru) > 0:
                max_rank = max(max_rank, max(voter.path_to_guru))
        return max_rank

    @cached_property
    def list_lengths(self):
        """
        Compute the list of all lengths of delegation paths

        Returns
        -------
        int list
            The list of delegation paths lengths

        """
        list_l = []
        for voter in self.list_voters:
            if len(voter.path_to_guru) > 0:
                list_l.append(len(voter.path_to_guru))
        return list_l

    @cached_property
    def max_length(self):
        """
        Compute the maximal length of delegation path

        Returns
        -------
        int
            The maximal length

        """
        return np.max(self.list_lengths)

    @cached_property
    def mean_length(self):
        """
        Compute the average length of delegation path

        Returns
        -------
        int
            The average length

        """
        return np.mean(self.list_lengths)

    @cached_property
    def list_powers(self):
        """
        Compute the list of gurus powers (i.e. the weight of each guru)

        Returns
        -------
        int list
            The list of gurus power

        """
        dict_power = {}
        for voter in self.list_voters:
            if voter.guru is not None:
                guru_id = voter.guru.id
                if guru_id not in dict_power:
                    dict_power[guru_id] = 0
                dict_power[guru_id] += 1
        return  list(dict_power.values())

    @cached_property
    def max_power(self):
        """
        Compute the maximal power of a guru

        Returns
        -------
        int
            The maximal amount of power of a guru

        """
        return np.max(self.list_powers)

    @cached_property
    def power_entropy(self):
        """
        Compute the power entropy of the gurus

        Returns
        -------
        float
            The power entropy

        """
        s = 0
        list_p = self.list_powers
        total_power = np.sum(list_p)
        for p in list_p:
            proba = p/total_power
            s -= proba*np.log(proba)
        return s

    @cached_property
    def list_ranks(self):
        """
        Compute the list of ranks for an arborescence

        Returns
        -------
        int list
            The list of all ranks

        """
        list_r = []
        for voter in self.list_voters:
            if len(voter.path_to_guru) > 0:
                list_r.append(voter.path_to_guru[0])
        return list_r

    @cached_property
    def sum_rank(self):
        """
        Compute the sum of all ranks for arborescences

        Returns
        -------
        int
            The sum of all ranks

        """
        return np.sum(self.list_ranks)

    @cached_property
    def avg_rank(self):
        """
        Compute the average rank in an arborescence

        Returns
        -------
        float
            The average rank

        """
        return np.mean(self.list_ranks)

    @cached_property
    def max_sum(self):
        """
        Compute the maximal sum of rank in one delegation path

        Returns
        -------
        int
            Maximal sum of rank

        """
        max_sum = 0
        for voter in self.list_voters:
            if len(voter.path_to_guru) > 0:
                max_sum = max(max_sum, np.sum(voter.path_to_guru))
        return max_sum

    @cached_property
    def total_votes(self):
        """
        Compute the number of non-isolated voters in the election

        Returns
        -------
        int
            The number of voters

        """
        return np.sum(self.list_powers)

    @cached_property
    def max_representation(self):
        """
        Compute the maximal fraction of voters that a guru represents.

        Returns
        -------
        float
            The maximal fraction of voter that a guru represent
        """
        return self.max_power/self.total_votes

    @cached_property
    def unpopularity(self):
        """
        Compute the unpopularity of an arborescence

        Returns
        -------
        int
            The unpopularity of the arborescence
        """
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

        dict_paths, dict_gurus = LPArborescence(tab_edges, tab_voters)
        total = 0
        for k in dict_paths:
            if len(dict_paths[k]) > 0:
                total += dict_paths[k][0] - 2
        return -total
