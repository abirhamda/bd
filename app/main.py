from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml import PipelineModel

# 1. Créer une SparkSession
spark = SparkSession.builder \
    .appName("SuicideRatePrediction") \
    .getOrCreate()

# 2. Lire le fichier CSV
df = spark.read.csv("/app/Data3.csv", header=True, inferSchema=True)

# 3. Nettoyage des données
df = df.dropna()

# 4. Création de la colonne suicide_rate
df = df.withColumn("suicide_rate", (col("suicides_no") / col("population")) * 100000)

# 5. Encodage des variables catégorielles
indexers = [
    StringIndexer(inputCol="country", outputCol="country_indexed", handleInvalid="keep"),
    StringIndexer(inputCol="sex", outputCol="sex_indexed", handleInvalid="keep"),
    StringIndexer(inputCol="age", outputCol="age_indexed", handleInvalid="keep")
]

# 6. Assemblage des features
assembler = VectorAssembler(
    inputCols=["country_indexed", "year", "sex_indexed", "age_indexed", "population"],
    outputCol="features"
)

# 7. Modèle Random Forest
rf = RandomForestRegressor(featuresCol="features", labelCol="suicide_rate", maxBins=256)


# 8. Pipeline
pipeline = Pipeline(stages=indexers + [assembler, rf])

# 9. Séparation des données
train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)

# 10. Entraînement
model = pipeline.fit(train_data)

# 11. Prédiction
predictions = model.transform(test_data)

# 12. Évaluation
evaluator_r2 = RegressionEvaluator(labelCol="suicide_rate", predictionCol="prediction", metricName="r2")
evaluator_rmse = RegressionEvaluator(labelCol="suicide_rate", predictionCol="prediction", metricName="rmse")

r2 = evaluator_r2.evaluate(predictions)
rmse = evaluator_rmse.evaluate(predictions)

print(f"\n=== Évaluation du modèle Random Forest ===")
print(f"R² Score: {r2:.4f}")
print(f"RMSE: {rmse:.4f}")

# 13. Sauvegarde du modèle
model.save("/app/best_rf_model")

# 14. Rechargement et test sur une donnée simulée
# Exemple de test_data : [117, 2015, 1, 1, 4609] -> attention à l'ordre des colonnes encodées

# Pour recharger le modèle plus tard :
# loaded_model = PipelineModel.load("/app/best_rf_model")
# test_df = spark.createDataFrame([(117.0, 2015.0, 1.0, 1.0, 4609.0)], ["country_indexed", "year", "sex_indexed", "age_indexed", "population"])
# test_df = assembler.transform(test_df)
# prediction = loaded_model.transform(test_df)
# prediction.select("prediction").show()

spark.stop()
