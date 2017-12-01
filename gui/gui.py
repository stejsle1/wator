from PyQt5 import QtWidgets, QtGui, QtCore, QtSvg, uic
import numpy

CELL_SIZE = 32

SVG_WATER = QtSvg.QSvgRenderer('water.svg')
SVG_FISH = QtSvg.QSvgRenderer('fish.svg')
SVG_SHARK = QtSvg.QSvgRenderer('shark.svg')

VALUE_ROLE = QtCore.Qt.UserRole

def pixels_to_logical(x, y):
    return y // CELL_SIZE, x // CELL_SIZE


def logical_to_pixels(row, column):
    return column * CELL_SIZE, row * CELL_SIZE


class GridWidget(QtWidgets.QWidget):
    def __init__(self, array):
        super().__init__()  # musime zavolat konstruktor predka
        self.array = array
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

            # timto zajistime prekresleni widgetu v miste zmeny:
            # (pro Python 3.4 a nizsi volejte jen self.update() bez argumentu)
            self.update(*logical_to_pixels(row, column), CELL_SIZE, CELL_SIZE)    
        
    # vzdycky, kdyz je treba neco prekreslit, kdyz je treba, reaguje na udalost
    # metoda, protoze nejde pouzit v connect(slot)    
    def paintEvent(self, event):
        rect = event.rect()  # ziskame informace o rrekreslovane oblasti

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
                painter.fillRect(rect, QtGui.QBrush(color))    

def new_dialog(window, grid):
    # Vytvorime novy dialog.
    # V dokumentaci maji dialogy jako argument `this`;
    # jde o "nadrazene" okno.
    dialog = QtWidgets.QDialog(window)

    # Nacteme layout z Qt Designeru.
    with open('newsimulation.ui') as f:
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
    cols = dialog.findChild(QtWidgets.QSpinBox, 'widthBox').value()
    rows = dialog.findChild(QtWidgets.QSpinBox, 'heightBox').value()

    # Vytvoreni nove mapy
    grid.array = numpy.zeros((rows, cols), dtype=numpy.int8)

    # Mapa muze byt jinak velka, tak musime zmenit velikost Gridu;
    # (tento kod pouzivame i jinde, meli bychom si na to udelat funkci!)
    size = logical_to_pixels(rows, cols)
    grid.setMinimumSize(*size)
    grid.setMaximumSize(*size)
    grid.resize(*size)

    # Prekresleni celeho Gridu
    grid.update()
    
            
def main():
    app = QtWidgets.QApplication([])

    window = QtWidgets.QMainWindow()

    with open('mainwindow.ui') as f:
        uic.loadUi(f, window)
        
    # mapa zatim nadefinovana rovnou v kodu
    array = numpy.zeros((15, 20), dtype=numpy.int8)
    array[:, 5] = -1  # nejaka zed

    # ziskame oblast s posuvniky z Qt Designeru
    scroll_area = window.findChild(QtWidgets.QScrollArea, 'scrollArea')

    # dame do ni nas grid
    grid = GridWidget(array)
    scroll_area.setWidget(grid)    
    
    # ziskame paletu vytvorenou v Qt Designeru
    palette = window.findChild(QtWidgets.QListWidget, 'palette')

    for name, svg, num in ('Water', 'water.svg', 1),('Fish', 'fish.svg', 2),('Shark', 'shakr.svg', 3):
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
            print(item.data(VALUE_ROLE))

    palette.itemSelectionChanged.connect(item_activated)
    palette.setCurrentRow(1) # aby to nesletelo, protoze neni nic vybrano
    
    # Napojeni signalu actionNew.triggered
    action = window.findChild(QtWidgets.QAction, 'actionNew')
    action.triggered.connect(lambda: new_dialog(window, grid))
    
    window.show()

    return app.exec()

main()        