###testestjksl
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSink,
    QgsProcessingOutputVectorLayer,
    QgsGeometry,
    QgsFeature,
    QgsField,
    QgsWkbTypes,
    QgsFields,
    QgsPointXY
)
from qgis import processing
from PyQt5.QtCore import QVariant

class RandomPointsInBufferAlgorithm(QgsProcessingAlgorithm):
    """
    Processamento para gerar pontos aleatórios dentro dos buffers das feições
    """
    INPUT_LAYER = 'INPUT_LAYER'
    BUFFER_RADIUS = 'BUFFER_RADIUS'
    NUM_POINTS = 'NUM_POINTS'
    OUTPUT_LAYER = 'OUTPUT_LAYER'
    
    # Define a função de tradução tr
    def tr(self, string):
        return QCoreApplication.translate('RandomPointsInBufferAlgorithm', string)
    
    # Cria uma instância da classe RandomPointsInBufferAlgorithm
    def createInstance(self):
        return RandomPointsInBufferAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'RandomPointsInBufferAlgorithm'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Exercício 4')

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
    
    def initAlgorithm(self, config=None):
        """
        Inicializa o processamento
        """
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_LAYER,
            'Camada de entrada',
            types=[QgsProcessing.TypeVectorPolygon]
        ))
        
        self.addParameter(QgsProcessingParameterNumber(
            self.BUFFER_RADIUS,
            'Raio do buffer',
            type=QgsProcessingParameterNumber.Double,
            minValue=0.0
        ))
        
        self.addParameter(QgsProcessingParameterNumber(
            self.NUM_POINTS,
            'Número de pontos aleatórios',
            type=QgsProcessingParameterNumber.Integer,
            minValue=0
        ))
        
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT_LAYER,
            'Camada de saída',
            type=QgsProcessing.TypeVectorPoint
        ))
        
    def processAlgorithm(self, parameters, context, feedback):
        """
        Executa o processamento
        """
        # Obter os parâmetros de entrada
        input_layer = self.parameterAsSource(parameters, self.INPUT_LAYER, context)
        buffer_radius = self.parameterAsDouble(parameters, self.BUFFER_RADIUS, context)
        num_points = self.parameterAsInt(parameters, self.NUM_POINTS, context)
        
        # Criar os campos de atributos para a camada de saída
        input_fields = input_layer.fields()
        output_fields = QgsFields()
        for field in input_fields:
            output_fields.append(field)
        output_fields.append(QgsField('feicao_id', QVariant.Int))
        
        # Criar a camada de saída
        output_layer = self.parameterAsSink(parameters, self.OUTPUT_LAYER, context,
                                             output_fields, QgsWkbTypes.Point, input_layer.sourceCrs())
        
        # Obter as feições de entrada
        features = input_layer.getFeatures()
        
        # Loop sobre as feições de entrada
        for feat in features:
            # Criar um buffer em torno da feição
            buffer_geom = feat.geometry().buffer(buffer_radius, 30)
            
            # Loop para gerar os pontos aleatórios
            for i in range(num_points):
                # Gerar um ponto aleatório dentro do buffer
                random_point = buffer_geom.randomPoint()
                
                # Criar uma nova feição para o ponto aleatório
                output_feat = QgsFeature(output_fields)
                output_feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(random_point)))
                
                # Copiar os atributos da feição de entrada para a feição de saída
                for field in input_fields:
                    output_feat[field.name()] = feat[field.name()]
                
                # Armazenar o ID da feição de entrada
                output_feat['feicao_id'] = feat.id()
                
                # Adicionar a feição de saída à camada de saída
                output_layer.addFeature(output_feat)
                
                # Verificar se o processamento foi cancelado pelo usuário
                if feedback.isCanceled():
                    return {self.OUTPUT_LAYER: None}
                
                # Atualizar o progresso do processamento
                feedback.setProgress(int(i / num_points * 100))
        
        # Retornar a camada de saída
        return {self.OUTPUT_LAYER: output_layer}