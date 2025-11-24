pipeline {
    agent any

    environment {
        REGISTRY = "claudiocabrera/notas-entregable4"
        IMAGE_TAG = "latest"
    }

    stages {

        stage('Clonar repositorio') {
            steps {
                checkout scm
            }
        }

        stage('Semgrep analysis') {
            agent {
                docker {
                    image 'returntocorp/semgrep'
                }
            }
            steps {
                sh '''
                    semgrep --config auto --json --output semgrep-report.json || true
                '''
            }
        }

        stage('Snyk scan') {
            agent {
                docker {
                    image 'snyk/snyk-cli'
                }
            }
            environment {
                SNYK_TOKEN = credentials('snyk-token')
            }
            steps {
                sh '''
                    snyk auth $SNYK_TOKEN
                    snyk test --file=requirements.txt --package-manager=pip --severity-threshold=high
                '''
            }
        }

        stage('Build & Test Python') {
            agent {
                docker {
                    image 'python:3.10'
                }
            }
            steps {
                sh '''
                    python -m py_compile app.py
                '''
            }
        }

        stage('Build & Push Docker image') {
            agent {
                docker {
                    image 'docker:24.0'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            environment {
                DOCKERHUB = credentials('dockerhub')
            }
            steps {
                sh '''
                    docker build -t $REGISTRY:$IMAGE_TAG .
                    echo "$DOCKERHUB_PSW" | docker login -u "$DOCKERHUB_USR" --password-stdin
                    docker push $REGISTRY:$IMAGE_TAG
                '''
            }
        }

        stage('Deploy with Helm') {
            agent {
                docker {
                    image 'alpine/helm:3.13.0'
                    args '-v /root/.kube:/root/.kube'
                }
            }
            steps {
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
            echo "❌ Pipeline falló."
        }
    }
}
