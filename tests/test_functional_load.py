
import sys
import os

from corpustools.funcload.functional_load import minpair_fl, deltah_fl
from corpustools.corpus.classes import Segment


#class NeutralizeTest(unittest.TestCase):
#    pass


def test_non_minimal_pair_corpus(unspecified_test_corpus):
    calls = [({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('s','ʃ')],
                    'frequency_cutoff':0,
                    'relative_count':True},0.125),
            ({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('s','ʃ')],
                    'frequency_cutoff':0,
                    'relative_count':False},1),
            ({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('m','n')],
                    'frequency_cutoff':0,
                    'relative_count':True},0.11111),
            ({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('m','n')],
                    'frequency_cutoff':0,
                    'relative_count':False},1),
            ({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('e','o')],
                    'frequency_cutoff':0,
                    'relative_count':True},0),
            ({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('e','o')],
                    'frequency_cutoff':0,
                    'relative_count':False},0),

            ({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('s','ʃ')],
                    'frequency_cutoff':3,
                    'relative_count':True},0.14286),
            ({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('s','ʃ')],
                    'frequency_cutoff':3,
                    'relative_count':False},1),
            ({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('m','n')],
                    'frequency_cutoff':3,
                    'relative_count':True},0),
            ({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('m','n')],
                    'frequency_cutoff':3,
                    'relative_count':False},0),
            ({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('e','o')],
                    'frequency_cutoff':3,
                    'relative_count':True},0),
            ({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('e','o')],
                    'frequency_cutoff':3,
                    'relative_count':False},0),

            ({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('s','ʃ'),
                                    ('m','n'),
                                    ('e','o')],
                    'frequency_cutoff':0,
                    'relative_count':True},0.14286),
            ({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('s','ʃ'),
                                    ('m','n'),
                                    ('e','o')],
                    'frequency_cutoff':0,
                    'relative_count':False},2),
            ({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('s','ʃ'),
                                    ('m','n'),
                                    ('e','o')],
                    'frequency_cutoff':3,
                    'relative_count':True},0.09091),
            ({'corpus': unspecified_test_corpus,
                    'segment_pairs':[('s','ʃ'),
                                    ('m','n'),
                                    ('e','o')],
                    'frequency_cutoff':3,
                    'relative_count':False},1)]

    for c,v in calls:
        assert(abs(minpair_fl(**c)-v) < 0.0001)

def test_non_minimal_pair_corpus(unspecified_test_corpus):
    calls = [({'corpus': unspecified_test_corpus,
                'segment_pairs':[('s','ʃ')],
                'frequency_cutoff':0,
                'type_or_token':'type'},0.13333),
            ({'corpus': unspecified_test_corpus,
                'segment_pairs':[('s','ʃ')],
                'frequency_cutoff':0,
                'type_or_token':'token'},0.24794),
            ({'corpus': unspecified_test_corpus,
                'segment_pairs':[('m','n')],
                'frequency_cutoff':0,
                'type_or_token':'type'},0.13333),
            ({'corpus': unspecified_test_corpus,
                'segment_pairs':[('m','n')],
                'frequency_cutoff':0,
                'type_or_token':'token'},0.00691),
            ({'corpus': unspecified_test_corpus,
                'segment_pairs':[('e','o')],
                'frequency_cutoff':0,
                'type_or_token':'type'},0),
            ({'corpus': unspecified_test_corpus,
                'segment_pairs':[('e','o')],
                'frequency_cutoff':0,
                'type_or_token':'token'},0),

            ({'corpus': unspecified_test_corpus,
                'segment_pairs':[('s','ʃ')],
                'frequency_cutoff':3,
                'type_or_token':'type'},0.16667),
            ({'corpus': unspecified_test_corpus,
                'segment_pairs':[('s','ʃ')],
                'frequency_cutoff':3,
                'type_or_token':'token'},0.25053),
            ({'corpus': unspecified_test_corpus,
                'segment_pairs':[('m','n')],
                'frequency_cutoff':3,
                'type_or_token':'type'},0),
            ({'corpus': unspecified_test_corpus,
                'segment_pairs':[('m','n')],
                'frequency_cutoff':3,
                'type_or_token':'token'},0),
            ({'corpus': unspecified_test_corpus,
                'segment_pairs':[('e','o')],
                'frequency_cutoff':3,
                'type_or_token':'type'},0),
            ({'corpus': unspecified_test_corpus,
                'segment_pairs':[('e','o')],
                'frequency_cutoff':3,
                'type_or_token':'token'},0),

            ({'corpus': unspecified_test_corpus,
                'segment_pairs':[('s','ʃ'),
                                ('m','n'),
                                ('e','o')],
                'frequency_cutoff':0,
                'type_or_token':'type'},0.26667),
            ({'corpus': unspecified_test_corpus,
                'segment_pairs':[('s','ʃ'),
                                ('m','n'),
                                ('e','o')],
                'frequency_cutoff':0,
                'type_or_token':'token'},0.25485),

            ({'corpus': unspecified_test_corpus,
                'segment_pairs':[('s','ʃ'),
                                ('m','n'),
                                ('e','o')],
                'frequency_cutoff':3,
                'type_or_token':'type'},0.16667),
            ({'corpus': unspecified_test_corpus,
                'segment_pairs':[('s','ʃ'),
                                ('m','n'),
                                ('e','o')],
                'frequency_cutoff':3,
                'type_or_token':'token'},0.25053),]


    for c,v in calls:
        assert(abs(deltah_fl(**c)-v) < 0.0001)

