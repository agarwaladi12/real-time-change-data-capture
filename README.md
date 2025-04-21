# MySQL → Debezium → Kafka → Airflow → BigQuery CDC Pipeline

This project demonstrates a **Change Data Capture (CDC)** pipeline built **without Docker**.  
We capture MySQL database changes using **Debezium**, stream them into **Kafka**, consume and transform the data with **Apache Airflow**, and finally load the clean data into **Google BigQuery**.

<br>

## ✨ Tech Stack

- **MySQL** — Source database
- **Debezium** — Captures CDC events from MySQL
- **Apache Kafka** — Event streaming platform
- **Apache Airflow** — Orchestrator for CDC pipeline
- **Google BigQuery** — Data warehouse (final destination)

<br>
## 🛠  Project Structure
cdc-project/
├── airflow/                 # Airflow config and DAGs
│   └── dags/
│       └── debezium_to_bigquery.py
├── airflow_setup/            # Setup steps for Airflow
│   └── airflow_connections.md
├── kafka/                    # Kafka + Debezium configs
│   ├── config/
│   ├── create_topics.sh
│   ├── register-mysql.json
│   ├── LICENSE
│   ├── NOTICE
|   ├── plugins
│   └── licenses/
├── mysql_setup/              # MySQL initialization scripts
│   └── init.sql
├── requirements.txt          # Python and Airflow dependencies
├── .gitignore
└── README.md

<br>

---

## 🚀 How to Set Up and Run

### 1. Install Requirements

```bash
python3 -m venv airflow-venv
source airflow-venv/bin/activate
pip install -r requirements.txt

### 2. Setup MySQL Database

mysql -u root -p < mysql_setup/init.sql

### 3. Start Kafka and Zookeeper

# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka Broker
bin/kafka-server-start.sh config/server.properties

# Start Kafka Connect Distributed Worker
bin/connect-distributed.sh config/connect-distributed.properties

### 4. Create Kafka Topic

cd kafka/
bash create_topics.sh

### 5. Register Debezium Connector for MySQL

curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" \
--data @register-mysql.json \
http://localhost:8083/connectors/

### 6. Setup and Start Airflow

cd airflow
airflow db init
airflow standalone
