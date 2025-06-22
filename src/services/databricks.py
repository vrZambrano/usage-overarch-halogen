from databricks import sql
import os
import pandas as pd

from dotenv import load_dotenv

load_dotenv()

def query_to_dataframe(query: str) -> pd.DataFrame:
    """
    Executa uma query no Databricks e retorna os resultados como um DataFrame pandas.
    
    Args:
        query (str): Query SQL para executar
        
    Returns:
        pd.DataFrame: DataFrame com os resultados da query
    """
    databricks_key = os.getenv("DATABRICKS_KEY")
    
    connection = sql.connect(
        server_hostname="dbc-915e4eed-b4eb.cloud.databricks.com",
        http_path="/sql/1.0/warehouses/d5dcbd75e5cfa79b",
        access_token=databricks_key
    )
    
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        
        # Buscar os dados
        results = cursor.fetchall()
        
        # Obter os nomes das colunas
        columns = [desc[0] for desc in cursor.description]
        
        # Criar o dataframe
        df = pd.DataFrame(results, columns=columns)
        
        return df
        
    finally:
        cursor.close()
        connection.close()

# Exemplo de uso
if __name__ == "__main__":
    query = """
    select tpep_pickup_datetime, tpep_dropoff_datetime, trip_distance, 
           fare_amount, pickup_zip, dropoff_zip 
    from samples.nyctaxi.trips 
    limit 10
    """
    
    df = query_to_dataframe(query)
    
    print("Dataframe criado com sucesso!")
    print(f"Shape: {df.shape}")
    print("\nPrimeiras linhas:")
    print(df.head())
    
    print("\nInfo do dataframe:")
    print(df.info())
    
    print("\nTipos de dados:")
    print(df.dtypes)
