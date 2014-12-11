
import random
import collections
import math

class CorpusIntegrityError(Exception):
    pass

class Segment(object):
    """
    Class for segment symbols
    """

    def __init__(self, symbol):
        #None defaults are for word-boundary symbols
        self.symbol = symbol
        self.features = dict()

    @property
    def category(self):
        if len(self.features) == 0:
            return None
        if 'voc' in self.features:
            feat_type = 'spe'
        elif 'consonantal' in self.features:
            feat_type = 'hayes'
        else:
            return None
        category = []
        if feat_type == 'spe':
            if self.features['voc'] == '+':
                if self.features['high'] == '.':
                    category.append('Diphthong')
                    if self.features['back'] == '-':
                        category.append('Front')
                    else:
                        category.append('Back')
                else:
                    category.append('Vowel')
                    #Height, backness, roundness
                    if self.features['low'] == '-' and self.features['high'] == '+':
                        if self.features['tense'] == '+':
                            category.append('Close')
                        else:
                            category.append('Near close')
                    elif self.features['low'] == '-' and self.features['high'] == '-':
                        if self.features['tense'] == '+':
                            category.append('Close mid')
                        else:
                            category.append('Open mid')
                    elif self.features['low'] == '+' and self.features['high'] == '-':
                        if self.features['tense'] == '+':
                            category.append('Open')
                        else:
                            category.append('Open')
                    else:
                        category.append(None)

                    if self.features['back'] == '+':
                        if self.features['tense'] == '+':
                            category.append('Back')
                        else:
                            category.append('Near back')
                    elif self.features['back'] == 'n':
                        category.append('Central')
                    elif self.features['back'] == '-':
                        if self.features['tense'] == '+':
                            category.append('Front')
                        else:
                            category.append('Near front')
                    else:
                        category.append(None)
                    if self.features['round'] == '+':
                        category.append('Rounded')
                    else:
                        category.append('Unrounded')
            elif self.features['voc'] == '-':
                category.append('Consonant')
                #Place, manner, voicing
                if (self.features['ant'] == '+' and self.features['cor'] == '-' and
                        self.features['back'] == '-'):
                            category.append('Labial')
                elif (self.features['ant'] == '+' and self.features['cor'] == '-' and
                        self.features['back'] == '+' and self.features['high'] == '+'):
                            category.append('Labial')
                elif (self.features['ant'] == '+' and self.features['cor'] == '-' and
                        self.features['back'] == '-'):
                            category.append('Labiodental')
                elif (self.features['ant'] == '+' and self.features['cor'] == '+' and
                        self.features['back'] == '-'):
                            category.append('Dental')
                elif (self.features['ant'] == '-' and self.features['cor'] == '+' and
                        self.features['back'] == '-' and self.features['high'] == '-'):
                            category.append('Alveolar')
                elif (self.features['ant'] == '-' and self.features['cor'] == '+' and
                        self.features['back'] == '-' and self.features['high'] == '+'):
                            category.append('Alveopalatal')
                elif (self.features['ant'] == '-' and self.features['cor'] == '-' and
                        self.features['back'] == '-'):
                            category.append('Palatal')
                elif (self.features['ant'] == '-' and self.features['cor'] == '-' and
                        self.features['back'] == '+' and self.features['high'] == '+'):
                            category.append('Velar')
                elif (self.features['ant'] == '-' and self.features['cor'] == '-' and
                        self.features['back'] == '+' and self.features['high'] == '-'):
                            category.append('Uvular')
                elif (self.features['low'] == '+' and
                        self.features['back'] == '+'):
                            category.append('Pharyngeal')
                elif (self.features['low'] == '+' and self.features['back'] == '-'):
                            category.append('Glottal')
                else:
                    category.append(None)
                if (self.features['son'] == '-' and self.features['nasal'] == '-' and
                        self.features['cont'] == '-'):
                            category.append('Stop')
                elif (self.features['nasal'] == '+'):
                            category.append('Nasal')
                elif (self.features['son'] == '-' and self.features['nasal'] == '-' and
                        self.features['cont'] == '+'):
                            category.append('Fricative')
                elif (self.features['del_rel'] == '+'):
                            category.append('Affricate')
                elif (self.features['son'] == '+' and self.features['nasal'] == '-'):
                            category.append('Approximate')
                elif (self.features['son'] == '+' and self.features['lat'] == '+'):
                            category.append('Lateral approximate')
                else:
                    category.append(None)
                if self.features['voice'] == '+':
                    category.append('Voiced')
                elif self.features['voice'] == '-':
                    category.append('Voiceless')
                else:
                    category.append(None)
            else:
                return None
        elif feat_type == 'hayes':
            if self.features['diphthong'] == '+':
                category.append('Diphthong')
                if self.features['front_diphthong'] == '+':
                    category.append('Front')
                else:
                    category.append('Back')
            elif self.features['syllabic'] == '+':
                category.append('Vowel')
                #Height, backness, roundness
                if self.features['low'] == '-' and self.features['high'] == '+':
                    if self.features['tense'] == '+':
                        category.append('Close')
                    else:
                        category.append('Near close')
                elif self.features['low'] == '-' and self.features['high'] == '-':
                    if self.features['tense'] == '+':
                        category.append('Close mid')
                    else:
                        category.append('Open mid')
                elif self.features['low'] == '+' and self.features['high'] == '-':
                    if self.features['tense'] == '+':
                        category.append('Open')
                    else:
                        category.append('Open')
                else:
                    category.append(None)

                if self.features['back'] == '+' and self.features['front'] == '-':
                    if self.features['tense'] == '+':
                        category.append('Back')
                    else:
                        category.append('Near back')
                elif self.features['back'] == '-' and self.features['front'] == '-':
                    category.append('Central')
                elif self.features['back'] == '-' and self.features['front'] == '+':
                    if self.features['tense'] == '+':
                        category.append('Front')
                    else:
                        category.append('Near front')
                else:
                    category.append(None)
                if self.features['round'] == '+':
                    category.append('Rounded')
                else:
                    category.append('Unrounded')

            elif self.features['syllabic'] == '-':
                category.append('Consonant')
                if self.features['labial'] == '+':
                    category.append('Labial')
                elif self.features['labiodental'] == '+':
                    category.append('Labiodental')
                elif self.features['anterior'] == '+' and self.features['coronal'] == '+':
                    category.append('Dental')
                elif self.features['anterior'] == '-' and self.features['coronal'] == '+':
                    category.append('Alveopalatal')
                elif self.features['dorsal'] == '+' and self.features['coronal'] == '+':
                    category.append('Palatal')
                elif self.features['dorsal'] == '+' and self.features['front'] == '+':
                    category.append('Palatal')
                elif self.features['dorsal'] == '+'and self.features['back'] == '+':
                    category.append('Uvular')
                elif self.features['dorsal'] == '+':
                    category.append('Velar')
                elif (self.features['dorsal'] == '-' and self.features['coronal'] == '-'):
                    category.append('Glottal')
                else:
                    category.append(None)
                if (self.features['sonorant'] == '-' and self.features['continuant'] == '-'
                        and self.features['nasal'] == '-' and self.features['delayed_release'] == '-'):
                    category.append('Stop')
                elif (self.features['nasal'] == '+'):
                    category.append('Nasal')
                elif (self.features['trill'] == '+'):
                    category.append('Trill')
                elif (self.features['tap'] == '+'):
                    category.append('Tap')
                elif (self.features['sonorant'] == '-' and self.features['continuant'] == '+'):
                    category.append('Fricative')
                elif (self.features['sonorant'] == '-' and self.features['continuant'] == '-'
                        and self.features['delayed_release'] == '+'):
                    category.append('Affricate')
                elif (self.features['sonorant'] == '+' and self.features['lateral'] == '-'):
                    category.append('Approximate')
                elif (self.features['sonorant'] == '+' and self.features['lateral'] == '+'):
                    category.append('Lateral approximate')
                else:
                    category.append(None)
                if self.features['voice'] == '+':
                    category.append('Voiced')
                else:
                    category.append('Voiceless')
            else:
                return None
        return category

    def specify(self,feature_dict):
        self.features = feature_dict

    def feature_match(self, specification):
        """
        Return true if segment matches specification, false otherwise.
        Specification can be a single feature value '+feature' or a list of
        feature values ['+feature1','-feature2']
        """
        if isinstance(specification,str):
            try:
                if self.features[specification[1:]]!=specification[0]:
                    return False
            except KeyError:
                return False
        elif isinstance(specification,list):
            for f in specification:
                try:
                    if self.features[f[1:]]!=f[0]:
                        return False
                except KeyError:
                    return False
        return True

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.symbol

    def __eq__(self, other):
        """Two segments are considered equal if their symbol attributes match

        """
        if isinstance(other, Segment):
            return self.symbol == other.symbol
        else:
            return self.symbol == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self,other):
        if isinstance(other, Segment):
            return self.symbol < other.symbol
        else:
            return self.symbol < other

    def __le__(self,other):
        return (self.symbol == other.symbol or self.symbol < other.symbol)

    def __ge__(self,other):
        return (self.symbol == other.symbol or self.symbol > other.symbol)

    def __gt__(self,other):
        if isinstance(other, Segment):
            return self.symbol > other.symbol
        else:
            return self.symbol > other

    def __len__(self):
        return len(self.symbol)

class Transcription(object):
    """
    Transcription object, sequence of symbols
    """
    def __init__(self,seg_list):
        if seg_list is None:
            seg_list = []
        self._list = seg_list

    def __getitem__(self, key):
        if isinstance(key,int) or isinstance(key,slice):
            return self._list[key]
        raise(KeyError)

    def __str__(self):
        return '.'.join(self._list)

    def __iter__(self):
        for s in self._list:
            yield s

    def __add__(self, other):
        """
        Allow for Transcriptions to be added to get all the segments in each
        """
        if not isinstance(other,Transcription):
            raise(TypeError)
        return self._list + other._list

    def __eq__(self, other):
        if not isinstance(other, Transcription) and not isinstance(other,list):
            return False

        if len(other) != len(self):
            return False
        for i,s  in enumerate(self):
            if s != other[i]:
                return False
        return True

    def __lt__(self,other):
        if isinstance(other, Transcription):
            return self._list < other._list
        else:
            return self._list < other

    def __le__(self,other):
        if isinstance(other, Transcription):
            return (self._list == other._list or self._list < other._list)
        else:
            return self._list <= other

    def __ge__(self,other):
        if isinstance(other, Transcription):
            return (self._list == other._list or self._list > other._list)
        else:
            return self._list >= other

    def __gt__(self,other):
        if isinstance(other, Transcription):
            return self._list > other._list
        else:
            return self._list > other

    def match_segments(self, segments):
        """
        Returns a matching segments from a list of segments
        """
        match = list()
        for s in self:
            if s in segments:
                match.append(s)
        return match

    def get_env(self,pos):
        """
        Return the symbol to the left and the symbol to the right of the position
        """

        if len(self) == 1:
            lhs = '#'
            rhs = '#'
        elif pos == 0:
            lhs = '#'
            rhs = self[pos+1]
        elif pos == len(self)-1:
            lhs = self[pos-1]
            rhs = '#'
        else:
            lhs = self[pos-1]
            rhs = self[pos+1]
        return lhs,rhs

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self._list)

class FeatureMatrix(object):
    """
    An object that stores feature values for segments


    Attributes
    ----------
    name : str
        An informative identifier for the feature matrix

    feature_entries : list of Dictionary
        Dictionaries in the list should contain feature names as keys
        and feature values as values, as well as a special key-value pair
        for the symbol

    """

    def __init__(self, name,feature_entries):
        self.name = name
        self._features = None
        self.possible_values = set()
        self.matrix = {}
        self._default_value = 'n'
        for s in feature_entries:
            if self._features is None:
                self._features = {k for k in s.keys() if k != 'symbol'}
            self.matrix[s['symbol']] = {k:v for k,v in s.items() if k != 'symbol'}
            self.possible_values.update({v for k,v in s.items() if k != 'symbol'})

        #What are these?
        self.matrix['#'] = {'#':''}
        self.matrix[''] = {'*':''}

    def __eq__(self, other):
        if not isinstance(other,FeatureMatrix):
            return False
        if self.matrix == other.matrix:
            return True
        return False

    def __setstate__(self,state):
        if '_features' not in state:
            state['_features'] = state['features']
        self.__dict__.update(state)

        #Backwards compatability
        if '_default_value' not in state:
            self._default_value = 'n'

    def validate(self):
        """
        Make sure that all segments in the matrix have all the features.
        If not, add an unspecified value for that feature to them.
        """
        for v in self.possible_values:
            if v not in ['+','-','.']:
                default_value = v
                break
        #dictionary
        for k,v in self.matrix.items():
            for f in self._features:
                if f not in v:
                    self.matrix[k][f] = self._default_value

    @property
    def default_value(self):
        return self._default_value

    @property
    def features(self):
        """
        Get a list of features that are used in this feature system

        Returns
        -------
        list
            Sorted list of the names of all features in the matrix
        """
        return sorted(list(self._features))

    def add_segment(self,seg,feat_spec):
        """
        Add a segment with a feature specification to the feature system

        Attributes
        ----------
        seg : str
            Segment symbol to add to the feature system

        feat_spec : dictionary
            Dictionary with features as keys and feature values as values

        """

        #Validation
        for f in feat_spec.keys():
            if f not in self._features:
                raise(AttributeError('The segment \'%s\' has a feature \'%s\' that is not defined for this feature matrix' %(seg,f)))

        self.matrix[seg] = feat_spec

    def add_feature(self,feature):
        """
        Add a feature to the feature system

        Attributes
        ----------
        feature : str
            Name of the feature to add to the feature system

        """

        self._features.update({feature})
        self.validate()

    @property
    def segments(self):
        """
        Return a list of segment symbols that are specified in the feature
        system

        Returns
        -------
        list
            List of all the segments with feature specifications
        """
        return list(self.matrix.keys())

    def seg_to_feat_line(self,symbol):
        """
        Get a list of feature values for a given segment in the order
        that features are return in get_feature_list

        Use for display purposes

        Attributes
        ----------
        symbol : str
            Segment symbol to look up

        Returns
        -------
        list
            List of feature values for the symbol, as well as the symbol itself
        """
        featline = [symbol] + [ self.matrix[symbol][feat]
                            for feat in self.features]
        return featline

    def __getitem__(self,item):
        if isinstance(item,str):
            return self.matrix[item]
        elif isinstance(item,tuple):
            return self.matrix[item[0]][item[1]]

    def __delitem__(self,item):
        del self.matrix[item]

    def __contains__(self,item):
        return item in list(self.matrix.keys())

    def __setitem__(self,key,value):
        self.matrix[key] = value

    def __len__(self):
        return len(self.matrix)

class Word(object):
    """An object representing a word in a corpus

    A Corpus object creates Words from information in a user-supplied text file.
    The names of the attributes of a Word are therefore unpredictable.

    Attributes
    ----------
    spelling : str
        A representation of a word that lacks phonological information.

    transcription : list of Segments
        A representation of a word that includes phonological information.

    tiers : list
        A list of tiers, which are created with the self.add_tier method. This
        is an empty list if not tiers have been created.

    descriptors : list of str
        A list of the names of the attributes of a Word instance. This is
        automatically generated based on the contents of the original corpus


    """

    _corpus = None

    _freq_names = ['abs_freq', 'freq_per_mil','sfreq',
        'lowercase_freq', 'log10_freq']

    def __init__(self, **kwargs):

        self.tiers = list()
        self.transcription = None
        self.spelling = None
        self.frequency = 0
        self.descriptors = ['spelling','transcription']
        self.wordtokens = list()

        for key, value in kwargs.items():
            key = key.lower()
            if key in self._freq_names:
                key = 'frequency'
            if isinstance(value,list):
                #transcription type stuff
                if key != 'transcription':
                    self.tiers.append(key)
                value = Transcription(value)
            elif key != 'spelling':
                try:
                    f = float(value)
                    if not math.isnan(f) and not math.isinf(f):
                        value = f
                except (ValueError, TypeError):
                    pass
            setattr(self,key, value)
            if key not in self.descriptors:
                self.descriptors.append(key)
        if self.spelling is None and self.transcription is None:
            raise(ValueError('Words must be specified with at least a spelling or a transcription.'))
        if self.spelling is None:
            self.spelling = ''.join(map(str,self.transcription))

    def __getstate__(self):
        state = self.__dict__.copy()
        state['wordtokens'] = list()
        #for k,v in state.items():
        #    if (k == 'transcription' or k in self.tiers) and v is not None:
        #        state[k] = [x.symbol for x in v] #Only store string symbols
        return state

    def __setstate__(self, state):
        self.transcription = None
        self.spelling = None
        self.frequency = 0
        if 'wordtokens' not in state:
            state['wordtokens'] = list()
        self.__dict__.update(state)



    def add_tier(self, tier_name, tier_segments):
        """Adds a new tier attribute to a Word instance

        Parameters
        ----------
        tier_name : str
            User-supplied name for the new tier

        tier_features: list of str
            User-supplied list of phonological features values that define
            which segments are included in the tier

        """
        matching_segs = self.transcription.match_segments(tier_segments)
        new_tier = Transcription(matching_segs)
        setattr(self,tier_name,new_tier)
        if tier_name not in self.tiers:
            self.tiers.append(tier_name)

    def remove_tier(self, tier_name):
        """Deletes a tier attribute from a Word

        Parameters
        ----------
        tier_name : str
            Name of tier attribute to be deleted.

        Notes
        ----------
        If tier_name is not a valid attribute, this function does nothing. It
        does not raise an error.

        """
        try:
            self.tiers.remove(tier_name)
            delattr(self, tier_name)
        except ValueError:
            pass #tier_name does not exist

    def details(self):
        """Formatted printout of a Word's attributes and their values.

        Notes
        ----------
        This is intended for debugging and interactive mode.
        """
        print('-'*25)
        for description in self.descriptors:
            print('{}: {}'.format(description, getattr(self,description)))
        print('-'*25+'\n')

    def get_env(self,pos,tier_name):
        """Get details of a particular environment in a Word

        Parameters
        ----------
        pos : int
            A position in the word, so 0<=pos<=len(self)

        Returns
        ----------
        e : Environment
            Environment of the segment at the given position in the word

        """
        tier = getattr(self,tier_name)
        lhs, rhs = tier.get_env(pos)
        e = Environment(lhs, rhs)

        return e

    def __repr__(self):
        return '<Word: \'%s\'>' % self.spelling

    def __str__(self):
        return self.spelling


    def __eq__(self, other):
        if not isinstance(other,Word):
            return False
        if self.spelling != other.spelling:
            return False
        if self.transcription != other.transcription:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.spelling < other.spelling

    def __gt__(self, other):
        return self.spelling > other.spelling

    def __le__(self, other):
        return self.spelling <= other.spelling

    def __ge__(self, other):
        return self.spelling >= other.spelling

class Environment(object):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return '_'.join([self.lhs, self.rhs])

    def __hash__(self):
        return hash((lhs,rhs))

    def __eq__(self,other):
        """Two Environments are equal if they share a left AND right hand side

        """
        if not isinstance(other,Environment):
            return False

        if other.lhs != self.lhs:
            return False
        if other.rhs != self.rhs:
            return False
        return True

    def __ne__(self,other):
        return not self.__eq__(other)


class EnvironmentFilter(object):
    """
    Environments are strings of the form "[+feature,-feature]_[+feature]"
    or "[+feature]_" or "a_b" or "_b"
    """
    def __init__(self, corpus, env):

        #there's a problem where some feature names have underscores in them
        #so doing lhs,rhs=env.split('_') causes unpacking problems
        #this in an awakward work-around that checks to see if either side of
        #the environment is a list of features, by looking for brackets, then
        #splits by brackets if necessary. However, I can't split out any
        #starting brackets [ because I also use those for identifying lists
        #at a later point
        #otherwise, if its just segment envrionments, split by underscore
        if ']_[' in env:
            #both sides are lists
            lhs, rhs = env.split(']_')
        elif '_[' in env:
            #only the right hand side is a list of a features
            lhs, rhs = env.split('_', maxsplit=1)
        elif ']_' in env:
            #only the left hand side is a list of features
            lhs, rhs = env.split(']_')
        else: #both sides are segments
            lhs, rhs = env.split('_')

        if not lhs:
            self.lhs_string  = ''
            self.lhs = list()
        elif lhs.startswith('['):
            self.lhs_string = lhs
            lhs = lhs.lstrip('[')
            lhs = lhs.rstrip(']')
            #lhs = {feature[1:]:feature[0] for feature in lhs.split(',')}
            lhs = lhs.split(',')
            self.lhs = corpus.features_to_segments(lhs)
        #else it's a segment, just leave it as the string it already is
        else:
            self.lhs_string = lhs
            self.lhs = [lhs]

        if not rhs:
            self.rhs_string  = ''
            self.rhs = list()
        elif rhs.startswith('['):
            self.rhs_string = rhs
            rhs = rhs.lstrip('[')
            rhs = rhs.rstrip(']')
            #rhs = {feature[1:]:feature[0] for feature in rhs.split(',')}
            rhs = rhs.split(',')
            self.rhs = corpus.features_to_segments(rhs)
        #else it's a segment, just leave it as the string it already is
        else:
            self.rhs_string = rhs
            self.rhs = [rhs]

    def __str__(self):
        return '_'.join([self.lhs_string,self.rhs_string])

    def __eq__(self, other):
        if not hasattr(other,'lhs'):
            return False
        if not hasattr(other,'rhs'):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def __hash__(self):
        return hash((self.rhs_string, self.lhs_string))

    def __contains__(self, item):
        if not isinstance(item, Environment):
            return False
        if self.rhs:
            if item.rhs not in self.rhs:
                return False
        if self.lhs:
            if item.lhs not in self.lhs:
                return False
        return True


class Corpus(object):
    """
    Attributes
    ----------

    name : str
        Name of the corpus, used only for easy of reference

    wordlist : dict
        Dictionary where every key is a unique string representing a word in a
        corpus, and each entry is a Word object

    specifier : FeatureSpecifier
        See the FeatureSpecifier object

    inventory : list
        list of all Segments that appear at least once in self.wordlist.values()

    orthography : list
        list of one-character strings that appear in self.wordlist.keys()

    custom : bool
        True if this is a user-supplied corpus, False if it is a built-in corpus

    feature_system : str
        Name of the feature system used for the corpus
    """

    #__slots__ = ['name', 'wordlist', 'specifier',
    #            'inventory', 'orthography', 'custom', 'feature_system',
    #            'has_frequency_value','has_spelling_value','has_transcription_value']

    def __init__(self, name):
        self.name = name
        self.wordlist = dict()
        self.specifier = None
        self._inventory = {'#' : Segment('#')} #set of Segments, if transcription exists
        self.orthography = {'#'} #set of orthographic characters
        self.has_frequency = True
        self.has_spelling = False
        self.has_transcription = False
        self._tiers = []
        self._freq_base = dict()
        self.transcription_freq_base = {'token':None, 'type':None}
        self.spelling_freq_base = {'token':None, 'type':None}

    def __eq__(self, other):
        if not isinstance(other,Corpus):
            return False
        if self.wordlist != other.wordlist:
            return False
        return True

    def get_frequency_base(self, sequence_type, count_what, gramsize = 1,
                        probability = False):
        if (sequence_type, count_what, gramsize) not in self._freq_base:
            freq_base = collections.defaultdict(float)
            for word in self:
                if count_what == 'token':
                    freq = word.frequency
                else:
                    freq = 1
                grams = zip(*[getattr(word, sequence_type)[i:] for i in range(gramsize)])
                for x in grams:
                    if len(x) == 1:
                        x = x[0]
                    freq_base[x] += freq
            freq_base['total'] = sum(value for value in freq_base.values())
            self._freq_base[(sequence_type, count_what, gramsize)] = freq_base
        freq_base = self._freq_base[(sequence_type, count_what, gramsize)]
        return_dict = { k:v for k,v in freq_base.items()}
        if probability:
            return_dict = { k:v/freq_base['total'] for k,v in return_dict.items()}
        return return_dict

    def get_phone_probs(self, sequence_type, count_what, gramsize = 1,
                        probability = True, preserve_position = True,
                        log_count = True):
        if (sequence_type, count_what, gramsize, probability,
                    preserve_position, log_count) not in self._freq_base:
            freq_base = collections.defaultdict(float)
            totals = collections.defaultdict(float)
            for word in self:
                if count_what == 'token':
                    freq = word.frequency
                    if log_count:
                        freq = math.log(freq)
                else:
                    freq = 1
                grams = zip(*[getattr(word, sequence_type)[i:] for i in range(gramsize)])
                for i, x in enumerate(grams):
                    #if len(x) == 1:
                    #    x = x[0]
                    if preserve_position:
                        x = (x,i)
                        totals[i] += freq

                    freq_base[x] += freq

            if not preserve_position:
                freq_base['total'] = sum(value for value in freq_base.values())
            else:
                freq_base['total'] = totals
            self._freq_base[(sequence_type, count_what, gramsize, probability,
                    preserve_position, log_count)] = freq_base
        freq_base = self._freq_base[(sequence_type, count_what, gramsize,
                    probability,preserve_position, log_count)]
        return_dict = { k:v for k,v in freq_base.items()}
        if probability and not preserve_position:
            return_dict = { k:v/freq_base['total'] for k,v in return_dict.items()}
        elif probability:
            return_dict = { k:v/freq_base['total'][k[1]] for k,v in return_dict.items() if k != 'total'}
        return return_dict

    @property
    def tiers(self):
        return self._tiers

    @property
    def attributes(self):
        att = list()
        if self.has_spelling:
            att.append('spelling')
        if self.has_transcription:
            att.append('transcription')
        att.append('frequency')
        att += self.tiers
        return att

    @property
    def words(self):
        return sorted(list(self.wordlist.keys()))

    def features_to_segments(self, feature_description):
        segments = list()
        for k,v in self._inventory.items():
            if v.feature_match(feature_description):
                segments.append(k)
        return segments

    def segment_to_features(self, seg):
        try:
            features = self.specifier.matrix[seg]
        except TypeError:
            features = self.specifier.matrix[seg.symbol]
        return features

    def add_tier(self, tier_name, spec):
        if tier_name not in self._tiers:
            self._tiers.append(tier_name)
        if isinstance(spec, str):
            tier_segs = self.features_to_segments(spec)
        else:
            tier_segs = spec
        for word in self:
            word.add_tier(tier_name,tier_segs)

    def remove_tier(self, tier_name):
        for i in range(len(self._tiers)):
            if self._tiers[i] == tier_name:
                del self._tiers[i]
                break
        for word in self:
            word.remove_tier(tier_name)

    def __setstate__(self,state):
        try:
            if '_inventory' not in state:
                state['_inventory'] = state['inventory']
            if 'has_spelling' not in state:
                state['has_spelling'] = state['has_spelling_value']
            if 'has_transcription' not in state:
                state['has_transcription'] = state['has_transcription_value']
            if '_freq_base' not in state:
                state['_freq_base'] = dict()
            self.__dict__.update(state)
            self._specify_features()

            #Backwards compatability
            word = self.random_word()
            if '_tiers' not in state:
                self._tiers = word.tiers
            if not isinstance(word.transcription, Transcription):
                for w in self:
                    w.transcription = Transcription(w.transcription)
                    for t in w.tiers:
                        setattr(w,t,Transcription(getattr(w,t)))
        except Exception as e:
            raise(CorpusIntegrityError("An error occurred while loading the corpus: {}.\nPlease redownload or recreate the corpus.".format(str(e))))


    def _specify_features(self):
        if self.specifier is not None:
            for k in self._inventory.keys():
                try:
                    self._inventory[k].specify(self.specifier[k])
                except KeyError:
                    pass

    def check_coverage(self):
        if not self.specifier is not None:
            return []
        return [x for x in self._inventory.keys() if x not in self.specifier]

    def phonological_search(self,seg_list,envs=None, sequence_type = 'transcription',
                            call_back = None, stop_check = None):
        if call_back is not None:
            call_back('Searching...')
            call_back(0,len(self))
            cur = 0
        if envs is not None:
            envs = [EnvironmentFilter(self, env) for env in envs]
        results = list()
        for word in self:
            if stop_check is not None and stop_check():
                return
            if call_back is not None:
                cur += 1
                if cur % 20 == 0:
                    call_back(cur)
            founds = list()
            for pos,seg in enumerate(getattr(word, sequence_type)):
                if not seg in seg_list:
                    continue
                if envs is None:
                    founds.append((seg,))
                    continue
                word_env = word.get_env(pos, sequence_type)
                for env in envs:
                    if word_env in env:
                        founds.append((seg,env))
                        break
            if founds:
                results.append((word, founds))
        return results

    def iter_sort(self):
        """Sorts the keys in the corpus dictionary, then yields the values in that order

        """
        sorted_list = sorted(self.wordlist.keys())
        for word in sorted_list:
            yield self.wordlist[word]

    def set_feature_matrix(self,matrix):
        """
        Set the feature system to be used by the corpus and make sure
        every word is using it too.

        Attributes
        ----------
        matrix : FeatureMatrix
            New feature system to use in the corpus
        """
        self.specifier = matrix
        self._specify_features()

    @property
    def inventory(self):
        """
        Returns a sorted list of segments used in transcriptions

        Returns
        -------
        list
            Sorted list of segment symbols used in transcriptions in the corpus
        """
        return sorted(list(self._inventory.values()))

    def get_random_subset(self, size, new_corpus_name='randomly_generated'):
        """Get a new corpus consisting a random selection from the current corpus

        Parameters
        ----------
        size : int
            Size of new corpus

        new_corpus_name : str

        Returns
        ----------
        new_corpus : Corpus
            New corpus object with len(new_corpus) == size
        """
        new_corpus = Corpus(new_corpus_name)
        while len(new_corpus) < size:
            word = self.random_word()
            new_corpus.add_word(word, allow_duplicates=False)
        new_corpus.specifier = self.specifier
        return new_corpus

    def add_word(self, word, allow_duplicates=True):
        """Add a word to the Corpus.
        If allow_duplicates is True, then words with identical spelling can
        be added. They are kept sepearate by adding a "silent" number to them
        which is never displayed to the user. If allow_duplicates is False,
        then duplicates are simply ignored.

        Parameters
        ----------
        word : Word
            Word object to be added

        allow_duplicates : bool

        """
        word._corpus = self
        #If the word doesn't exist, add it
        try:
            check = self.find(word.spelling, keyerror=True)
            if allow_duplicates:
                #Some words have more than one entry in a corpus, e.g. "live" and "live"
                #so they need to be assigned unique keys

                n = 0
                while True:
                    n += 1
                    #key = '{} ({})'.format(word.spelling.lower(),n)
                    key = '{} ({})'.format(word.spelling,n)
                    try:
                        check = self.find(key, keyerror=True)
                    except KeyError:
                    #if isinstance(check, EmptyWord):
                        self.wordlist[key] = word
                        break
        except KeyError:
            self.wordlist[word.spelling] = word
            if word.spelling is not None:
                self.orthography.update(word.spelling)
                if not self.has_spelling:
                    self.has_spelling = True

        if word.transcription is not None:
            for s in word.transcription:
                if s not in self._inventory:
                    self._inventory[s] = Segment(s)
            if not self.has_transcription:
                self.has_transcription = True

    def get_or_create_word(self, spelling, transcription):
        words = self.find_all(spelling)
        if transcription is None:
            transcription = list()
        for w in words:
            if str(w.transcription) == '.'.join(transcription):
                word = w
                break
        else:
            word = Word(spelling=spelling,transcription=transcription)
            self.add_word(word)
        return word

    def random_word(self):
        """Return a randomly selected Word

        """
        word = random.choice(list(self.wordlist.keys()))
        return self.wordlist[word]

    def get_features(self):
        """Get a list of the features used to describe Segments

        Returns
        ----------
        list of str

        """
        return self.specifier.features

    def find(self, word, keyerror=True, ignore_case = False):
        """Search for a Word in the corpus
        If keyerror == True, then raise a KeyError if the word is not found
        If keyerror == False, then return an EmptyWord if the word is not found

        Parameters
        ----------
        word : str
            String representing the spelling of the word (not transcription)

        keyerror : bool
            Set whether a KeyError should be raised if a word is not found

        Returns
        ----------
        result : Word or EmptyWord


        Raises
        ----------
        KeyError if keyerror == True and word is not found

        """
        patterns = [word]
        if ignore_case:
            patterns.append(word.lower())
            patterns.append(word.title())
        for w in patterns:
            key = w
            try:
                result = self.wordlist[w]
                return result
            except KeyError:
                try:
                    key = '{} (1)'.format(w)
                    result = [self.wordlist[key]]
                    return result
                except KeyError:
                    pass

        raise KeyError('The word \"{}\" is not in the corpus'.format(word))

    def find_all(self,spelling):
        words = list()
        try:
            words.append(self.wordlist[spelling])
            count = 0
            while True:
                count += 1
                try:
                    words.append(self.wordlist['{} ({})'.format(spelling,count)])
                except KeyError:
                    break
        except KeyError:
            pass
        return words

    def __contains__(self,item):
        return self.wordlist.__contains__(item)

    def __len__(self):
        return len(self.wordlist)

    def __setitem__(self,item,value):
        self.wordlist[item] = value

    def __getitem__(self,item):
        return self.wordlist[item]

    def __iter__(self):
        return iter(self.wordlist.values())