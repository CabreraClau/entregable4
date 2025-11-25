# entregable4
Entregable para devops

##Punto 1
#Contenerización, Seguridad y Despliegue con Helm

Este proyecto implementa una aplicación Flask llamada notas, la cual es contenerizada, analizada por herramientas de seguridad (Trivy + Dive) y desplegada en Kubernetes mediante un Helm Chart.
#1. Contenerización de la aplicación
1.1 Construcción inicial

Primero se construyó la imagen:
```
docker build -t app-notas .

```
Pero observamos que dejaba el tag por defecto (latest):
```
REPOSITORY     TAG      SIZE
app-notas      latest   126MB

```
Por lo que se reconstruyó correctamente con un tag explícito:
```
docker build -t app-notas:1.0 .

```
Ahora sí:
```
REPOSITORY     TAG      SIZE
app-notas      1.0      126MB

```
Análisis de Vulnerabilidades con Trivy
```
trivy image app-notas:1.0

```
#Resultados del analisis
Resultados del análisis

Sistema operativo (Debian 13.2):

52 vulnerabilidades

-51 LOW
-1 MEDIUM
-0 HIGH
-0 CRITICAL

Dependencias Python:

Total: 8 vulnerabilidades
      1 HIGH
      → afecta a Flask-Cors 4.0.0
      → corregido en 4.0.2

      6 MEDIUM

      1 LOW

✔ Conclusiones

-No hay vulnerabilidades críticas.
-El nivel de riesgo es aceptable para entornos controlados.
-La única vulnerabilidad "HIGH" se resuelve actualizando Flask-Cors.
-El resto proviene de librerías del sistema base Debian y no afectan directamente la app.

#Análisis de la Imagen con Dive

Se instaló Dive:
```
choco install dive

```
Se analizó la imagen:
```
dive app-notas:1.0

```


La imagen NO ejecuta procesos como root, ya que usamos:

```
USER appuser
```
Se utilizó la herramienta **Dive** para inspeccionar la imagen `app-notas:1.0` y evaluar:

- Eficiencia de capas  
- Espacio desperdiciado  
- Buenas prácticas de construcción


```
| Métrica                                  | Resultado                    |
| ---------------------------------------- | ---------------------------- |
| **Tamaño total de la imagen**            | 126 MB                       |
| **Espacio potencialmente desperdiciado** | 5.6 MB                       |
| **Eficiencia general**                   |   **96%**                    |
| **Ejecución del proceso**                | ✔ No corre como root         |
| **Multi-stage build**                    | ✔ Implementado correctamente |

```
#Conclusion:
La imagen está correctamente optimizada.
Dive confirma que el build es eficiente, ya que:

Se usa multi-stage build → se instala todo en una etapa “builder” y se copia solo lo necesario a la imagen final.

El contenedor no ejecuta procesos como root. Se definió un usuario específico: USER appuser

Esto mejora la seguridad y sigue buenas prácticas recomendadas para contenedores productivos.

El espacio desperdiciado es mínimo
Un “wasted space” del 5%.

La estructura de capas es limpia y lógica, gracias a:
Instalaciones agrupadas en pocas capas (apt-get)
Creación del usuario en una capa separada
Copia limpia de la aplicación

#Despliegue en Kubernetes con Helm

Se creó un chart Helm:
```
helm create entregable4-chart

```
Luego se modificaron los valores:
```
image:
  repository: app-notas
  tag: "1.0"
  pullPolicy: IfNotPresent

app:
  port: 5000
  env: "dev"

service:
  type: ClusterIP
  port: 5000

```
Instalación:
```
helm install notas ./entregable4-chart

```
Verificacion:
```
kubectl get pods

```

```
```

##Punto 4
# Monitoreo con Prometheus, Grafana y Kubernetes

Este proyecto despliega la aplicación **notas** en Kubernetes utilizando **Helm** y agrega monitoreo con:

- **Prometheus Operator**
- **ServiceMonitor**
- **Grafana**

Incluye además un dashboard exportado en:  
 `/grafana/dashboard.json`

---

##  Requisitos previos

Asegurar de tener instalado:

- Docker  
- Kubernetes (Docker Desktop o Minikube)  
- kubectl  
- Helm 3  

Verificar el clúster:

```bash
kubectl get nodes
```

# 1. Instalar Prometheus Operator

Prometheus es una herramienta de monitoreo y alertas que se usa en enotrnos como kubernetes, microservicios y DevOps.

Desde la app exponemos métricas con prometheus_client, y gracias al ServiceMonitor, Prometheus puede descubrir automáticamente mi servicio y empezar a recolectarlas.

Agregar repositorio:
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

```
Instalar kube-prometheus-stack:

```bash
helm install monitoring prometheus-community/kube-prometheus-stack

```

Verificar:

```bash
helm install monitoring prometheus-community/kube-prometheus-stack

```

Se añadió un ServiceMonitor:

```
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: notas-servicemonitor
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app: entregable4-chart
  endpoints:
    - port: http
      path: /metrics
      interval: 10s

```
Prometheus detecta las métricas expuestas por la app mediante prometheus_client.

#2. Acceder a Grafana

Grafana se incluye automáticamente con kube-prometheus-stack.

Exponer el servicio:
```bash
kubectl port-forward -n default svc/monitoring-grafana 3000:80

```

# Desplegar la aplicación notas con Helm
```bash
helm upgrade --install notas-entregable4-chart ./entregable4-chart


```
Verificar el despliegue:
```bash
kubectl get pods


```
# . Verificar que Prometheus scrapea /metrics

Ver los ServiceMonitor disponibles:
```bash
kubectl get servicemonitors


```
Exponer Prometheus:
```bash
kubectl port-forward -n default svc/prometheus-operated 9090:9090


```

Abrir en navegador:

🔗 http://localhost:9090/targets

Debe aparecer algo como:
serviceMonitor/default/notas-servicemonitor
State: UP


Importar dashboard en Grafana

Ruta del archivo exportado:
/grafana/dashboard.json


. Comandos útiles

Ver logs de la app:
```
kubectl logs -l app=entregable4-chart
```

Ver servicios:
```
kubectl get svc
```

Eliminar la app:
```
helm uninstall notas-entregable4-chart
```

Eliminar Prometheus/Grafana:
```
helm uninstall monitoring
```

Estructura del proyecto:
```
entregable4-chart/
 ├── templates/
 │   ├── deployment.yaml
 │   ├── service.yaml
 │   ├── servicemonitor.yaml
 │   └── pvc.yaml
 ├── values.yaml
grafana/
 └── dashboard.json
 ```
#Resultado Final

La app expone métricas en /metrics
Prometheus las detecta con ServiceMonitor
Grafana muestra dashboards como:
RPS (requests per second)
Latencia por endpoint
Total de requests






