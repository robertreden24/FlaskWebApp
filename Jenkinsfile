node{
	stage('Git Hub Checkout'){
		git credentialsId: 'b255cf65-b055-4120-be88-1a4264f5caca', url: 'https://github.com/robertreden24/FlaskWebApp'}
	}
	stage('Build Docker Image'){
		bat 'docker-compose up --build'
	}
	stage('Push Docker Image Into Docker Hub'){
		withCredentials([string(credentialsId: '6bba230b-a065-440c-a9eb-9ea4c291ecb2', variable: 'Docker_Password')]) {
			    // some block
			bat 'docker login -u robertreden24 -p ${Docker-Password}'
		}
		bat 'docker push'
	}
	stage('Deploymeny Into Azure'){
		bat """kubectl --kubeconfig=/Users/elizabethgirlang/.kube/config apply -f deployment-service.yaml"""
	}
}