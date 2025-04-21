#!/bin/bash

# Script to create Debezium CDC Topic for Products Table

kafka-topics.sh --create \
  --topic inventory.inventory.products \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1
