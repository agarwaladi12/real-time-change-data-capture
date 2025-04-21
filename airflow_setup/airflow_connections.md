# Airflow Connection Setup Guide

## Kafka Connection

- Conn ID: `kafka_default`
- Conn Type: `Kafka`
- Host: `localhost:9092`
- No Authentication

## Google Cloud Connection

- Conn ID: `google_cloud_default`
- Conn Type: `Google Cloud`
- Project ID: `your-gcp-project-id`
- Keyfile Path: `/path/to/your/credentials.json`
- Scopes: Leave blank (default)
