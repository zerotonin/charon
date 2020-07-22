from importlib import reload
import folderAutomaton

reload(folderAutomaton)
x = folderAutomaton.folderAutomaton()  

x.run()