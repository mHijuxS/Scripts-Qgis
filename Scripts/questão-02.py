# -*- coding: utf-8 -*-
"""
/***************************************************************************
Lista de exercícios de Programação Aplicada
Grupo 2
Alunos:
 - Al Charles
 - Al Ferreira
 - Al Nojima
Solução Questão 2
 ***************************************************************************/
"""


"""
cria grupo pai "MEU_GRUPO"
"""
meu_grupo = QgsProject.instance().layerTreeRoot().addGroup("MEU_GRUPO")

"""
cria subgrupos filhos de "MEU_GRUPO"
"""
ponto_group = meu_grupo.addGroup("Ponto")
linha_group = meu_grupo.addGroup("Linha")
area_group = meu_grupo.addGroup("Area")
imagem_group = meu_grupo.addGroup("Imagem")

"""
obtém as camadas selecionadas
"""
layers = iface.layerTreeView().selectedLayers()

"""
adiciona as camadas selecionadas aos subgrupos correspondentes
"""
if layer in layers == QgsMapLayerType.RasterLayer:
    imagem_group.addLayer(layer)
else: 
    for layer in layers:
        if layer.type() == QgsMapLayerType.RasterLayer: 
            """
            camada raster
            """
            imagem_group.addLayer(layer)
        elif layer.geometryType() == 0:
            """
            camada de ponto
            """
            ponto_group.addLayer(layer)
        elif layer.geometryType() == 1:
            """
            camada de linha
            """
            linha_group.addLayer(layer)
        elif layer.geometryType() == 2:
            """
            camada de poligono
            """
            area_group.addLayer(layer)