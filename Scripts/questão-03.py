# -*- coding: utf-8 -*-
"""
/***************************************************************************
Lista de exercícios de Programação Aplicada
Grupo 2
Alunos:
 - Al Charles
 - Al Ferreira
 - Al Nojima
Solução Questão 3
 ***************************************************************************/
"""

"""
Define o nome da camada de entrada e de saída
"""
inputLayerName = iface.activeLayer().name()
outLayerName = "camada_de_pontos"

"""
Obtém a camada de entrada
"""
inputLayer = QgsProject.instance().mapLayersByName(inputLayerName)[0]

"""
Cria a camada de saída
"""
outLayer = QgsVectorLayer("Point?crs=EPSG:4326&field=id:integer&field=ord:integer", outLayerName, "memory")

"""
Adiciona os campos de ID e ordenação na camada de saída
"""
provider = outLayer.dataProvider()
provider.addAttributes([QgsField("id", QVariant.Int), QgsField("ord", QVariant.Int)])
outLayer.updateFields()

"""
Inicia a edição da camada de saída
"""
outLayer.startEditing()

"""
Itera sobre as feições da camada de entrada
"""
for feature in inputLayer.getFeatures():
    
    geom = feature.geometry()
    
    """
    Verifica se a geometria é um polígono único ou um multipolígono
    """
    if geom.isMultipart():
        polygon = geom.asMultiPolygon()[0] 
        """
        Somente a primeira parte do multipolígono
        """
    else:
        polygon = geom.asPolygon()

    """
    Obtém as coordenadas dos pontos médios de cada lado do polígono
    """
    points = []
    for ring in polygon:
        for i in range(len(ring)-1):
            lineStart = ring[i]
            if i == len(ring)-1:
                lineEnd = ring[0]
            else:
                lineEnd = ring[i+1]
            point = QgsPointXY(lineStart.x() + (lineEnd.x() - lineStart.x())/2, lineStart.y() + (lineEnd.y() - lineStart.y())/2)
            points.append(point)
    """
    Ordena os pontos de acordo com sua posição em sentido horário a partir do ponto mais ao norte
    """
    north = max(points, key=lambda p: p.y())
    sortedPoints = sorted(points, key=lambda p: -math.atan2(p.y() - north.y(), p.x() - north.x()))

    """
    Adiciona os pontos na camada de saída
    """
    for i, point in enumerate(sortedPoints):
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPointXY(point))
        feat.setAttributes([feature.id(), i+1])
        provider.addFeatures([feat])

"""
Salva as alterações e encerrar a edição da camada de saída
"""
outLayer.commitChanges()

"""
Adiciona a camada de saída no mapa
"""
QgsProject.instance().addMapLayer(outLayer)



