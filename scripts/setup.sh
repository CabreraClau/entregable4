#!/bin/bash

set -e


echo "Iniciando entorno completo"


NAMESPACE="default"
GRAFANA_POD=""
GRAFANA_PORT=3000
APP_PORT=5000

echo "Actualizando repositorios Helm "
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update


echo "Instalando Prometheus"
helm install monitoring prometheus-community/kube-prometheus-stack -n $NAMESPACE

echo "Esperando que Prometheus y Grafana estén arriba"
sleep 40


echo "Instalando Grafana (si no viene del operator)"
helm upgrade --install grafana grafana/grafana \
  --set adminPassword=admin \
  --set service.type=ClusterIP \
  -n $NAMESPACE

echo "Esperando pod de Grafana..."
sleep 25


echo "Buscando pod de Grafana..."
GRAFANA_POD=$(kubectl get pod -n $NAMESPACE -l "app.kubernetes.io/name=grafana" -o jsonpath="{.items[0].metadata.name}")
echo " Grafana Pod: $GRAFANA_POD"


echo "Instalando aplicación app-notas con Helm"
helm upgrade --install notas ./entregable4-chart


echo "Esperando que la app esté disponible..."
sleep 20


echo "Creando ServiceMonitor..."
kubectl apply -f k8s/servicemonitor.yaml


echo "Generando tráfico automático hacia la aplicación..."
APP_SVC=$(kubectl get svc -n $NAMESPACE -l "app=notas" -o jsonpath="{.items[0].metadata.name}")

echo "  Nombre del servicio: $APP_SVC"

for i in {1..40}
do
  kubectl run curl-test-$i --rm -i --image=busybox --restart=Never -- \
    wget -qO- http://$APP_SVC:$APP_PORT > /dev/null
  echo "     → Request #$i enviada"
done


echo "Exportando dashboard hacia Grafana..."

kubectl port-forward svc/grafana $GRAFANA_PORT:80 -n $NAMESPACE &

sleep 5

echo "Importando dashboard JSON..."
curl -X POST \
  -H "Content-Type: application/json" \
  -d @"grafana/dashboard.json" \
  http://admin:admin@localhost:$GRAFANA_PORT/api/dashboards/db

echo " Dashboard importado correctamente."



echo "Todo el entorno fue inicializado"
echo "   Prometheus + Grafana + App + Dashboard"


