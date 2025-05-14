from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel

# 1. Créer une SparkSession
spark = SparkSession.builder \
    .appName("SuicideRatePrediction") \
    .getOrCreate()

# 2. Charger le modèle
model = PipelineModel.load("/app/best_rf_model")

# 3. Créer une entrée de test avec les mêmes colonnes que le dataset brut
# Exemple : country, year, sex, age, population
data = [("Algeria", 2015, "male", "15-24 years", 4609)]
columns = ["country", "year", "sex", "age", "population"]

df = spark.createDataFrame(data, columns)

# 4. Appliquer le modèle
predicted = model.transform(df)

# 5. Afficher le résultat
predicted.select("country", "sex", "age", "population", "prediction").show()

spark.stop()
