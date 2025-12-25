#!/bin/bash
echo "=================================="
echo "Testing Endpoints After Nginx Reload"
echo "=================================="
echo ""

BASE_URL="https://40.81.235.65"

echo "1. Testing /airflow-be/api/health"
curl -s -k "${BASE_URL}/airflow-be/api/health" | head -3
echo ""
echo ""

echo "2. Testing /airflow-be/api/discovery"
curl -s -k "${BASE_URL}/airflow-be/api/discovery?page=0&size=5" | head -5
echo ""
echo ""

echo "3. Testing /airflow-be/api/discovery/stats"
curl -s -k "${BASE_URL}/airflow-be/api/discovery/stats"
echo ""
echo ""

echo "4. Testing /airflow-be/api/discovery/trigger (POST)"
curl -s -k -X POST "${BASE_URL}/airflow-be/api/discovery/trigger"
echo ""
echo ""

echo "=================================="
