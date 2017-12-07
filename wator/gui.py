from PyQt5 import QtWidgets, QtGui, QtCore, QtSvg, uic
import numpy
from wator import WaTor
import time
import os.path


CELL_SIZE = 32

SVG_WATER = QtSvg.QSvgRenderer('wator/gui/water.svg')
SVG_FISH = QtSvg.QSvgRenderer('wator/gui/fish.svg')
SVG_SHARK = QtSvg.QSvgRenderer('wator/gui/shark.svg')

VALUE_ROLE = QtCore.Qt.UserRole

def pixels_to_logical(x, y):
    return y // CELL_SIZE, x // CELL_SIZE


def logical_to_pixels(row, column):
    return column * CELL_SIZE, row * CELL_SIZE


class GridWidget(QtWidgets.QWidget):
    def __init__(self, array, energy):
        super().__init__()  # musime zavolat konstruktor predka
        self.array = array
        self.energy = energy
        # nastavime velikost podle velikosti matice, jinak je nas widget prilis maly
        size = logical_to_pixels(*array.shape)
        self.setMinimumSize(*size)
        self.setMaximumSize(*size)
        self.resize(*size)

    def mousePressEvent(self, event):
        # prevedeme klik na souradnice matice
        row, column = pixels_to_logical(event.x(), event.y())

        # Pokud jsme v matici, aktualizujeme data
        if 0 <= row < self.array.shape[0] and 0 <= column < self.array.shape[1]:
            self.array[row, column] = self.selected
            if self.selected < 0:
               self.energy[row, column] = self.initEnergy

            # timto zajistime prekresleni widgetu v miste zmeny:
            # (pro Python 3.4 a nizsi volejte jen self.update() bez argumentu)
            self.update(*logical_to_pixels(row, column), CELL_SIZE, CELL_SIZE)

    # vzdycky, kdyz je treba neco prekreslit, kdyz je treba, reaguje na udalost
    # metoda, protoze nejde pouzit v connect(slot)
    def paintEvent(self, event):
        rect = event.rect()  # ziskame informace o prekreslovane oblasti

        # zjistime, jakou oblast nasi matice to predstavuje
        # nesmime se pritom dostat z matice ven
        row_min, col_min = pixels_to_logical(rect.left(), rect.top())
        row_min = max(row_min, 0)
        col_min = max(col_min, 0)
        row_max, col_max = pixels_to_logical(rect.right(), rect.bottom())
        row_max = min(row_max + 1, self.array.shape[0])
        col_max = min(col_max + 1, self.array.shape[1])

        painter = QtGui.QPainter(self)  # budeme kreslit

        for row in range(row_min, row_max):
            for column in range(col_min, col_max):
                # ziskame ctverecek, ktery budeme vybarvovat
                x, y = logical_to_pixels(row, column)
                rect = QtCore.QRectF(x, y, CELL_SIZE, CELL_SIZE)

                #BARVY
                # seda pro zdi, zelena pro travu
                #if self.array[row, column] < 0:
                #    color = QtGui.QColor(115, 115, 115)
                #else:
                #    color = QtGui.QColor(0, 255, 0)

                # OBRAZKY
                # podkladova barva pod polopruhledne obrazky
                white = QtGui.QColor(255, 255, 255)
                painter.fillRect(rect, QtGui.QBrush(white))

                # travu dame vsude, protoze i zdi stoji na trave
                SVG_WATER.render(painter, rect)

                # zdi dame jen tam, kam patri
                if self.array[row, column] > 0:
                    SVG_FISH.render(painter, rect)
                if self.array[row, column] < 0:
                    SVG_SHARK.render(painter, rect)

                # vyplnime ctverecek barvou
                #painter.fillRect(rect, QtGui.QBrush(color))

def new_dialog(window, grid):
    # Vytvorime novy dialog.
    # V dokumentaci maji dialogy jako argument `this`;
    # jde o "nadrazene" okno.
    dialog = QtWidgets.QDialog(window)

    # Nacteme layout z Qt Designeru.
    with open('wator/gui/newsimulation.ui') as f:
        uic.loadUi(f, dialog)

    # Zobrazime dialog.
    # Funkce exec zajisti modalitu (tzn. nejde ovladat zbytek aplikace,
    # dokud je dialog zobrazen) a vrati se az potom, co uzivatel dialog zavre.
    result = dialog.exec()

    # Vysledna hodnota odpovida tlacitku/zpusobu, kterym uzivatel dialog zavrel.
    if result == QtWidgets.QDialog.Rejected:
        # Dialog uzivatel zavrel nebo klikl na Cancel.
        return

    # Nacteni hodnot ze SpinBoxu
    cols = dialog.findChild(QtWidgets.QSpinBox, 'colsBox').value()
    rows = dialog.findChild(QtWidgets.QSpinBox, 'rowsBox').value()
    nfish = dialog.findChild(QtWidgets.QSpinBox, 'nfishBox').value()
    nsharks = dialog.findChild(QtWidgets.QSpinBox, 'nsharksBox').value()

    if cols == 0 or rows == 0:
       error = QtWidgets.QErrorMessage()
       error.showMessage('Number of columns or rows can\'t be 0!')
       error.exec()
       return

    wator = WaTor(shape=(rows, cols), nfish=nfish, nsharks=nsharks)
    # Vytvoreni nove mapy
    grid.array = wator.creatures
    grid.energy = wator.energies

    # Mapa muze byt jinak velka, tak musime zmenit velikost Gridu;
    # (tento kod pouzivame i jinde, meli bychom si na to udelat funkci!)
    size = logical_to_pixels(rows, cols)
    grid.setMinimumSize(*size)
    grid.setMaximumSize(*size)
    grid.resize(*size)

    # Prekresleni celeho Gridu
    grid.update()


def save_dialog(window, grid):
    dialog = QtWidgets.QDialog(window)

    #with open('wator/gui/savesimulation.ui') as f:
    #    uic.loadUi(f, dialog)

    #result = dialog.exec()

    #if result == QtWidgets.QDialog.Rejected:
    #    return

    filename, _filter = QtWidgets.QFileDialog.getSaveFileName(None, "Save File", "wator/gui/simulations/", "(*)")
    #filename = dialog.findChild(QtWidgets.QLineEdit, 'filenameLine').text()

    if filename == "":
       return

    #if os.path.isfile(filename):
    #   error = QtWidgets.QMessageBox.critical(None, "Error", "File already exist!")
    #   error.exec()
    #   return

    numpy.savetxt(filename, grid.array)



def open_dialog(window, grid):
    dialog = QtWidgets.QDialog(window)

    #with open('wator/gui/opensimulation.ui') as f:
    #    uic.loadUi(f, dialog)

    #result = dialog.exec()

    #if result == QtWidgets.QDialog.Rejected:
    #    return

    filename, _filter = QtWidgets.QFileDialog.getOpenFileName(None, "Open file", 'wator/gui/simulations/', "(*)")
    #filename = dialog.findChild(QtWidgets.QLineEdit, 'filenameLine').text()

    if filename == "":
       return

    #if not os.path.isfile(filename):
       #error = QtWidgets.QErrorMessage()
       #error.showMessage('File does not exist!')
     #  error = QtWidgets.QMessageBox.critical(None, "Error", "File does not exist!", QtWidgets.QMessageBox.Ok)
      # error.exec()
       #return

    if os.path.getsize(filename) == 0:
       error = QtWidgets.QMessageBox.critical(None, "Error", "File is empty!", QtWidgets.QMessageBox.Ok)
     #  error = QtWidgets.QErrorMessage()
     #  error.showMessage('File is empty!')
     #  error.exec()
       return

    try:
       array = numpy.loadtxt(filename, dtype=numpy.int8)
    except ValueError:
       #error = QtWidgets.QErrorMessage()
       #error.showMessage('File does not contains data for simulation!')
       #error.exec()
       error = QtWidgets.QMessageBox.critical(None, "Error", "File does not contains data for simulation!", QtWidgets.QMessageBox.Ok)
       return



    wator = WaTor(creatures=array)
    grid.array = wator.creatures
    grid.energy = wator.energies

    size = logical_to_pixels(grid.array.shape[0], grid.array.shape[1])
    grid.setMinimumSize(*size)
    grid.setMaximumSize(*size)
    grid.resize(*size)

    grid.update()


def next_chronon(window, grid):

    wator = WaTor(creatures=grid.array, energies=grid.energy)

    age_fish = window.findChild(QtWidgets.QSpinBox, 'age_fishBox').value()
    age_shark = window.findChild(QtWidgets.QSpinBox, 'age_sharkBox').value()
    eat = window.findChild(QtWidgets.QSpinBox, 'energy_eatBox').value()


    wator.setAge_fish(age_fish)
    wator.setAge_shark(age_shark)
    wator.setEnergy_eat(eat)
    wator.tick()
    grid.array = wator.creatures
    grid.energy = wator.energies

    grid.update()



def simulation(window, grid, app):

    wator = WaTor(creatures=grid.array, energies=grid.energy)

    age_fish = window.findChild(QtWidgets.QSpinBox, 'age_fishBox').value()
    age_shark = window.findChild(QtWidgets.QSpinBox, 'age_sharkBox').value()
    eat = window.findChild(QtWidgets.QSpinBox, 'energy_eatBox').value()

    wator.setAge_fish(age_fish)
    wator.setAge_shark(age_shark)
    wator.setEnergy_eat(eat)

    a = 0
    while a < 10:
       wator.tick()
       grid.array = wator.creatures
       grid.energy = wator.energies

       grid.update()
       time.sleep(1)
       app.processEvents()
       a += 1



def printAbout(window, grid):
    about = QtWidgets.QMessageBox.about(None, "About WaTor", "<b>WaTor simulation</b><br>Python module with GUI simulating WaTor sea world<br><br>2017<br>Author: Lenka Stejskalova<br><a href=\"https://github.com/stejsle1/wator\">GitHub stejsle1/wator</a><br>Contains <a href=\"https://pypi.python.org/pypi/PyQt5/5.9.1\">PyQt5</a> and graphics from <a href=\"opengameart.org\">OpenGameArt.org</a>")
    return


def main():
    app = QtWidgets.QApplication([])

    window = QtWidgets.QMainWindow()

    with open('wator/gui/mainwindow.ui') as f:
        uic.loadUi(f, window)

    # mapa zatim nadefinovana rovnou v kodu
    wator = WaTor(shape=(15, 20), nfish=10, nsharks=10)

    # ziskame oblast s posuvniky z Qt Designeru
    scroll_area = window.findChild(QtWidgets.QScrollArea, 'scrollArea')

    # dame do ni nas grid
    grid = GridWidget(wator.creatures, wator.energies)
    scroll_area.setWidget(grid)

    # ziskame paletu vytvorenou v Qt Designeru
    palette = window.findChild(QtWidgets.QListWidget, 'palette')

    for name, svg, num in ('Water', 'wator/gui/water.svg', 0),('Fish', 'wator/gui/fish.svg', 1),('Shark', 'wator/gui/shark.svg', -1):
       item = QtWidgets.QListWidgetItem(name)  # vytvorime polozku
       icon = QtGui.QIcon(svg)  # ikonu
       item.setIcon(icon)  # priradime ikonu polozce
       item.setData(VALUE_ROLE, num)
       palette.addItem(item)  # pridame polozku do palety


    def item_activated():
        """Tato funkce se zavola, kdyz uzivatel zvoli polozku"""

        # Polozek muze obecne byt vybrano vic, ale v nasem seznamu je to
        # zakazano (v Designeru selectionMode=SingleSelection).
        # Projdeme "vsechny vybrane polozky", i kdyz vime ze bude max. jedna.
        for item in palette.selectedItems():
            #print(item.data(VALUE_ROLE))
            grid.selected = item.data(VALUE_ROLE)

    palette.itemSelectionChanged.connect(item_activated)
    palette.setCurrentRow(0) # aby to nesletelo, protoze neni nic vybrano


    # Napojeni signalu actionNew.triggered
    action1 = window.findChild(QtWidgets.QAction, 'actionNew')
    action1.triggered.connect(lambda: new_dialog(window, grid))

    action2 = window.findChild(QtWidgets.QAction, 'actionNext_chronon')
    action2.triggered.connect(lambda: next_chronon(window, grid))

    action3 = window.findChild(QtWidgets.QAction, 'actionSave')
    action3.triggered.connect(lambda: save_dialog(window, grid))

    action4 = window.findChild(QtWidgets.QAction, 'actionOpen')
    action4.triggered.connect(lambda: open_dialog(window, grid))

    action5 = window.findChild(QtWidgets.QAction, 'actionSim')
    action5.triggered.connect(lambda: simulation(window, grid, app))

    action6 = window.findChild(QtWidgets.QAction, 'actionAbout')
    action6.triggered.connect(lambda: printAbout(window, grid))

    init = window.findChild(QtWidgets.QSpinBox, 'energy_initialBox').value()
    grid.initEnergy = init


    window.show()

    return app.exec()

if __name__ == "__main__":
    main()
