
import csv
from corpustools.config import TMP_DIR

from .imports import *

from .models import VariantModel, ResultsModel
from .windows import FunctionWorker

class AudioWorker(FunctionWorker):
    def run(self):
        #if not QSound.isAvailable():
        #    print('uh oh')
        for p in self.kwargs['files']:
            print(p)
            s = QSound(p)
            print(s.loops())
            s.play()
            while s.loopsRemaining():
                print(s.loopsRemaining())
                if self.stopped:
                    break
            if self.stopped:
                s.stop()
                break


class TableWidget(QTableView):
    def __init__(self,parent=None):
        super(TableWidget, self).__init__(parent=parent)

        self.verticalHeader().hide()

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        #self.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.customContextMenuRequested.connect(self.popup)
        #header = self.horizontalHeader()
        #header.setContextMenuPolicy(Qt.CustomContextMenu)
        #header.customContextMenuRequested.connect( self.showHeaderMenu )
        self.horizontalHeader().setMinimumSectionSize(70)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.setSortingEnabled(True)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

    def setModel(self,model):
        super(TableWidget, self).setModel(model)
        #self.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        #try:
        #    self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #except AttributeError:
        #    self.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.model().columnsRemoved.connect(self.horizontalHeader().resizeSections)

    def calcWidth(self):
        header = self.horizontalHeader()
        width = self.horizontalOffset()
        for i in range(header.count()):
            width += header.sectionSize(i)
        return width

class LexiconView(QWidget):
    selectTokens = Signal(object)
    wordsChanged = Signal()
    wordToBeEdited = Signal(object, object)
    def __init__(self,parent=None):
        super(LexiconView, self).__init__(parent=parent)
        self._parent = parent
        self.setStyleSheet( """ TableWidget::item:selected:active {
                                     background: lightblue;
                                }
                                TableWidget::item:selected:!active {
                                     background: lightblue;
                                }
                                TableWidget::item:selected:disabled {
                                     background: lightblue;
                                }
                                TableWidget::item:selected:!disabled {
                                     background: lightblue;
                                }
                                """
                                )

        self.table = TableWidget(self)
        layout = QVBoxLayout()
        self.searchField = QLineEdit()
        self.searchField.setPlaceholderText('Search...')
        self.searchField.returnPressed.connect(self.search)
        layout.addWidget(self.searchField, alignment = Qt.AlignRight)
        layout.addWidget(self.table)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.showMenu)

        header = self.table.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect( self.showHeaderMenu )

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding))

    def search(self):
        text = self.searchField.text()
        if not text:
            return
        model = self.table.model()
        curSelection = self.table.selectionModel().selectedRows()
        if curSelection:
            row = curSelection[-1].row() + 1
        else:
            row = 0
        start = model.index(row,0)
        matches = model.match(start, Qt.DisplayRole, text, 1, Qt.MatchContains)
        if matches:
            index = matches[0]
            self.table.selectionModel().select(index,
                    QItemSelectionModel.SelectCurrent|QItemSelectionModel.Rows)
            self.table.scrollTo(index,QAbstractItemView.PositionAtCenter)
        else:
            start = model.index(0,0)
            matches = model.match(start, Qt.DisplayRole, text, 1, Qt.MatchContains)
            if matches:
                index = matches[0]
                self.table.selectionModel().select(index,
                    QItemSelectionModel.SelectCurrent|QItemSelectionModel.Rows)
                self.table.scrollTo(index,QAbstractItemView.PositionAtCenter)
            else:
                self.table.selectionModel().clear()

    def highlightType(self,wordtype):
        if self.table.model() is None:
            return
        model = self.table.model()
        self.table.selectionModel().clear()
        for i,r in enumerate(model.rows):
            if model.corpus[r] == wordtype:
                index = model.index(i,0)
                break
        else:
            return
        self.table.selectionModel().select(index,
                    QItemSelectionModel.SelectCurrent|QItemSelectionModel.Rows)
        self.table.scrollTo(index,QAbstractItemView.PositionAtCenter)

    def setModel(self, model):
        self.table.setModel(model)
        try:
            self.table.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        except AttributeError:
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def showHeaderMenu(self, pos):
        header = self.table.horizontalHeader()
        column = header.logicalIndexAt(pos.x())

        if column < 3:
            return

        editAction = QAction(self)
        editAction.setText('Edit column details')
        editAction.triggered.connect(lambda: self.editColumn(self.table.indexAt(pos)))

        removeAction = QAction(self)
        removeAction.setText('Remove column')
        removeAction.triggered.connect(lambda: self.removeColumn(self.table.indexAt(pos)))

        menu = QMenu(self)
        menu.addAction(editAction)
        menu.addAction(removeAction)

        menu.popup(header.mapToGlobal(pos))

    def editColumn(self, index):
        print(index.column())
        pass

    def removeColumn(self, index):
        print(index)
        pass

    def showMenu(self, pos):
        menu = QMenu()

        neighbourAction = QAction(self)
        neighbourAction.setText('List neighbours')
        #menu.addAction(neighbourAction)

        editWordAction = QAction(self)
        editWordAction.setText('Edit word details')
        editWordAction.triggered.connect(lambda: self.editWord(self.table.indexAt(pos)))
        menu.addAction(editWordAction)

        hideAction = QAction(self)
        nonlexhidden = self.table.model().nonLexHidden
        if nonlexhidden:
            hideAction.setText('Show non-transcribed items')
        else:
            hideAction.setText('Hide non-transcribed items')
        hideAction.triggered.connect(lambda: self.hideNonLexical(not nonlexhidden))
        menu.addAction(hideAction)

        variantsAction = QAction(self)
        variantsAction.setText('List pronunciation variants')
        variantsAction.triggered.connect(lambda: self.showVariants(self.table.indexAt(pos)))
        menu.addAction(variantsAction)

        findTokensAction = QAction(self)
        findTokensAction.setText('Find all tokens')
        findTokensAction.triggered.connect(lambda: self.findTokens(self.table.indexAt(pos)))
        menu.addAction(findTokensAction)

        menu.addSeparator()

        removeWordAction = QAction(self)
        removeWordAction.setText('Remove word')
        removeWordAction.triggered.connect(lambda: self.removeWord(self.table.indexAt(pos)))
        menu.addAction(removeWordAction)
        action = menu.exec_(self.table.viewport().mapToGlobal(pos))

    def editWord(self, index):
        word = self.table.model().wordObject(index.row())
        self.wordToBeEdited.emit(index.row(), word)

    def removeWord(self,index):
        word_key = self.table.model().rows[index.row()]

        msgBox = QMessageBox(QMessageBox.Warning, "Remove word",
                "Are you sure you want to remove '{}'?".format(str(self.table.model().corpus[word_key])), QMessageBox.NoButton, self)
        msgBox.addButton("Continue", QMessageBox.AcceptRole)
        msgBox.addButton("Abort", QMessageBox.RejectRole)
        if msgBox.exec_() != QMessageBox.AcceptRole:
            return
        self.table.model().removeWord(word_key)
        self.wordsChanged.emit()

    def hideNonLexical(self,b):
        self.table.model().hideNonLexical(b)

    def findTokens(self, index):
        tokens = self.table.model().wordObject(index.row()).wordtokens
        self.selectTokens.emit(tokens)

    def showVariants(self, index):
        variantDialog = QDialog()
        variantDialog.setWindowTitle('Pronunciation variants')
        layout = QVBoxLayout()
        table = TableWidget()
        layout.addWidget(table)
        table.setModel(VariantModel(self.table.model().wordObject(index.row()).wordtokens))
        variantDialog.setLayout(layout)
        variantDialog.exec_()


class TextView(QAbstractItemView):
    ExtraHeight = 3
    ExtraWidth = 15
    resizeCompleted = Signal()
    def __init__(self, parent=None):
        self.idealHeight = 0
        self.idealWidth = 0
        QAbstractItemView.__init__(self, parent)

        self.hashIsDirty = False
        self.rectForRow = dict()

        self.horizontalScrollBar().setRange(0,0)
        self.verticalScrollBar().setRange(0,0)
        self._resize_timer = None
        self.resizeCompleted.connect(self.handleResizeCompleted)

    def updateResizeTimer(self, interval=None):
        if self._resize_timer is not None:
            self.killTimer(self._resize_timer)
        if interval is not None:
            self._resize_timer = self.startTimer(interval)
        else:
            self._resize_timer = None

    def resizeEvent(self, event):
        self.updateResizeTimer(300)

    def timerEvent(self, event):
        if event.timerId() == self._resize_timer:
            self.updateResizeTimer()
            self.resizeCompleted.emit()

    def handleResizeCompleted(self):
        self.hashIsDirty = True
        self.calculateRectsIfNecessary()
        self.updateGeometries()

    def setModel(self,model):
        QAbstractItemView.setModel(self, model)
        self.hashIsDirty = True
        self.setItemDelegate(QStyledItemDelegate())

    def edit(self, index, trigger, event):
        if trigger == QAbstractItemView.DoubleClicked:
            return False
        return QAbstractItemView.edit(self, index, trigger, event)

    def calculateRectsIfNecessary(self):
        if not self.hashIsDirty:
            return
        if self.model() is None:
            return
        fm = QFontMetrics(self.font())
        rowHeight = fm.height() + self.ExtraHeight
        maxWidth = self.viewport().width()
        minimumWidth = 0
        x = 0
        y = 0
        for row in range(self.model().rowCount(self.rootIndex())):
            index = self.model().index(row, 0, self.rootIndex())
            text = self.model().data(index,Qt.DisplayRole)
            textWidth = fm.width(text)
            if not (x == 0 or x+textWidth+self.ExtraWidth < maxWidth):
                y += rowHeight
                x = 0
            elif x != 0:
                x += self.ExtraWidth
            self.rectForRow[row] = QRectF(x, y, textWidth + self.ExtraWidth, rowHeight)
            if textWidth > minimumWidth:
                minimumWidth = textWidth
            x += textWidth
        self.idealWidth = minimumWidth + self.ExtraWidth
        self.idealHeight = y + rowHeight
        self.hashIsDirty = False
        self.viewport().update()

    def visualRect(self,index):
        if index.isValid():
            rect = self.viewportRectForRow(index.row()).toRect()
            return rect

    def viewportRectForRow(self, row):
        self.calculateRectsIfNecessary()
        rect = self.rectForRow[row].toRect()
        if not rect.isValid():
            return rect
        return QRectF(rect.x() - self.horizontalScrollBar().value(),
                    rect.y() - self.verticalScrollBar().value(),
                    rect.width(), rect.height())

    def isIndexHidden(self, index):
        return False

    def horizontalOffset(self):
        return self.horizontalScrollBar().value()

    def verticalOffset(self):
        return self.verticalScrollBar().value()

    def scrollTo(self, index, ScrollHint):
        area = self.viewport().rect()
        rect = self.visualRect(index)

        if rect.left() < area.left():
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + rect.left() - area.left())
        elif rect.right() > area.right():
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + min(
                    rect.right() - area.right(), rect.left() - area.left()))

        if rect.top() < area.top():
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + rect.top() - area.top())
        elif rect.bottom() > area.bottom():
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + min(
                    rect.bottom() - area.bottom(), rect.top() - area.top()))
        self.viewport().update()

    def indexAt(self, point):
        prx = point.x() + self.horizontalScrollBar().value()
        pry = point.y() + self.verticalScrollBar().value()

        self.calculateRectsIfNecessary()
        for k,v in self.rectForRow.items():
            if v.contains(point):
                return self.model().index(k,0, self.rootIndex())
        return QModelIndex()

    def dataChanged(self, topLeft, bottomRight, roles):
        self.hashIsDirty = True
        QAbstractItemView.dataChanged(self, topLeft, bottomRight, roles)

    def rowsInserted(self, parent, start, end):
        self.hashIsDirty = True
        QAbstractItemView.rowsInserted(self, parent, start, end)

    def rowsAboutToBeRemoved(self, parent, start, end):
        self.hashIsDirty = True
        QAbstractItemView.rowsAboutToBeRemoved(self, parent, start, end)

    def moveCursor(self, cursorAction, modifiers):
        index = self.currentIndex()
        if ((cursorAction == QAbstractItemView.MoveLeft and index.row() > 0) or
            cursorAction == QAbstractItemView.MoveRight and index.row() + 1 < self.model().rowCount()):
            if cursorAction == QAbstractItemView.MoveLeft:
                offset = -1
            else:
                offset = 1
            index = model().index(index.row() + offset, index.column(), index.parent())
        elif ((cursorAction == QAbstractItemView.MoveUp and index.row() > 0) or
            cursorAction == QAbstractItemView.MoveDown and index.row() + 1 < self.model().rowCount()):
            fm = QFontMetrics(self.font())
            if cursorAction == QAbstractItemView.MoveUp:
                offset = -1
            else:
                offset = 1
            rowHeight = (fm.height() + self.ExtraHeight) * offset
            rect = self.viewportRectForRow(index.row()).toRect()
            point = QPoint(rect.center().x(), rect.center().y() + rowHeight)
            while point.x() >= 0:
                index = self.indexAt(point)
                if index.isValid():
                    break
                point.setX(point.x() - fm.width('n'))
        return index

    def scrollContentsBy(self, dx, dy):
        self.scrollDirtyRegion(dx, dy)
        self.viewport().scroll(dx, dy)

    def setSelection(self, rect, flags):
        rectangle = QRectF(rect.translated(self.horizontalScrollBar().value(),
                self.verticalScrollBar().value()).normalized())
        self.calculateRectsIfNecessary()
        firstRow = self.model().rowCount()
        lastRow = -1
        for k,v in self.rectForRow.items():
            if v.intersects(rectangle):
                if not (firstRow < k):
                    firstRow = k
                if not (lastRow > k):
                    lastRow = k
        if firstRow != self.model().rowCount() and lastRow != -1:
            selection = QItemSelection(self.model().index(firstRow,0,self.rootIndex()),
                            self.model().index(lastRow, 0, self.rootIndex()))
            self.selectionModel().select(selection, flags)
        else:
            invalid = QModelIndex()
            selection = QItemSelection(invalid, invalid)
            self.selectionModel().select(selection, flags)

        self.update()

    def visualRegionForSelection(self, selection):
        region = QRegion()

        for span in selection:
            for row in range(span.top(), span.bottom() + 1):
                for col in range(span.left(), span.right() + 1):
                    index = self.model().index(row, col, self.rootIndex())
                    region += self.visualRect(index)

        return region

    def paintEvent(self,event):
        if self.model() is None:
            return
        painter = QPainter(self.viewport())
        painter.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        for row in range(self.model().rowCount(self.rootIndex())):
            index = self.model().index(row, 0, self.rootIndex())
            rect = self.viewportRectForRow(row)
            if not rect.isValid() or rect.bottom() < 0 or\
                    rect.y() > self.viewport().height():
                continue
            option = self.viewOptions()
            option.rect = rect.toRect()
            if self.selectionModel().isSelected(index):
                option.state |= QStyle.State_Selected
            if self.currentIndex() == index:
                option.state |= QStyle.State_HasFocus
            self.itemDelegate().paint(painter, option, index)
            self.paintOutline(painter,rect)

    def paintOutline(self, painter, rectangle):
        rect = rectangle.adjusted(0,0,-1,-1)
        painter.save()
        painter.setPen(QPen(self.palette().dark().color(), 0.5))
        painter.drawRect(rect)
        painter.setPen(QPen(Qt.black,0.5))
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        painter.drawLine(rect.bottomRight(), rect.topRight())
        painter.restore()

    def updateGeometries(self):
        fm = QFontMetrics(self.font())
        rowHeight = fm.height() + self.ExtraHeight
        self.horizontalScrollBar().setSingleStep(fm.width('n'))
        self.horizontalScrollBar().setPageStep(self.viewport().width())
        self.horizontalScrollBar().setRange(0, max(0, self.idealWidth - self.viewport().width()))

        self.verticalScrollBar().setSingleStep(rowHeight)
        self.verticalScrollBar().setPageStep(self.viewport().height())
        self.verticalScrollBar().setRange(0, max(0,self.idealHeight - self.viewport().height()))

    def mousePressEvent(self, event):
        QAbstractItemView.mousePressEvent(self, event)
        #self.setCurrentIndex(self.indexAt(event.pos()))

class DiscourseView(QWidget):
    selectType = Signal(object)
    def __init__(self,parent=None):
        super(DiscourseView, self).__init__(parent=parent)
        self.audioThread = AudioWorker()
        self.setupActions()
        self.audioThread.finished.connect(self.audioFinished)

        self.text = TextView(self)
        self.text.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text.customContextMenuRequested.connect(self.showMenu)
        self.table = TableWidget(self)
        self.table.setSortingEnabled(False)
        try:
            self.table.horizontalHeader().setSectionsClickable(False)
        except AttributeError:
            self.table.horizontalHeader().setClickable(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.showMenu)
        self.table.hide()
        self.setStyleSheet( """ TextView::item:selected:active {
                                     background: lightblue;
                                }
                                TextView::item:selected:!active {
                                     background: lightblue;
                                }
                                TextView::item:selected:disabled {
                                     background: lightblue;
                                }
                                TextView::item:selected:!disabled {
                                     background: lightblue;
                                }
                                TableWidget::item:selected:active {
                                     background: lightblue;
                                }
                                TableWidget::item:selected:!active {
                                     background: lightblue;
                                }
                                TableWidget::item:selected:disabled {
                                     background: lightblue;
                                }
                                TableWidget::item:selected:!disabled {
                                     background: lightblue;
                                }
                                """
                                )

        layout = QVBoxLayout()
        self.searchField = QLineEdit()
        self.searchField.setPlaceholderText('Search...')
        self.searchField.returnPressed.connect(self.search)
        layout.addWidget(self.searchField, alignment = Qt.AlignRight)
        layout.addWidget(self.text)
        layout.addWidget(self.table)

        self.playbar = QToolBar()

        self.playbar.addAction(self.playStopAction)
        self.playbar.hide()
        layout.addWidget(self.playbar, alignment=Qt.AlignHCenter)

        self.setLayout(layout)

    def setModel(self,model):
        self.text.setModel(model)
        self.table.setModel(model)
        self.table.setSelectionModel(self.text.selectionModel())
        if False and AUDIO_ENABLED and model.hasAudio():
            self.playbar.show()
        else:
            self.playbar.hide()
        try:
            self.table.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        except AttributeError:
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def search(self):
        text = self.searchField.text()
        if not text:
            return
        model = self.text.model()
        curSelection = self.text.selectionModel().selectedRows()
        if curSelection:
            row = curSelection[-1].row() + 1
        else:
            row = 0
        start = model.index(row,0)
        matches = model.match(start, Qt.DisplayRole, text, 1, Qt.MatchContains)
        if matches:
            index = matches[0]
            self.text.selectionModel().select(index,
                    QItemSelectionModel.SelectCurrent)
            self.text.scrollTo(index,QAbstractItemView.PositionAtCenter)
        else:
            start = model.index(0,0)
            matches = model.match(start, Qt.DisplayRole, text, 1, Qt.MatchContains)
            if matches:
                index = matches[0]
                self.text.selectionModel().select(index,
                    QItemSelectionModel.SelectCurrent)
                self.text.scrollTo(index,QAbstractItemView.PositionAtCenter)
            else:
                self.text.selectionModel().clear()

    def findType(self, index):
        wordtype = self.text.model().wordTokenObject(index.row()).wordtype
        self.selectType.emit(wordtype)

    def changeView(self):
        if self.text.isHidden():
            self.text.show()
            self.table.hide()
        else:
            self.text.hide()
            self.table.show()

    def showMenu(self, pos):
        menu = QMenu()
        index = self.text.indexAt(pos)
        changeViewAction = QAction(self)
        if self.text.isHidden():
            changeViewAction.setText('Show as text')
        else:
            changeViewAction.setText('Show as table')
        changeViewAction.triggered.connect(self.changeView)
        menu.addAction(changeViewAction)
        if index.isValid():
            lookupAction = QAction(self)
            lookupAction.setText('Look up word')
            lookupAction.triggered.connect(lambda: self.findType(self.text.indexAt(pos)))
            menu.addAction(lookupAction)
        action = menu.exec_(self.text.viewport().mapToGlobal(pos))

    def playStopAudio(self):
        print('triggered')
        if self.audioThread.isRunning():
            self.audioThread.stop()
            self.playStopAction.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.playStopAction.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
            rows = [x.row() for x in self.text.selectionModel().selectedRows()]
            times = self.text.model().rowsToTimes(rows)
            filenames = self.text.model().discourse.extract_tokens(times,TMP_DIR)
            #QSound.play(filenames[0])
            print('params')
            self.audioThread.setParams({'files':filenames})

            print('start thread')
            self.audioThread.start()
            #for f in filenames:
            #    s = QSound(f)
            #    s.loopsRemaining()

    def audioFinished(self):
        self.playStopAction.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def highlightTokens(self, tokens):
        if self.text.model() is None:
            return
        self.text.selectionModel().clear()
        times = [x.begin for x in tokens if x.discourse == self.text.model().corpus]
        rows = self.text.model().timesToRows(times)
        for r in rows:
            index = self.text.model().index(r,0)
            self.text.selectionModel().select(index, QItemSelectionModel.Select |QItemSelectionModel.Rows)

    def setupActions(self):
        self.playStopAction = QAction(self.style().standardIcon(QStyle.SP_MediaPlay), self.tr("Play"), self)
        self.playStopAction.setShortcut(Qt.NoModifier + Qt.Key_Space)
        self.playStopAction.setDisabled(False)
        self.playStopAction.triggered.connect(self.playStopAudio)

class SubTreeView(QTreeView):
    def __init__(self,parent=None):
        super(SubTreeView, self).__init__(parent=parent)
        self.setExpandsOnDoubleClick(True)

    def edit(self, index, trigger, event):
        if trigger == QAbstractItemView.DoubleClicked:
            return False
        return QTreeView.edit(self, index, trigger, event)


class TreeWidget(SubTreeView):
    newLexicon = Signal(object)
    def __init__(self,parent=None):
        super(TreeWidget, self).__init__(parent=parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)
        self.setColumnWidth(0,40)
        self._selection_model = None

    def setModel(self, model):
        QTreeView.setModel(self, model)
        self._selection_model = QTreeView.selectionModel(self)

    def selectionModel(self):
        return self._selection_model

    def showMenu(self, pos):
        menu = QMenu()

        buildAction = QAction(self)
        buildAction.setText('Build lexicon')
        buildAction.triggered.connect(lambda: self.buildNewLexicon(self.indexAt(pos)))
        menu.addAction(buildAction)
        combineAction = QAction(self)
        combineAction.setText('Combine sub dialogs')
        menu.addAction(combineAction)
        action = menu.exec_(self.viewport().mapToGlobal(pos))

    def buildNewLexicon(self, index):
        lexicon = self.model().createLexicon(index)
        self.newLexicon.emit(lexicon)

class ResultsWindow(QDialog):
    def __init__(self, title, dialog, parent):
        QDialog.__init__(self,parent = parent)
        self.dialog = dialog
        dataModel = ResultsModel(self.dialog.header,self.dialog.results, self.parent().settings)
        layout = QVBoxLayout()
        self.table = TableWidget()
        self.table.setModel(dataModel)
        try:
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        except AttributeError:
            self.table.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.table)
        self.aclayout = QHBoxLayout()
        self.redoButton = QPushButton('Reopen function dialog')
        self.redoButton.clicked.connect(self.redo)
        self.saveButton = QPushButton('Save to file')
        self.saveButton.clicked.connect(self.save)
        self.aclayout.addWidget(self.redoButton)
        self.aclayout.addWidget(self.saveButton)
        acframe = QFrame()
        acframe.setLayout(self.aclayout)
        layout.addWidget(acframe)
        self.setLayout(layout)
        #self.setWidget(frame)
        self.table.resizeColumnsToContents()
        self.setWindowTitle(title)
        self.table.adjustSize()
        self.setMaximumWidth(self.table.calcWidth()+41)
        self.resize(self.maximumWidth(),400)

    def redo(self):
        if self.dialog.exec_():
            if self.dialog.update:
                self.table.model().addRows(self.dialog.results)
            else:
                dataModel = ResultsModel(self.dialog.header,self.dialog.results, self.parent().settings)
                self.table.setModel(dataModel)
        self.raise_()
        self.activateWindow()

    def save(self):
        filename = QFileDialog.getSaveFileName(self,'Choose save file',
                        filter = 'Text files (*.txt *.csv)')

        if filename and filename[0]:
            with open(filename[0], mode='w', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(self.table.model().columns)
                for row in self.table.model().rows:
                    writer.writerow(row)

class PhonoSearchResults(ResultsWindow):
    def __init__(self, title, dataModel, parent=None):
        ResultsWindow.__init__(self, title, dataModel, parent)
        self.summarized = True
        self.summaryButton = QPushButton('Show individual results')
        self.summaryButton.clicked.connect(self.summaryDetail)
        self.aclayout.addWidget(self.summaryButton)

    def summaryDetail(self):
        if self.summarized:
            self.table.model().setSummarized(True)
            self.summaryButton.setText('Show individual results')
        else:
            self.table.model().setSummarized(False)
            self.summaryButton.setText('Show summary results')
        self.summarized = not self.summarized