#! groovy

pipeline {
    environment {
        image_name = "restbase/restbase-server"
        registryCredential = 'dockerhub'
        dockerImage = ''
    }

    agent any

    stages {
        
        stage("Tests"){
            steps{
                script{
                dir(path: 'tests') {
                        sh (
                            script: 'bash localtest.sh',
                        )
                    }
                }
            }
        }

        stage("Build docker image"){
            steps{
                dockerImage = docker.build image_name
            }
            }
            }
        }
    
        stage("Push to dockerhub"){
            steps{
                script{
                    docker.withRegistry('https://index.docker.io/v1/', registryCredential ) {
                        if ((env.BRANCH_NAME == 'master') || (env.BRANCH_NAME == 'main')){
                            dockerImage.push('latest')
                        }
                        else {
                            dockerImage.push(env.BRANCH_NAME)
                        }
                    }
                }
            }
        }

        stage("Clear"){
            steps{
                script{
                    sh 'docker rmi -f restbase/restbase-server'
                }
            }
        }
    }
}