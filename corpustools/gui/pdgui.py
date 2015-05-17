from collections import OrderedDict

from corpustools.gui.widgets import SegmentClassSelectWidget
from .imports import *
from .widgets import (EnvironmentSelectWidget, EnvironmentDialog, SegmentPairSelectWidget, RadioSelectWidget, TierWidget)
from .windows import FunctionWorker, FunctionDialog
import itertools

from corpustools.prod.pred_of_dist import calc_prod,calc_prod_all_envs

from corpustools.exceptions import PCTError, PCTPythonError

class PDWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        kwargs = self.kwargs
        self.results = list()
        if 'envs' in kwargs:
            for pair in kwargs['segment_pairs']:
                try:
                    res = calc_prod(kwargs['corpus'], pair[0],pair[1],
                                    kwargs['envs'],
                                    kwargs['sequence_type'],
                                    kwargs['type_token'],
                                    kwargs['strict'],
                                    True,
                                    stop_check = kwargs['stop_check'],
                                    call_back = kwargs['call_back'])
                except PCTError as e:
                    self.errorEncountered.emit(e)
                    return
                except Exception as e:
                    e = PCTPythonError(e)
                    self.errorEncountered.emit(e)
                    return
                if self.stopped:
                    return
                self.results.append(res)

        else:
            for pair in kwargs['segment_pairs']:
                try:
                    res = calc_prod_all_envs(kwargs['corpus'], pair[0],pair[1],
                                             kwargs['sequence_type'],
                                             kwargs['type_token'],
                                             True,
                                             stop_check = kwargs['stop_check'],
                                             call_back = kwargs['call_back'])
                except PCTError as e:
                    self.errorEncountered.emit(e)
                    return
                except Exception as e:
                    e = PCTPythonError(e)
                    self.errorEncountered.emit(e)
                    return
                if self.stopped:
                    return
                self.results.append(res)

        # if kwargs['pair_behavior'] == 'cols':
        #                 print(self.results)
        #                 h_avg = sum([r[0] for r in self.results])/len(self.results)
        #                 seg1_freq_sum = sum([r[2] for r in self.results])
        #                 seg2_freq_sum = sum([r[3] for r in self.results])
        #                 self.results.append([self.SegmentClassSelector.class1features,
        #                                       self.SegmentClassSelector.class2features,
        #                                       self.tierWidget.displayValue(),
        #                                       'COL-AVG',
        #                                       seg1_freq_sum,
        #                                       seg2_freq_sum,
        #                                       sum(seg1_freq_sum, seg2_freq_sum),
        #                                       h_avg,
        #                                       self.typeTokenWidget.value()])
        self.dataReady.emit(self.results)


class PDDialog(FunctionDialog):
    header = ['Sound1',
                'Sound2',
                'Tier',
                'Environment',
                'Freq. of Sound1',
                'Freq. of Sound2',
                'Freq. of env.',
                'Entropy',
                'Type or token']

    ABOUT = ['This function calculates'
                ' the predictability of distribution of two sounds, using the measure of entropy'
                ' (uncertainty). Sounds that are entirely predictably distributed (i.e., in'
                ' complementary distribution, commonly assumed to be allophonic), will have'
                ' an entropy of 0. Sounds that are perfectly overlapping in their distributions'
                ' will have an entropy of 1.',
                '',
                'Coded by Scott Mackie and Blake Allen',
                '',
                'References',
                ('Hall, K.C. 2009. A probabilistic model of phonological'
                ' relationships from contrast to allophony. PhD dissertation,'
                ' The Ohio State University.')]

    name = 'predictability of distribution'
    def __init__(self, parent, corpus, showToolTips):
        FunctionDialog.__init__(self, parent, PDWorker())
        self.parent = parent
        self.corpus = corpus
        self.showToolTips = showToolTips

        pdFrame = QFrame()
        pdlayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(corpus)

        pdlayout.addWidget(self.segPairWidget)

        addSegClassButton = QPushButton('Add a class of sounds')
        addSegClassButton.clicked.connect(self.addSegClass)
        pdlayout.addWidget(addSegClassButton)

        self.envWidget = EnvironmentSelectWidget(corpus)
        self.envWidget.setTitle('Environments (optional)')
        pdlayout.addWidget(self.envWidget)


        optionLayout = QVBoxLayout()

        self.tierWidget = TierWidget(corpus,include_spelling=False)

        optionLayout.addWidget(self.tierWidget)

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                            OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))

        optionLayout.addWidget(self.typeTokenWidget)


        self.groupSegments = RadioSelectWidget('Calculate pairs or columns',
                                               OrderedDict([('Do pairs individually', 'pairs'),
                                                   ('Average over each column', 'cols')]))

        optionLayout.addWidget(self.groupSegments)

        checkFrame = QGroupBox('Exhaustivity and uniqueness')

        checkLayout = QVBoxLayout()

        self.enforceCheck = QCheckBox('Enforce environment\nexhaustivity and uniqueness')
        self.enforceCheck.setChecked(True)

        checkLayout.addWidget(self.enforceCheck)

        checkFrame.setLayout(checkLayout)

        optionLayout.addWidget(checkFrame)

        optionFrame = QGroupBox('Options')

        optionFrame.setLayout(optionLayout)

        pdlayout.addWidget(optionFrame)

        pdFrame.setLayout(pdlayout)

        self.layout().insertWidget(0,pdFrame)

        self.setWindowTitle('Predictability of distribution')

        if self.showToolTips:
            self.segPairWidget.setToolTip(("<FONT COLOR=black>"
                            'Choose pairs of segments whose'
                            ' predictability of distribution you want to calculate. The order of the'
                            ' two sounds is irrelevant. The symbols you see here should automatically'
                            ' match the symbols used anywhere in your corpus.'
                            "</FONT>"))
            self.tierWidget.setToolTip(("<FONT COLOR=black>"
                                    'Choose which tier predictability should'
                                    ' be calculated over (e.g., the whole transcription'
                                    ' vs. a tier containing only [+voc] segments).'
                                    ' New tiers can be created from the Corpus menu.'
            "</FONT>"))
            self.typeTokenWidget.setToolTip(("<FONT COLOR=black>"
            'Choose what kind of frequency should'
                                    ' be used for the calculations. Type frequency'
                                    ' means each word is counted once. Token frequency'
                                    ' means each word is counted as often as it occurs'
                                    ' in the corpus.'
            "</FONT>"))
            self.enforceCheck.setToolTip(("<FONT COLOR=black>"
            'Indicate whether you want the program'
                                    ' to check for exhausitivity and uniqueness.'
                                    ' Checking for exhaustivity'
                                    ' will ensure that you have selected environments'
                                    ' that cover all instances of the two sounds in the'
                                    ' corpus. Checking for uniqueness'
                                    ' will ensure that the environments you'
                                    ' have selected don\'t overlap with one another.'
            "</FONT>"))
            self.envWidget.setToolTip(("<FONT COLOR=black>"
            'This screen allows you to construct multiple'
                                    ' environments in which to calculate predictability'
                                    ' of distribution. For each environment, you can specify'
                                    ' either the left-hand side or the right-hand side, or'
                                    ' both. Each of these can be specified using either features or segments.'
                                    ' Not specifying any environments will calculate the predictability of'
                                    ' distribution across all environments based on frequency alone.'
            "</FONT>"))

    def addSegClass(self):
        self.addSegClassWindow = SegmentClassSelector(self, self.corpus)
        results = self.addSegClassWindow.exec_()
        if results:
            for p in self.addSegClassWindow.pairs:
                self.segPairWidget.table.model().addRow(p)
            self.class1name = self.addSegClassWindow.class1features
            self.class2name = self.addSegClassWindow.class2features

    def generateKwargs(self):
        kwargs = {}
        segPairs = self.segPairWidget.value()
        if len(segPairs) == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one segment pair.")
            return None
        kwargs['segment_pairs'] = segPairs
        envs = self.envWidget.value()
        if len(envs) > 0:
            kwargs['envs'] = envs

        kwargs['corpus'] = self.corpus
        kwargs['sequence_type'] = self.tierWidget.value()
        kwargs['strict'] = self.enforceCheck.isChecked()
        kwargs['pair_behavior'] = self.groupSegments.value()
        kwargs['type_token'] = self.typeTokenWidget.value()
        return kwargs

    def calc(self):
        kwargs = self.generateKwargs()
        if kwargs is None:
            return
        self.thread.setParams(kwargs)
        self.thread.start()

        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            self.accept()


    def setResults(self,results):
        self.results = list()
        seg_pairs = self.segPairWidget.value()
        seg_pairs_options = 'individual'
        if seg_pairs_options == 'individual':
            for i, r in enumerate(results):
                if isinstance(r,dict):
                    for env,v in r.items():
                        self.results.append([seg_pairs[i][0],seg_pairs[i][1],
                                            self.tierWidget.displayValue(),
                                            env,
                                            v[2], # freq of seg1
                                            v[3], #freq of seg2
                                            v[1], #total_tokens
                                            v[0], #H
                                            self.typeTokenWidget.value()])
                else:
                    self.results.append([seg_pairs[i][0],seg_pairs[i][1],
                                            self.tierWidget.displayValue(),
                                            'FREQ-ONLY',
                                            r[2], # freq of seg1
                                            r[3], #freq of seg2
                                            r[1], #total_tokens
                                            r[0], #H
                                            self.typeTokenWidget.value()])

        if self.groupSegments.value() == 'cols':
                        h_avg = sum([r[0] for r in results])/len(results)
                        seg1_freq_sum = sum([r[2] for r in results])
                        seg2_freq_sum = sum([r[3] for r in results])
                        self.results.append([self.class1name,
                                              self.class2name,
                                              self.tierWidget.displayValue(),
                                              'COL-AVG',
                                              seg1_freq_sum,
                                              seg2_freq_sum,
                                              sum([seg1_freq_sum, seg2_freq_sum]),
                                              h_avg,
                                              self.typeTokenWidget.value()])


class SegmentClassSelector(EnvironmentDialog):

    def __init__(self, parent, corpus):
        parent.name = 'class'
        super().__init__(corpus, parent)
        self.lhsEnvFrame.setTitle('First class')
        self.rhsEnvFrame.setTitle('Second class')
        self.anotherButton.hide()
        self.corpus = corpus

    def accept(self):

        lhs = self.lhs.value()
        rhs = self.rhs.value()
        if not (lhs and rhs):
            reply = QMessageBox.critical(self,
                                         "Missing information", "Please specify two segment classes")
            return

        self.class1features = lhs[1:-1].split(',')
        self.class2features = rhs[1:-1].split(',')
        class1segs = list()
        class2segs = list()
        for seg in self.corpus.inventory:
            if all(seg.features[feature[1:]]==feature[0] for feature in self.class1features):
               class1segs.append(seg.symbol)
            if all(seg.features[feature[1:]]==feature[0] for feature in self.class2features):
               class2segs.append(seg.symbol)

        self.pairs = itertools.product(class1segs, class2segs)
        self.pairs = [p for p in self.pairs if not p[0]==p[1]]

        QDialog.accept(self)
