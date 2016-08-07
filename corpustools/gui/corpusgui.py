from .imports import *
from corpustools.contextmanagers import CanonicalVariantContext

from corpustools.corpus.classes import Word, Attribute

from .widgets import (RadioSelectWidget, SegmentSelectionWidget,
                    InventoryBox,
                    CreateClassWidget, TranscriptionWidget, TierWidget)
from .featuregui import FeatureSystemSelect
from .helpgui import HelpDialog

class InventorySummary(QWidget):
    def __init__(self, corpus, inventory, parent=None):
        QWidget.__init__(self,parent)

        self.type_context = CanonicalVariantContext(corpus, 'transcription', 'type')
        self.token_context = CanonicalVariantContext(corpus, 'transcription', 'token')

        layout = QHBoxLayout()

        layout.setAlignment(Qt.AlignTop)

        self.segments = InventoryBox('Segments',inventory)
        self.segments.setExclusive(True)
        for b in self.segments.btnGroup.buttons():
            b.clicked.connect(self.summarizeSegment)

        layout.addWidget(self.segments)

        self.detailFrame = QFrame()

        layout.addWidget(self.detailFrame)

        self.setLayout(layout)

    def summarizeSegment(self):
        self.detailFrame.deleteLater()
        seg = self.sender().text()

        self.detailFrame = QGroupBox('Segment details')

        layout = QFormLayout()
        layout.setAlignment(Qt.AlignTop)
        with self.type_context as c:
            freq_base = c.get_frequency_base(gramsize = 1,
                            probability = False)

            probs = c.get_frequency_base(gramsize = 1,
                        probability = True)

        layout.addRow(QLabel('Type frequency:'),
                            QLabel('{:,.1f} ({:.2%})'.format(
                                                freq_base[seg], probs[seg]
                                                )
                            ))

        with self.token_context as c:
            freq_base = c.get_frequency_base(gramsize = 1,
                            probability = False)

            probs = c.get_frequency_base(gramsize = 1,
                            probability = True)

        layout.addRow(QLabel('Token frequency:'),
                            QLabel('{:,.1f} ({:.2%})'.format(
                                                    freq_base[seg], probs[seg]
                                                    )
                            ))

        self.detailFrame.setLayout(layout)

        self.layout().addWidget(self.detailFrame, alignment = Qt.AlignTop)


class AttributeSummary(QWidget):
    def __init__(self, corpus, parent=None):
        QWidget.__init__(self,parent)

        self.corpus = corpus

        layout = QFormLayout()

        self.columnSelect = QComboBox()
        self.corpus_attributes = [x for x in self.corpus.attributes]# if not x.name in ('transcription', 'spelling')]
        #'transcription' and 'spelling' are special attributes that are actual methods decorated with @property
        #including them here results in duplications
        for a in self.corpus_attributes:
            self.columnSelect.addItem(str(a))
        self.columnSelect.currentIndexChanged.connect(self.summarizeColumn)

        layout.addRow(QLabel('Column'),self.columnSelect)

        self.detailFrame = QFrame()

        layout.addRow(self.detailFrame)

        self.setLayout(layout)

        self.summarizeColumn()

    def summarizeColumn(self):
        for a in self.corpus_attributes:
            if str(a) == self.columnSelect.currentText():
                self.detailFrame.deleteLater()
                self.detailFrame = QFrame()
                layout = QFormLayout()
                layout.addRow(QLabel('Type:'), QLabel(a.att_type.title()))
                if a.att_type == 'numeric':
                    l = QLabel('{0[0]:,}-{0[1]:,}'.format(a.range))
                    layout.addRow(QLabel('Range:'), l)

                elif a.att_type == 'factor':
                    if len(a.range) > 300:
                        l = QLabel('Too many levels to display')
                    else:
                        l = QLabel(', '.join(sorted(a.range)))
                    l.setWordWrap(True)
                    layout.addRow(QLabel('Factor levels:'), l)

                elif a.att_type == 'tier':
                    if a.name == 'transcription':
                        layout.addRow(QLabel('Included segments:'), QLabel('All'))
                    else:
                        l = QLabel(', '.join(a.range))
                        l.setWordWrap(True)
                        layout.addRow(QLabel('Included segments:'), l)
                self.detailFrame.setLayout(layout)
                self.layout().addRow(self.detailFrame)


class CorpusSummary(QDialog):
    def __init__(self, parent, corpus, inventory):
        QDialog.__init__(self,parent)


        if hasattr(corpus,'lexicon'):
            c = corpus.lexicon

            if hasattr(corpus,'discourses'):
                speech_corpus = True
            else:
                speech_corpus = False
        else:
            c = corpus

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        #layout.setSizeConstraint(QLayout.SetFixedSize)

        main = QFormLayout()

        main.addRow(QLabel('Corpus:'),QLabel(corpus.name))

        detailTabs = QTabWidget()
        if c.specifier is not None:
            main.addRow(QLabel('Feature system:'),QLabel(c.specifier.name))
            self.inventorySummary = InventorySummary(corpus, inventory)
            detailTabs.addTab(self.inventorySummary, 'Inventory')
        else:
            main.addRow(QLabel('Feature system:'),QLabel('None'))

        main.addRow(QLabel('Number of words types:'),QLabel(str(len(c))))

        self.attributeSummary = AttributeSummary(c)

        detailTabs.addTab(self.attributeSummary,'Columns')
        detailTabs.currentChanged.connect(self.hideWidgets)

        main.addRow(detailTabs)

        mainFrame = QFrame()
        mainFrame.setLayout(main)

        layout.addWidget(mainFrame, alignment = Qt.AlignCenter)

        self.doneButton = QPushButton('Done')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.doneButton)
        self.doneButton.clicked.connect(self.accept)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)
        self.setWindowTitle('Corpus summary')

    def hideWidgets(self,index):
        return
        if index == 0:
            self.inventorySummary.hide()
            self.attributeSummary.hide()
        elif index == 1:
            self.inventorySummary.hide()
            self.attributeSummary.show()
        self.adjustSize()



class AddWordDialog(QDialog):
    def __init__(self, parent, corpus, inventory, word = None):
        QDialog.__init__(self,parent)
        self.corpus = corpus
        self.inventory = inventory
        layout = QVBoxLayout()
        layout.setSizeConstraint(QLayout.SetFixedSize)

        main = QFormLayout()

        self.edits = {}

        for a in self.corpus.attributes:
            if a.att_type == 'tier' and a.name == 'transcription':
                if not self.corpus.has_transcription:
                    pass
                else:
                    self.edits[a.name] = TranscriptionWidget('Transcription', corpus, inventory)
                    self.edits[a.name].transcriptionChanged.connect(self.updateTiers)
                    main.addRow(self.edits[a.name])
            elif a.att_type == 'tier':
                self.edits[a.name] = QLabel('Empty')
                main.addRow(QLabel(str(a)),self.edits[a.name])
            elif a.att_type == 'spelling':
                self.edits[a.name] = QLineEdit()
                main.addRow(QLabel(str(a)),self.edits[a.name])
            elif a.att_type == 'numeric':
                self.edits[a.name] = QLineEdit()
                self.edits[a.name].setText('0')
                main.addRow(QLabel(str(a)),self.edits[a.name])
            elif a.att_type == 'factor':
                self.edits[a.name] = QLineEdit()
                main.addRow(QLabel(str(a)),self.edits[a.name])
            else:
                print(a.name)
                print(str(a))
            if word is not None:
                if a.name == 'transcription' and not self.corpus.has_transcription:
                    pass
                else:
                    self.edits[a.name].setText(str(getattr(word,a.name)))

        mainFrame = QFrame()
        mainFrame.setLayout(main)

        layout.addWidget(mainFrame)
        if word is None:
            self.createButton = QPushButton('Create word')
            self.setWindowTitle('Create word')
        else:
            self.createButton = QPushButton('Save word changes')
            self.setWindowTitle('Edit word')
        self.createButton.setAutoDefault(True)
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.createButton)
        acLayout.addWidget(self.cancelButton)
        self.createButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

    def updateTiers(self, new_transcription):
        transcription = new_transcription.split('.')
        for a in self.corpus.attributes:
            if a.att_type != 'tier':
                continue
            if a.name == 'transcription':
                continue
            if a.name not in self.edits:
                continue
            text = '.'.join([x for x in transcription if x in a.range])
            if text == '':
                text = 'Empty'
            self.edits[a.name].setText(text)

    def accept(self):

        kwargs = {}

        for a in self.corpus.attributes:
            if a.att_type == 'tier':
                text = self.edits[a.name].text()
                if text == 'Empty':
                    text = ''
                kwargs[a.name] = [x for x in text.split('.') if x != '']
                #if not kwargs[a.name]:
                #    reply = QMessageBox.critical(self,
                #            "Missing information", "Words must have a Transcription.".format(str(a)))
                #    return

                for i in kwargs[a.name]:
                    if i not in self.inventory.segs:
                        reply = QMessageBox.critical(self,
                            "Invalid information", "The column '{}' must contain only symbols in the corpus' inventory.".format(str(a)))
                        return
            elif a.att_type == 'spelling':
                kwargs[a.name] = self.edits[a.name].text()
                if kwargs[a.name] == '' and a.name == 'spelling':
                    kwargs[a.name] = None
                #if not kwargs[a.name] and a.name == 'spelling':
                #    reply = QMessageBox.critical(self,
                #            "Missing information", "Words must have a spelling.".format(str(a)))
                #    return
            elif a.att_type == 'numeric':
                try:
                    kwargs[a.name] = float(self.edits[a.name].text())
                except ValueError:
                    reply = QMessageBox.critical(self,
                            "Invalid information", "The column '{}' must be a number.".format(str(a)))
                    return

            elif a.att_type == 'factor':
                kwargs[a.name] = self.edits[a.name].text()
        self.word = Word(**kwargs)
        QDialog.accept(self)

class AddTierDialog(CreateClassWidget):
    def __init__(self, parent, corpus, inventory, class_type='tier'):
        CreateClassWidget.__init__(self, parent, corpus, inventory, class_type)

    def accept(self):
        tierName = self.nameEdit.text()
        self.attribute = Attribute(tierName.lower().replace(' ',''),'tier',tierName)
        if tierName == '':
            reply = QMessageBox.critical(self,
                                         "Missing information", "Please enter a name for the tier.")
            return
        elif self.attribute.name in self.corpus.basic_attributes:
            reply = QMessageBox.critical(self,
                                         "Invalid information",
                                         "The name '{}' overlaps with a protected column.".format(tierName))
            return
        elif self.attribute in self.corpus.attributes:

            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate tiers",
                                 "'{}' is already the name of a tier.  Overwrite?".format(tierName),
                                 QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return
        #createType = self.createType.currentText()
        #createList = self.createWidget.value()
        inClass, notInClass = self.generateClass()
        if not inClass:
            reply = QMessageBox.critical(self,
                                         "Missing information",
                                         "Please specify at least one segment or one feature value")
        self.segList = inClass
        QDialog.accept(self)

class AddCountColumnDialog(QDialog):
    def __init__(self, parent, corpus, inventory):
        QDialog.__init__(self,parent)
        self.corpus = corpus

        layout = QVBoxLayout()

        main = QFormLayout()

        self.nameWidget = QLineEdit()

        main.addRow('Name of column',self.nameWidget)

        self.tierWidget = TierWidget(self.corpus)

        main.addRow('Tier to count on',self.tierWidget)

        self.segmentSelect = SegmentSelectionWidget(inventory)

        main.addRow(self.segmentSelect)


        mainFrame = QFrame()
        mainFrame.setLayout(main)

        layout.addWidget(mainFrame)

        self.createButton = QPushButton('Add count column')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.createButton)
        acLayout.addWidget(self.cancelButton)
        self.createButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Add count column')

    def accept(self):
        name = self.nameWidget.text()
        self.attribute = Attribute(name.lower().replace(' ',''),'numeric',name)
        if name == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please enter a name for the tier.")
            return
        elif self.attribute.name in self.corpus.basic_attributes:
            reply = QMessageBox.critical(self,
                    "Invalid information", "The name '{}' overlaps with a protected column.".format(name))
            return
        elif self.attribute in self.corpus.attributes:

            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate tiers",
                    "'{}' is already the name of a tier.  Overwrite?".format(name), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return

        self.sequenceType = self.tierWidget.value()

        self.segList = self.segmentSelect.value()

        QDialog.accept(self)


class AddColumnDialog(QDialog):
    def __init__(self, parent, corpus, attribute = None):
        QDialog.__init__(self,parent)
        self.corpus = corpus

        layout = QVBoxLayout()

        main = QFormLayout()

        self.nameWidget = QLineEdit()

        main.addRow('Name of column',self.nameWidget)

        self.typeWidget = QComboBox()
        for at in Attribute.ATT_TYPES:
            if at == 'tier':
                continue
            self.typeWidget.addItem(at.title())
        self.typeWidget.currentIndexChanged.connect(self.updateDefault)

        main.addRow('Type of column',self.typeWidget)

        self.defaultWidget = QLineEdit()

        main.addRow('Default value',self.defaultWidget)


        mainFrame = QFrame()
        mainFrame.setLayout(main)

        layout.addWidget(mainFrame)

        self.createButton = QPushButton('Add column')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.createButton)
        acLayout.addWidget(self.cancelButton)
        self.createButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Add column')

    def updateDefault(self):
        if self.typeWidget.currentText().lower() == 'numeric':
            self.defaultWidget.setText('0')
        else:
            self.defaultWidget.setText('')

    def accept(self):
        name = self.nameWidget.text()
        at = self.typeWidget.currentText().lower()
        dv = self.defaultWidget.text()
        self.attribute = Attribute(name.lower().replace(' ',''),at,name)
        if name == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please enter a name for the tier.")
            return
        elif self.attribute.name in self.corpus.basic_attributes:
            reply = QMessageBox.critical(self,
                    "Invalid information", "The name '{}' overlaps with a protected column.".format(name))
            return
        elif self.attribute in self.corpus.attributes:

            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate tiers",
                    "'{}' is already the name of a tier.  Overwrite?".format(name), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return
        if at == 'numeric':
            try:
                dv = float(dv)
            except ValueError:
                reply = QMessageBox.critical(self,
                        "Invalid information", "The default value for numeric columns must be a number")
                return
        self.attribute.default_value = dv
        QDialog.accept(self)


class AddAbstractTierDialog(QDialog):
    def __init__(self, parent, corpus, inventory):
        QDialog.__init__(self,parent)
        self.corpus = corpus
        self.inventory = inventory

        layout = QVBoxLayout()

        main = QFormLayout()

        self.cvradio = QRadioButton('CV skeleton')
        self.cvradio.click()
        main.addWidget(self.cvradio)

        mainFrame = QFrame()
        mainFrame.setLayout(main)

        layout.addWidget(mainFrame)

        self.createButton = QPushButton('Create tier')
        self.previewButton = QPushButton('Preview tier')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.createButton)
        acLayout.addWidget(self.previewButton)
        acLayout.addWidget(self.cancelButton)
        self.createButton.clicked.connect(self.accept)
        self.previewButton.clicked.connect(self.preview)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Create abstract tier')

    def generateSegList(self):
        consonants = [c.symbol for c in self.inventory.get_consonants()]
        vowels = [v.symbol for v in self.inventory.get_vowels()]
        # for seg in self.inventory:
        #     category = self.inventory.categorize(seg)
        #     if category is None:
        #         continue
        #     elif category[0] == 'Consonant':
        #         consonants.append(seg.symbol)
        #     else:
        #         vowels.append(seg.symbol)
        segList = {'C' : consonants,
                    'V' : vowels}
        return segList

    def preview(self):
        if self.cvradio.isChecked():
            segList = self.generateSegList()
        preview = "The following abstract symbols correspond to the following segments:\n"
        for k,v in segList.items():
            preview += '{}: {}\n'.format(k,', '.join(v))
        reply = QMessageBox.information(self,
                "Tier preview", preview)


    def accept(self):
        if self.cvradio.isChecked():
            tierName = 'CV skeleton'
            self.attribute = Attribute('cvskeleton','factor','CV skeleton')
            self.segList = self.generateSegList()

        if tierName == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please enter a name for the tier.")
            return
        if self.attribute.name in self.corpus.basic_attributes:
            reply = QMessageBox.critical(self,
                    "Invalid information", "The name '{}' overlaps with a protected column.".format(tierName))
            return
        elif self.attribute in self.corpus.attributes:

            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate tiers",
                    "'{}' is already the name of a tier.  Overwrite?".format(tierName), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return

        QDialog.accept(self)


class RemoveAttributeDialog(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

        self.tierSelect = QListWidget()
        self.tierSelect.setSelectionMode(QAbstractItemView.ExtendedSelection)
        for t in corpus.attributes:
            if t in corpus.basic_attributes:
                continue
            self.tierSelect.addItem(t.display_name)

        layout.addWidget(self.tierSelect)

        self.removeSelectedButton = QPushButton('Remove selected columns')
        self.removeAllButton = QPushButton('Remove all non-essential columns')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.removeSelectedButton)
        acLayout.addWidget(self.removeAllButton)
        acLayout.addWidget(self.cancelButton)
        self.removeSelectedButton.clicked.connect(self.removeSelected)
        self.removeAllButton.clicked.connect(self.removeAll)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Remove tier')

    def removeSelected(self):
        selected = self.tierSelect.selectedItems()
        if not selected:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a column to remove.")
            return
        self.tiers = [x.text() for x in selected]
        msgBox = QMessageBox(QMessageBox.Warning, "Remove columns",
                "This will permanently remove the columns: {}.  Are you sure?".format(', '.join(self.tiers)), QMessageBox.NoButton, self)
        msgBox.addButton("Remove", QMessageBox.AcceptRole)
        msgBox.addButton("Cancel", QMessageBox.RejectRole)
        if msgBox.exec_() != QMessageBox.AcceptRole:
            return

        QDialog.accept(self)

    def removeAll(self):
        if self.tierSelect.count() == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "There are no columns to remove.")
            return
        self.tiers = [self.tierSelect.item(i).text() for i in range(self.tierSelect.count())]
        msgBox = QMessageBox(QMessageBox.Warning, "Remove columns",
                "This will permanently remove the columns: {}.  Are you sure?".format(', '.join(self.tiers)), QMessageBox.NoButton, self)
        msgBox.addButton("Remove", QMessageBox.AcceptRole)
        msgBox.addButton("Cancel", QMessageBox.RejectRole)
        if msgBox.exec_() != QMessageBox.AcceptRole:
            return

        QDialog.accept(self)



