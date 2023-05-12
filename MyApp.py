from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from my_modules import dbpia_crawler as crl
import sys, re

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.page = 1
        self.page_end = 1
        self.index_end = 0

    def initUI(self):
        self.setWindowTitle('Crawler')
        self.setGeometry(300, 300, 800, 600)

        tab_search = QWidget()
        tab_moreinfo = QWidget()

        self.search = QLineEdit(self)
        self.search.returnPressed.connect(self.inputKeyword)

        self.page_btn = QPushButton("Page", self)
        self.page_btn.clicked.connect(self.getPage)

        hbox = QHBoxLayout()
        hbox.addWidget(self.search)
        hbox.addWidget(self.page_btn)

        self.output = QTextBrowser(self)
        self.output.setOpenExternalLinks(True)

        self.nowpage_label_f = QLabel("Here is ")
        self.nowpage_label_f.setAlignment(Qt.AlignRight)
        self.nowpage_label_l = QLabel(" page on your results.")
        self.nowpage_label_l.setAlignment(Qt.AlignLeft)
        
        self.nowpages = QComboBox(self)
        self.nowpages.activated[str].connect(self.movePage)

        hbox_label = QHBoxLayout()
        hbox_label.addWidget(self.nowpage_label_f)
        hbox_label.addWidget(self.nowpages)
        hbox_label.addWidget(self.nowpage_label_l)

        vbox_tab1 = QVBoxLayout()
        vbox_tab1.addLayout(hbox)
        vbox_tab1.addWidget(self.output)
        vbox_tab1.addLayout(hbox_label)

        tab_search.setLayout(vbox_tab1)

        self.search_index = QLineEdit(self)
        self.search_index.returnPressed.connect(self.inputIndex)
        
        self.search_index_label = QLabel("Enter Your Index: ")

        self.show_info = QTextBrowser(self)
        self.show_info.setOpenExternalLinks(True)

        hbox_search_index = QHBoxLayout()
        hbox_search_index.addWidget(self.search_index_label)
        hbox_search_index.addWidget(self.search_index)

        vbox_info = QVBoxLayout()
        vbox_info.addLayout(hbox_search_index)
        vbox_info.addWidget(self.show_info)

        tab_moreinfo.setLayout(vbox_info)

        tabs = QTabWidget()
        tabs.addTab(tab_search, "Search")
        tabs.addTab(tab_moreinfo, "Find with Index")

        vbox_main = QVBoxLayout()
        vbox_main.addWidget(tabs)

        self.setLayout(vbox_main)
        self.show()
    
    def inputKeyword(self):
        self.keyword = self.search.text()
        self.search.clear()
        self.get, self.page_end, self.index_end = crl.crawl(self.keyword, self.page)
        self.updateElement(self.get, 1)
        self.updateNowPages()
    
    def updateElement(self, result, n):
        self.output.clear()
        for thesisdict in result:
            if thesisdict["page"] != int(n): continue
            line = f'<b>{str(thesisdict["index"])}</b>' +" "+ thesisdict["title"] +" "+ f'<a href="{str(thesisdict["href"])}">Goto</a>' +" "+ f'<a href="{str(thesisdict["view_link"])}">View</a>'
            self.output.append(line)

    def getPage(self):
        page, ok = QInputDialog.getText(self, 'Pop up', 'Enter your pages:')
        try:
            page = int(page)
        except: return
        if ok and page >= 1:
            self.page = page
    
    def updateNowPages(self):
        for n in range(1, int(self.page_end)+1):
            self.nowpages.addItem(str(n))
    
    def movePage(self, index):
        self.updateElement(self.get, index)
    
    def inputIndex(self):
        self.index = int(self.search_index.text())
        self.search_index.clear()
        self.updateInfo()

    def updateInfo(self):
        self.show_info.clear()
        if int(self.index) > self.index_end:
            QMessageBox.about(self, "Warning", "Can't find with index that is out of range.")
        else:
            find = self.get[self.index]
            for key in list(find.keys()):
                if str(key) == "href" or str(key) == "view_link":
                    value = f'<a href="{str(find[key])}">{str(find[key])}</a>'
                elif str(key) == "author" or str(key) == "keyword":
                    value = ''
                    for element in find[key]:
                        value = value +"_"+ element
                    value = re.sub("_", " | ", str(value[1:]))
                else:
                    value = str(find[key])
                
                self.show_info.append(f'{str(key)}: {value}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())