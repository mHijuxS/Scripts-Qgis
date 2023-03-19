# Importar módulos necessários
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingContext,
    QgsProject, 
    QgsProcessingFeedback, 
    QgsProcessingAlgorithm, 
    QgsProcessingParameterFeatureSource, 
    QgsProcessingParameterFeatureSink, 
    QgsProcessingParameterString, 
    QgsProcessingOutputVectorLayer, 
    QgsExpression,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsPointXY,
    QgsGeometry,
    QgsApplication,
    QgsWkbTypes
)
from qgis.analysis import QgsNativeAlgorithms
from PyQt5.QtCore import QVariant


class DuplicarVertices(QgsProcessingAlgorithm):
    """
    Algoritmo para criar uma nova camada com os vértices duplicados da camada de entrada.
    """
    
    INPUT_LAYER = 'INPUT'
    OUTPUT_LAYER = 'OUTPUT'
    FLAG_FIELD = 'FLAG_FIELD'
    TEMPORARY_OUTPU = 'TEMPORARY_OUTPUT'
    def tr(self, string):
        return QCoreApplication.translate('Processando', string)
        
    def createInstance(self):
        return DuplicarVertices()
        
    def name(self):
        return 'duplicar_vertices'

    def displayName(self):
        return 'Duplicar Vértices'

    def group(self):
        return 'Meu grupo de processamento'

    def groupId(self):
        return 'meu_grupo_de_processamento'
        
    def shortHelpString(self):
        return self.tr("Exemplo do algoritmo")

    # Definir os parâmetros de entrada do algoritmo
    

    def initAlgorithm(self, config=None):
        # Definir os parâmetros de entrada do algoritmo
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER,
                'Camada de entrada',
                types=[QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_LAYER,
                'Camada de saída',
                )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        # Obter os parâmetros de entrada do algoritmo
        source = self.parameterAsSource(
                        parameters, 
                        self.INPUT_LAYER, 
                        context
                        )
        
        #Criar uma lista de campos de atributo
        fields = QgsFields()
        
        #Adicionar um campo de inteiro chamado "id"
        field_id = QgsField('id',QVariant.Int)
        fields.append(field_id)
        
        #analogamente para "flag"
        field_flag = QgsField('flag',QVariant.String)
        fields.append(field_flag)
        
        (sink, dest_id) = self.parameterAsSink(
                        parameters, 
                        self.OUTPUT_LAYER, 
                        context, 
                        fields, 
                        QgsWkbTypes.Point, 
                        source.sourceCrs())
        
        # Criar uma expressão para o campo "flag"
        
        #Computar os passos totais para comparação do progresso
        total = 100.0 ; source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        
        
        # Iterar sobre as feições da camada de entrada
        for feature in features:
            attributes = feature.attributes()
            
            # Obter a geometria da feição
            geometry = feature.geometry()
            
            if geometry.isMultipart():
                polygon = geometry.asMultiPolygon()[0]
                """
                Somente a primeira parte do multipolígono
                """
            else:
                polygon = geometry.asPolygon()
                
            points=[]
            for ring in polygon:
                for i, point in enumerate(ring):
                    if i < len(ring)-1 or point != ring[0]:
                        points.append(point)
                    
                    
                    
            feedback.pushInfo(f"{points}")
            point_dict = {}
            for point in points:
                if point not in point_dict: # verifica se o ponto ainda não foi adicionado ao dicionário
                    point_dict[point] = 1
                else:
                    point_dict[point] += 1
            

            # exibe os pontos duplicados
            feedback.pushInfo(f"point_dict: {point_dict}")
            for point, count in point_dict.items():
                if count > 1:
                    feedback.pushInfo(f"Ponto {point} aparece {count} vezes na camada")
                    feat = QgsFeature()
                    feat.setGeometry(QgsGeometry.fromPointXY(point))
                    string = "Vértice duplicado na feição de id {} da camada {}".format(feature.id(),source.sourceName())
                    attr = [feature.id(),string]
                    feat.setAttributes(attr)
                    sink.addFeature(feat)
            """
            # Verificar se há vértices duplicados
            for vertex in points:
                if points.count(vertex) > 1:
                                       
                    # Criar uma nova feição com a geometria do vértice duplicado
                    feat = QgsFeature()
                    feat.setGeometry(QgsGeometry.fromPointXY(vertex))

                    # Preencher o campo "flag" com a expressão criada anteriormente
                    feat.setAttributes([feature.id(),f"Vértice duplicado na feição de id {feature.id()} da camada nomedacamadaaqui"])
                    

                    # Adicionar a nova feição à camada de saída
                    sink.addFeature(feat)
           
            # Finalizar o processamento e retornar a camada de saída
        
            """
        return {self.OUTPUT_LAYER: sink}