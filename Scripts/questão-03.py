# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProject,
                       QgsVectorLayer,
                       QgsPointXY,
                       QgsField,
                       QgsFields,
                       QgsFeature,
                       QgsGeometry,
                       QgsWkbTypes,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from qgis import processing
from qgis.utils import iface
from PyQt5.QtCore import QVariant
import math


class PontosMediosPoligonosOrdenados(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        
        return QCoreApplication.translate('Processando', string)

    def createInstance(self):
        return PontosMediosPoligonosOrdenados()

    def name(self):
        
        return 'pontosmediospoligonosordenados'

    def displayName(self):
       
        return self.tr('Exercício 3')

    def group(self):
        
        return self.tr('Programação Aplicada')

    def groupId(self):
        
        return 'programacaoaplicada'

    def shortHelpString(self):
        
        return self.tr("Esse algoritmo identifica os pontos medios dos polígonos e cria uma nova camada com esses pontos ordenados do mais ao norte em sentido horario.")

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Camada Input'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Camada De Pontos'),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        # Conseguir as feições do input e do output
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )

        # Caso o input não seja criado, jogue uma exceção para indicar que o algoritmo encontrou
        # um erro fatal.
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
        # Crie uma lista de campos de atributos
        fields = QgsFields()

        # Adicione um campo de texto chamado "id"
        field_name = QgsField('id', QVariant.String)
        fields.append(field_name)

        # Adicione um campo numérico chamado "ordem"
        field_idade = QgsField('ordem', QVariant.Int)
        fields.append(field_idade)

        
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.Point,
            source.sourceCrs()
        )

        # Caso o output não seja criado, jogue uma exceção para indicar que o algoritmo encontrou
        # um erro fatal.
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Computar os passos totais para comparação
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()

        for current,feature in enumerate(features):
            """
            cancela a operacao caso aperte cancelar
            """ 
            if feedback.isCanceled():
                break

            geom = feature.geometry()
            
            if geom.isMultipart():
                polygon = geom.asMultiPolygon()[0]
                """
                Somente a primeira parte do multipolígono
                """
            else:
                polygon = geom.asPolygon()
                
            """
            Obtém as coordenadas dos pontos médios dos lados de cada polígono
            """
            
            points = []
            for ring in polygon:
                for i in range(len(ring)-1):
                    lineStart = ring[i]
                    if i == len(ring)-1:
                        lineEnd =ring[0]
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
                sink.addFeature(feat)
                
            #atualiza a barra de carregamento
            feedback.setProgress(int(current * total))
        
        
        return {self.OUTPUT: dest_id}
