from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor
from airflow.operators.bash import BashOperator
from airflow.hooks.base import BaseHook
from datetime import datetime
from kafka import KafkaConsumer
from decimal import Decimal
from tempfile import NamedTemporaryFile
import json
import base64
import time

def decode_decimal(encoded_value):
    try:
        if encoded_value is None:
            return None
        decoded = base64.b64decode(encoded_value).decode('utf-8')
        return Decimal(decoded)
    except Exception as e:
        print(f"⚠️ Error decoding price: {e} | value: {encoded_value}")
        return None

# Task: Consume messages from Kafka
def consume_from_kafka(**kwargs):
    kafka_conn_id = kwargs['kafka_conn_id']
    topic_name = kwargs['topic_name']
    batch_size = kwargs.get('batch_size', 100)
    ti = kwargs['ti']
    task_instance_key = ti.task_id + '_' + ti.run_id

    kafka_hook = BaseHook.get_connection(kafka_conn_id)
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=kafka_hook.host.split(','),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='airflow-kafka-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    messages = []
    timeout = time.time() + 30  # wait max 30s
    while len(messages) < batch_size and time.time() < timeout:
        raw_msgs = consumer.poll(timeout_ms=1000)
        for tp, msgs in raw_msgs.items():
            for msg in msgs:
                messages.append(msg.value['payload'])

    if messages:
        ti.xcom_push(key=f'kafka_messages_{task_instance_key}', value=messages)
        print(f"✅ Consumed {len(messages)} messages.")
    else:
        print("⚠️ No messages consumed.")

# Sensor: Check if Kafka messages are available
def check_kafka_messages(**kwargs):
    ti = kwargs['ti']
    task_instance_key = 'consume_from_kafka' + '_' + ti.run_id
    messages = ti.xcom_pull(task_ids='consume_from_kafka', key=f'kafka_messages_{task_instance_key}')
    return messages is not None and len(messages) > 0

# Task: Transform messages and write to JSONL
def transform_data(ti, **kwargs):
    task_instance_key = 'consume_from_kafka' + '_' + ti.run_id
    kafka_messages = ti.xcom_pull(task_ids='consume_from_kafka', key=f'kafka_messages_{task_instance_key}')
    
    transformed_data = []

    for message in kafka_messages:
        op = message.get("op")
        if op not in ("c", "u", "d"):  # Skip 'r' snapshot reads
            continue

        data = message.get("after") if op in ("c", "u") else message.get("before")
        if not data:
            continue

        row_id = data.get("id")
        if row_id is None:
            print(f"⚠️ Skipped row with null id: {data}")
            continue

        price_encoded = data.get("price")
        price_decoded = decode_decimal(price_encoded)
        row = {
            "id": row_id,
            "name": data.get("name"),
            "description": data.get("description"),
            "price": float(price_decoded) if price_decoded is not None else None,
        }
        transformed_data.append(row)

    # Write to JSONL
    temp_file = NamedTemporaryFile(delete=False, mode='w', suffix=".jsonl")
    for row in transformed_data:
        temp_file.write(json.dumps(row) + "\n")
    temp_file.close()

    ti.xcom_push(key='bq_data_file_path', value=temp_file.name)
    print(f"✅ Wrote {len(transformed_data)} clean rows to: {temp_file.name}")

# DAG definition
with DAG(
    dag_id='debezium_to_bigquery',
    start_date=datetime(2025, 4, 16),
    schedule_interval=None,
    catchup=False,
    tags=['debezium', 'kafka', 'bigquery'],
) as dag:

    consume_kafka = PythonOperator(
        task_id='consume_from_kafka',
        python_callable=consume_from_kafka,
        op_kwargs={
            'kafka_conn_id': 'kafka_default',
            'topic_name': 'inventory.inventory.products',
            'batch_size': 10,
        },
    )

    check_messages = PythonSensor(
        task_id='check_for_messages',
        python_callable=check_kafka_messages,
        poke_interval=30,
        timeout=600,
        mode='poke',
    )

    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )

    load_bigquery = BashOperator(
        task_id='load_to_bigquery',
        bash_command="""
export GOOGLE_APPLICATION_CREDENTIALS="/Users/aditya/airflow/cdc-project-456902-8eefa07b5d9e.json"
bq --project_id=cdc-project-456902 load \
  --source_format=NEWLINE_DELIMITED_JSON \
  --replace=false \
  --schema=id:INTEGER,name:STRING,description:STRING,price:NUMERIC \
  data_warehouse.products_cdc \
  "{{ ti.xcom_pull(task_ids='transform_data', key='bq_data_file_path') }}"
""",
    )

    consume_kafka >> check_messages >> transform >> load_bigquery