# -- coding: utf-8 --
"""
/*************************
Lista de exercícios de Programação Aplicada
Grupo 2
Alunos:
 - Al Ferreira
 - Al Charles
 - Al Nojima
Solução Questão 7
 *************************/
"""
from qgis.PyQt.QtCore import (QVariant, QCoreApplication) 
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterNumber,
                       QgsCoordinateReferenceSystem,
                       QgsField,
                       QgsFields,
                       QgsGeometry,
                       QgsFeature)
from qgis import processing

from qgis.utils import iface

# Cria uma subclasse de QgsProcessingAlgorithm chamada EliminarBuracosMenores
class EliminarBuracosMenores(QgsProcessingAlgorithm):
    # Define as constantes INPUT, TOLERANCIA e OUTPUT
    INPUT = 'INPUT'
    TOLERANCIA = 'TOLERANCIA'
    OUTPUT = 'OUTPUT'
   
   # Define a função de tradução tr
    def tr(self, string):
        return QCoreApplication.translate('EliminarBuracosMenores', string)
    
    # Cria uma instância da classe EliminarBuracosMenores
    def createInstance(self):
        return EliminarBuracosMenores()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'EliminarBuracosMenores'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Exercício 7')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Programação Aplicada')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'programacaoaplicada'
    
    # Define a mensagem que será exibida na caixa de ajuda do algoritmo
    def shortHelpString(self):
        return self.tr('Esse algoritmo remove buracos menores que uma determinada tolerância')

    # Define os parâmetros de entrada do algoritmo
    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                'INPUT',
                self.tr('Input layer(s)'),
                QgsProcessing.TypeVectorPolygon
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                'TOLERANCIA',
                self.tr('TOLERANCIA'),
                type=QgsProcessingParameterNumber.Double,
                minValue=0)
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Flags')
            )
        )
    # Define o processo principal do algoritmo
    def processAlgorithm(self, parameters, context, feedback):

        feedback.setProgressText(
            self.tr('Buscando buracos maiores que a tolerancia'))
        # Obtém a lista de camadas de entrada
        layerList = self.parameterAsLayerList(
            parameters, 'INPUT', context)
        # Obtém a tolerância informada pelo usuário
        minSize = self.parameterAsDouble(parameters, 'TOLERANCIA', context)
        # Obtém o sistema de coordenadas de referência do mapa
        CRSstr = iface.mapCanvas().mapSettings().destinationCrs().authid()
        CRS = QgsCoordinateReferenceSystem(CRSstr)
        # Cria uma lista para armazenar os buracos grandes encontrados
        bigRings = []
        # Obtem o número de camadas na lista
        listSize = len(layerList)
        # Define um passo de progresso para cada camada
        progressStep = 100/listSize if listSize else 0
        # Define o contador de passos para 0
        step = 0
        # Itera sobre cada camada na lista
        for step, layer in enumerate(layerList):
            # Verifica se o usuário cancelou a operação
            if feedback.isCanceled():
                return {self.OUTPUT: bigRings}
            # Itera sobre cada feição na camada
            for feature in layer.getFeatures():
                # Verifica se a feição possui geometria
                if not feature.hasGeometry():
                    continue
                # Obtém a geometria da feição como um polígono multiparte
                for poly in feature.geometry().asMultiPolygon():
                    # Seleciona apenas os anéis internos do polígono
                    onlyrings = poly[1:]
                    for ring in onlyrings:
                        # Cria uma nova geometria a partir do anel atual
                        newRing = QgsGeometry.fromPolygonXY([ring])
                        # Verifica se a área da nova geometria é maior que a tolerância
                        print(newRing.area())
                        if newRing.area() > minSize:
                            bigRings.append(newRing)
            # Atualiza o progresso
            feedback.setProgress(step * progressStep)
        # Verifica se foram encontrados anéis grandes
        if len(bigRings) == 0:
            flagLayer = self.tr(
                f'Holes greater than {str(minSize)} were not found')
            return{self.OUTPUT: flagLayer}
        # Caso contrário, cria uma nova camada contendo os buracos grandes encontrados
        flagLayer = self.outputLayer(parameters, context, bigRings, CRS, 6)
        return{self.OUTPUT: flagLayer}
    # Cria uma nova camada a partir dos buracos grandes encontrados
    def outputLayer(self, parameters, context, bigRings, CRS, geomType):
        newField = QgsFields()
        newField.append(QgsField('area', QVariant.Double))
        features = bigRings
        (sink, newLayer) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            newField,
            geomType,
            CRS
        )
        for feature in features:
            newFeat = QgsFeature()
            newFeat.setGeometry(feature)
            newFeat.setFields(newField)
            newFeat['area'] = feature.area()
            sink.addFeature(newFeat, QgsFeatureSink.FastInsert)

        return newLayer


        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )

        if source is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs()
        )

        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))

        if sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.OUTPUT))

        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()

        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break

            sink.addFeature(feature, QgsFeatureSink.FastInsert)

            feedback.setProgress(int(current * total))

        if False:
            buffered_layer = processing.run("native:buffer", {
                'iNPUT': dest_id,
                'DISTANCE': 1.5,
                'SEGMENTS': 5,
                'END_CAP_STYLE': 0,
                'JOIN_STYLE': 0,
                'MITER_LIMIT': 2,
                'DISSOLVE': False,
                'OUTPUT': 'memory:'
            }, context=context, feedback=feedback)['OUTPUT']

        return {self.OUTPUT: dest_id}