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
    QgsWkbTypes,
    QgsProcessingUtils,
    QgsProcessingException,
    QgsSpatialIndex
)
import random

class RandomPointsInBufferAlgorithm(QgsProcessingAlgorithm):
    INPUT_LAYER = 'INPUT_LAYER'
    BUFFER_RADIUS = 'BUFFER_RADIUS'
    NUM_POINTS = 'NUM_POINTS'
    OUTPUT_LAYER = 'OUTPUT_LAYER'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER,
                'Input layer'
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
                'Output layer',
                QgsProcessing.TypeVectorPoint
            )
        )

def processAlgorithm(self, parameters, context, feedback):
        input_layer = self.parameterAsSource(parameters, self.INPUT_LAYER, context)
        buffer_radius = self.parameterAsDouble(parameters, self.BUFFER_RADIUS, context)
        num_points = self.parameterAsInt(parameters, self.NUM_POINTS, context)
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT_LAYER, context,
                                                QgsFields(), QgsWkbTypes.Point, input_layer.sourceCrs())

        # Define o nome do campo do ID da feição da vizinhança
        neighbor_id_field = 'NEIGHBOR_ID'

        # Cria uma matriz para armazenar os IDs das feições da vizinhança
        neighbor_ids = {}

        # Cria um índice espacial para as feições de entrada
        input_index = QgsSpatialIndex(input_layer)

        # Itera sobre as feições de entrada e cria pontos aleatórios dentro dos buffers
        for feat in input_layer.getFeatures():
            geom = feat.geometry()
            buffer_geom = geom.buffer(buffer_radius, 5)
            feats_within_buffer = input_index.intersects(buffer_geom.boundingBox())
            for i in range(num_points):
                rand_point = QgsPoint(random.uniform(buffer_geom.boundingBox().xMinimum(), buffer_geom.boundingBox().xMaximum()), 
                                      random.uniform(buffer_geom.boundingBox().yMinimum(), buffer_geom.boundingBox().yMaximum()))

                # Verifica se o ponto gerado está contido na geometria do buffer
                if buffer_geom.contains(QgsGeometry.fromPointXY(rand_point)):
                    rand_feat = QgsFeature()
                    rand_feat.setGeometry(QgsGeometry.fromPointXY(rand_point))
                    rand_feat.setFields(sink.fields())
                    rand_feat.setAttribute(neighbor_id_field, feat.id())
                    sink.addFeature(rand_feat, QgsFeatureSink.FastInsert)
                else:
                    # Se o ponto não estiver contido na geometria do buffer, gera outro ponto
                    while not buffer_geom.contains(QgsGeometry.fromPointXY(rand_point)):
                        rand_point = QgsPoint(random.uniform(buffer_geom.boundingBox().xMinimum(), buffer_geom.boundingBox().xMaximum()), 
                                              random.uniform(buffer_geom.boundingBox().yMinimum(), buffer_geom.boundingBox().yMaximum()))
                    rand_feat = QgsFeature()
                    rand_feat.setGeometry(QgsGeometry.fromPointXY(rand_point))
                    rand_feat.setFields(sink.fields())
                    rand_feat.setAttribute(neighbor_id_field, feat.id())
                    sink.addFeature(rand_feat, QgsFeatureSink.FastInsert)

        return {self.OUTPUT_LAYER: dest_id}

