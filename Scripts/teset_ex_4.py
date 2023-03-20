from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSink,
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsFields,
    QgsPoint,
    QgsFeatureSink,
    QgsWkbTypes,
    QgsPointXY,
    QgsProcessingUtils,
    QgsProcessingException,
    QgsSpatialIndex
)
import random
from PyQt5.QtCore import QVariant


class RandomPointsInBufferAlgorithm(QgsProcessingAlgorithm):
    INPUT_LAYER = 'INPUT_LAYER'
    BUFFER_RADIUS = 'BUFFER_RADIUS'
    NUM_POINTS = 'NUM_POINTS'
    OUTPUT_LAYER = 'OUTPUT_LAYER'

    def tr(self,string):
        return QCoreApplication.translate('Processing', string)
        
    def createInstance(self):
        return RandomPointsInBufferAlgorithm()

    def name(self):
        return 'myscript'
        
    def displayName(self):
        return self.tr('My Script')
        
    def group(self):
        return self.tr('Example scripts')
        
    def groupId(self):
        return 'examplescripts'
        
    def shortHelpString(self):
        return 'examplescripts'
    
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER,
                'Input layer'
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.BUFFER_RADIUS,
                'Buffer radius',
                QgsProcessingParameterNumber.Double,
                minValue=0
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.NUM_POINTS,
                'Number of random points',
                QgsProcessingParameterNumber.Integer,
                minValue=1
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_LAYER,
                'Output layer'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, 
        self.INPUT_LAYER, 
        context
        )
        
        buffer_radius = self.parameterAsDouble(parameters, 
        self.BUFFER_RADIUS, 
        context
        )
        
        num_points = self.parameterAsInt(parameters, 
        self.NUM_POINTS, 
        context
        )
        
        (sink, dest_id) = self.parameterAsSink(parameters, 
        self.OUTPUT_LAYER, 
        context,
        QgsFields(), 
        QgsWkbTypes.Point, 
        source.sourceCrs()
        )

        features = source.getFeatures()
        
        # Define o nome do campo do ID da feição da vizinhança
        neighbor_id_field = 'NEIGHBOR_ID'

        # Cria uma matriz para armazenar os IDs das feições da vizinhança
        neighbor_ids = {}

        # Cria um índice espacial para as feições de entrada
        input_index = QgsSpatialIndex(source)

        # Itera sobre as feições de entrada e cria pontos aleatórios dentro dos buffers
        for feat in features:
            geom = feat.geometry()
            buffer_geom = geom.buffer(buffer_radius, 5)
            feats_within_buffer = input_index.intersects(buffer_geom.boundingBox())
            for i in range(num_points):
                rand_point = QgsPoint(random.uniform(buffer_geom.boundingBox().xMinimum(), buffer_geom.boundingBox().xMaximum()), 
                                      random.uniform(buffer_geom.boundingBox().yMinimum(), buffer_geom.boundingBox().yMaximum()))

                # Verifica se o ponto gerado está contido na geometria do buffer
                if buffer_geom.contains(QgsGeometry.fromPointXY(QgsPointXY(rand_point.x(),rand_point.y()))):
                    rand_feat = QgsFeature()
                    rand_feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(rand_point.x(),rand_point.y())))
                    rand_feat.setAttribute(feat.id())                    
                    sink.addFeature(rand_feat)
                else:
                    # Se o ponto não estiver contido na geometria do buffer, gera outro ponto
                    while not buffer_geom.contains(QgsGeometry.fromPointXY(QgsPointXY(rand_point.x(),rand_point.y()))):
                        rand_point = QgsPoint(random.uniform(buffer_geom.boundingBox().xMinimum(), buffer_geom.boundingBox().xMaximum()), 
                                              random.uniform(buffer_geom.boundingBox().yMinimum(), buffer_geom.boundingBox().yMaximum()))
                    rand_feat = QgsFeature()
                    rand_feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(rand_point.x(),rand_point.y())))
                    rand_feat.setAttribute(feat.id())                    
                    sink.addFeature(rand_feat)

        return {self.OUTPUT_LAYER: dest_id}

