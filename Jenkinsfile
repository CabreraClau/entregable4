pipeline {
    agent any

    environment {
        REGISTRY = "claudiocabrera/notas-entregable4"
        IMAGE_TAG = "latest"

        
        DOCKER_USERNAME = credentials('dockerhub').username
        DOCKER_PASSWORD = credentials('dockerhub').password
    }

    stages {

        stage('Clonación del repositorio') {
            steps {
                checkout scm
                echo 'Repositorio clonado correctamente.'
            }
        }

        stage('Análisis estático con Semgrep') {
            steps {
                echo 'Ejecutando Semgrep...'
                sh '''
                semgrep --config auto --json --output semgrep-report.json notas-app/ || true
                '''
            }
            post {
                failure {
                    error("❌ Semgrep falló. Deteniendo pipeline.")
                }
            }
        }

        stage('Escaneo de vulnerabilidades con Snyk') {
            steps {
                echo 'Ejecutando Snyk...'
                sh '''
                snyk test --file=requirements.txt --severity-threshold=high
                '''
            }
        }

        stage('Construcción y test de la aplicación') {
            steps {
                echo 'Validando Python app...'
                sh '''
                python3 -m py_compile notas-app/app.py
                '''
            }
        }

        stage('Build y Push de Docker Image') {
            steps {
                echo 'Construyendo imagen Docker...'
                sh '''
                docker build -t $REGISTRY:$IMAGE_TAG .
                docker login -u "$DOCKER_USERNAME" -p "$DOCKER_PASSWORD"
                docker push $REGISTRY:$IMAGE_TAG
                '''
            }
        }

        stage('Despliegue en Kubernetes con Helm') {
            steps {
                echo 'Desplegando en Kubernetes...'
                sh '''
                helm upgrade --install notas entregable4-chart \
                --set image.repository=$REGISTRY \
                --set image.tag=$IMAGE_TAG
                '''
            }
        }

    }

    post {
        success {
            echo "✔ Pipeline finalizado con éxito."
        }
        failure {
            echo "❌ Hubo un error en el pipeline."
        }
    }
}
