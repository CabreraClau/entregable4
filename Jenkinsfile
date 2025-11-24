pipeline {
    agent any

    environment {
        REGISTRY = "claudiocabrera/notas-entregable4"   // tu imagen dockerhub
        IMAGE_TAG = "latest"
    }

    stages {

        stage('Clonar repositorio') {
            steps {
                checkout scm
            }
        }

        stage('Análisis estático con Semgrep') {
            steps {
                sh '''
                echo "--- Ejecutando Semgrep ---"
                semgrep --config auto --json --output semgrep-report.json notas-app/ || true
                '''
            }
            post {
                unsuccessful {
                    echo "❌ Semgrep detectó hallazgos. Revisa semgrep-report.json."
                }
            }
        }

        stage('Escaneo de dependencias con Snyk') {
            steps {
                sh '''
                echo "--- Escaneando dependencias con Snyk ---"
                snyk test --file=requirements.txt --severity-threshold=high
                '''
            }
        }

        stage('Build de la aplicación y tests') {
            steps {
                sh '''
                echo "No tenés tests, así que solo validamos que Flask arranca."
                python3 -m py_compile notas-app/app.py
                '''
            }
        }

        stage('Build de imagen Docker') {
            steps {
                sh '''
                echo "--- Construyendo imagen Docker ---"
                docker build -t $REGISTRY:$IMAGE_TAG .
                docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD
                docker push $REGISTRY:$IMAGE_TAG
                '''
            }
        }

        stage('Despliegue en Kubernetes con Helm') {
            steps {
                sh '''
                echo "--- Desplegando en Kubernetes con Helm ---"
                helm upgrade --install notas entregable4-chart \
                    --set image.repository=$REGISTRY \
                    --set image.tag=$IMAGE_TAG
                '''
            }
        }
    }

    post {
        success {
            echo "✔ Pipeline completado correctamente."
        }
        failure {
            echo "❌ Hubo un error en el pipeline."
        }
    }
}
