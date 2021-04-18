#! groovy

pipeline {
    environment {

        if (env.BRANCH_NAME == 'develop') {
                image_name = "restbase/restbase-server"
            }
            if ((env.BRANCH_NAME == 'master') || (env.BRANCH_NAME == 'main')){
                image_name = "restbase/restbase-server"
            }
            else {
                image_name = "restbase/restbase-server-dev"
            }
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
                script {
                    dockerImage = docker.build image_name
                }
            }
            }

        stage("Push to dockerhub"){
            steps{
                script{
                    version = readFile "VERSION"
                    docker.withRegistry('https://index.docker.io/v1/', registryCredential ) {
                        if (env.BRANCH_NAME == 'develop') {
                            dockerImage.push(version)
                        }
                        if ((env.BRANCH_NAME == 'master') || (env.BRANCH_NAME == 'main')){
                            dockerImage.push(version)
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
