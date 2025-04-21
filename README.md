# Real-Time Change Data Capture

<br>

## 📖 About the Project
This project implements a **Real-Time Change Data Capture (CDC) Pipeline** that captures **database changes** from a **MySQL** server using **Debezium**, streams them through **Apache Kafka**, processes them with **Apache Airflow**, and finally loads the transformed data into **Google BigQuery** for real-time analytics.  
The entire setup runs **natively without Docker**, providing a deeper understanding of service orchestration, authentication, and cloud integration.

<br>

## 🚀 Technologies Used

![MySQL](https://img.shields.io/badge/Database-MySQL-blue?logo=mysql&logoColor=white)  
![Debezium](https://img.shields.io/badge/CDC-Debezium-red?logo=debezium&logoColor=white)  
![Apache Kafka](https://img.shields.io/badge/Stream-Apache%20Kafka-000000?logo=apachekafka&logoColor=white)  
![Apache Airflow](https://img.shields.io/badge/Orchestration-Apache%20Airflow-017CEE?logo=apacheairflow&logoColor=white)  
![Google BigQuery](https://img.shields.io/badge/Analytics-Google%20BigQuery-4285F4?logo=googlebigquery&logoColor=white)  
![Python](https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white)

<br>

## 🛠  Project Structure
```
cdc-project/
├── airflow/               # Airflow configuration and DAGs
│   └── dags/
│       └── debezium_to_bigquery.py
├── airflow_setup/          # Setup instructions for Airflow connections
│   └── airflow_connections.md
├── kafka/                  # Kafka and Debezium configuration
│   ├── config/
│   ├── create_topics.sh
│   ├── register-mysql.json
│   ├── LICENSE
│   ├── NOTICE
│   ├── plugins/
│   └── licenses/
├── mysql_setup/            # MySQL initialization scripts
│   └── init.sql
├── requirements.txt        # Python and Airflow dependencies
├── .gitignore
└── README.md
```

<br>


## 🚀 How to Set Up and Run

### 1. Install Requirements

```
python3 -m venv airflow-venv
source airflow-venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup MySQL Database

```
mysql -u root -p < mysql_setup/init.sql
```

### 3. Start Kafka and Zookeeper
```
# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka Broker
bin/kafka-server-start.sh config/server.properties

# Start Kafka Connect Distributed Worker
bin/connect-distributed.sh config/connect-distributed.properties
```
### 4. Create Kafka Topic
```
cd kafka/
bash create_topics.sh
```

### 5. Register Debezium Connector for MySQL
```
curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" \
--data @register-mysql.json \
http://localhost:8083/connectors/
```

### 6. Setup and Start Airflow
```
cd airflow
airflow db init
airflow standalone
```

### 7. Setup Kafka and Big Query Connections
In Airflow UI:
	•	Go to Admin → Connections and add:


Kafka Connection:

	Conn ID: kafka_default
	Conn Type: Kafka
	Host: localhost:9092

Google Cloud Connection:

	Conn ID: google_cloud_default
	Conn Type: Google Cloud
	Set Project ID
	Upload your service account JSON credentials

### 8. Trigger the DAG
	Unpause the DAG: debezium_to_bigquery
	Trigger the DAG manually

✅ The flow:
	Kafka messages consumed ➔
	Decoded and transformed ➔
	Data loaded into BigQuery.

<br>

## 🧩 Challenges Faced
 
### Environment Setup without Docker
  •	Setting up MySQL, Kafka, Debezium, and Airflow locally on macOS without Docker required careful manual configuration of ports, services, and dependencies.
### Airflow BigQuery Load Errors
  •	Encountered schema mismatch errors (e.g., Field id has changed mode from REQUIRED to NULLABLE) and decoding failures for base64-encoded price values.
### Google Cloud Authentication with Airflow
  •	Had to manually configure Application Default Credentials (ADC) so that Airflow workers could access BigQuery APIs within isolated venv environments.
### Kafka Connector Management
  •	Registered Debezium Kafka connectors manually via REST APIs, handling snapshot configurations and schema histories without graphical interfaces.
### Handling Large Kafka Batches
  •	Needed to carefully manage XCom data transfer sizes and generate temporary JSONL files to prevent memory crashes (exit code -9) during Airflow task execution.

<br>

## 🏆 Project Outcomes

### End-to-End Real-Time CDC Pipeline Built
  •	Successfully captured real-time database changes from MySQL and streamed them through Debezium ➔ Kafka ➔ Airflow ➔ BigQuery.
### Manual Native Installation
  •	Set up all services without Docker, gaining a strong low-level understanding of service orchestration and local environment management.
### BigQuery Data Load Optimizations
  •	Designed a clean ingestion pipeline with type-safe BigQuery inserts (handling NUMERIC fields and nullable columns correctly).
### Production-Ready Project Structure
  •	Organized the repository with Airflow DAGs, Kafka scripts, MySQL initialization scripts, and detailed documentation for easy setup.

<br>

## 📚 Learnings

### Debezium Internals and CDC Concepts
  •	Gained in-depth understanding of snapshot vs binlog events, Debezium source metadata, and message structures (op, source, ts_ms, etc.).
### Kafka Consumer Patterns
  •	Practiced reliable consumption patterns in Kafka, including safe deserialization and batch management using kafka-python.
### Airflow Best Practices
  •	Learned advanced Airflow concepts like PythonSensor, dynamic temporary files, XCom usage, and BashOperator scripting for BigQuery ingestion.
### Troubleshooting Skills
  •	Solved real-world issues related to credential management, fatal task crashes, schema mismatch errors, and environment variable loading.
### Cloud Integration
  •	Developed hands-on experience authenticating, querying, and loading data into Google BigQuery from a locally orchestrated pipeline.
