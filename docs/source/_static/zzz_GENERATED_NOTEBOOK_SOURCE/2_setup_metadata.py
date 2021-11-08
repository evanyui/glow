# Databricks notebook source
# MAGIC %md
# MAGIC ##### run metadata
# MAGIC 
# MAGIC Warning: this will only work in Databricks
# MAGIC 
# MAGIC It requires the databricks-cli to be installed via pip 
# MAGIC 
# MAGIC (this is included in the `projectglow/databricks-glow` docker container)

# COMMAND ----------

import pyspark.sql.functions as fx
from pyspark.sql.types import *
from databricks_cli.sdk.service import JobsService
from databricks_cli.sdk.service import ClusterService
from databricks_cli.configure.config import _get_api_client
from databricks_cli.configure.provider import get_config

from pathlib import Path

# COMMAND ----------

user=dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().apply('user')
dbfs_home_path = Path("dbfs:/home/{}/".format(user))
run_metadata_delta_path = str(dbfs_home_path / "genomics/data/delta/gwas_runs_info_hail_glow.delta")

# COMMAND ----------

cluster_id=dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().apply('clusterId')

# COMMAND ----------

cs = ClusterService(_get_api_client(get_config()))
_list = cs.list_clusters()['clusters']
conv = lambda x: {c:v for c,v in x.items() if type(v) in (str, int)}
cluster_info = spark.createDataFrame([conv(x) for x in _list])
cluster_info = cluster_info.where(fx.col("cluster_id") == cluster_id)
worker_info = cluster_info.select("node_type_id", "num_workers", "spark_version", "creator_user_name").collect()
node_type_id = worker_info[0].node_type_id
n_workers = worker_info[0].num_workers
spark_version = worker_info[0].spark_version
creator_user_name = worker_info[0].creator_user_name

# COMMAND ----------

display(cluster_info)

# COMMAND ----------

print("spark_version = " + str(spark_version))
print("node_type_id = " + str(node_type_id))
print("n_workers = " + str(n_workers))
print("creator_user_name = " + str(creator_user_name))

# COMMAND ----------

#define schema for logging runs in delta lake
schema = StructType([StructField("datetime", DateType(), True),
                     StructField("n_samples", LongType(), True),
                     StructField("n_variants", LongType(), True),
                     StructField("n_covariates", LongType(), True),
                     StructField("n_phenotypes", LongType(), True),
                     StructField("method", StringType(), True),
                     StructField("test", StringType(), True),
                     StructField("library", StringType(), True),
                     StructField("spark_version", StringType(), True),
                     StructField("node_type_id", StringType(), True),
                     StructField("worker_type", LongType(), True),
                     StructField("runtime", DoubleType(), True)
                    ])