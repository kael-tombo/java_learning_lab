pipeline {
    agent any
    tools {
        maven 'maven-3.9'
        jdk 'jdk-21'
    }
    options {
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }
    triggers {
        pollSCM('H/15 * * * *')
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Verify Tools') {
            steps {
                sh 'java -version'
                sh 'mvn -version'
            }
        }
        stage('Build Core Labs') {
            steps { sh 'mvn -f pom-aggregator.xml clean verify -B -V' }
        }
        stage('Build Full Reactor (no tests)') {
            steps { sh 'mvn -f pom.xml clean install -B -DskipTests=true' }
        }
    }
    post {
        always { junit allowEmptyResults: true, testResults: '**/target/surefire-reports/*.xml' }
        failure { echo 'Pipeline failed — see stage logs and surefire reports.' }
        success { echo 'Pipeline succeeded.' }
    }
}
