node{
	stage('Git Hub Checkout'){
		git credentialsId: 'b255cf65-b055-4120-be88-1a4264f5caca', url: 'https://github.com/robertreden24/FlaskWebApp'}
	}
	stage('Build Docker Image'){
		sh
	}
	stage('Push Docker Image Into Docker Hub'){
		withCredentials([string(credentialsId: '6bba230b-a065-440c-a9eb-9ea4c291ecb2', variable: 'Docker_Password')]) {
			    // some block
		}
	}
}