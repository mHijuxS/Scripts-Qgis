# -*- coding: utf-8 -*-
"""
/***************************************************************************
Lista de exercícios de Programação Aplicada
Grupo 2
Alunos:
 - Al Charles
 - Al Ferreira
 - Al Nojima
Solução Questão 1
 ***************************************************************************/
"""
"""
Importa o módulo de interface do QGIS
"""
from qgis.utils import iface
from PyQt5.QtWidgets import QMessageBox

"""
Obtém a camada selecionada pelo usuário
"""
layer = iface.activeLayer()

if layer is None:
    """
    Se não houver uma camada selecionada, exibe uma mensagem de erro e encerra o script
    """
    QMessageBox.critical(iface.mainWindow(), "Erro", "Nenhuma camada selecionada. Selecione uma camada e execute o script novamente.")
else:
    """
    Obtém uma lista de todos os grupos e camadas carregadas
    """
    root = QgsProject.instance().layerTreeRoot()
    all_layers = root.findLayers()
    """
    Itera sobre a lista e alterna a visibilidade dos grupos e camadas, exceto a camada selecionada
    """
    for node in all_layers:
        if node.layer() != layer:
            node.setItemVisibilityChecked(False)