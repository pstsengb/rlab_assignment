pipeline {
  agent none
  stages {
  

    stage('rlab assignment') {
      agent {
        docker {
          image 'ros2_x86_no_gpu:latest'
          args "${MOUNT_DIRS}"
        }
      }
      
      options {
        skipDefaultCheckout()
      }
    
      steps {
        
        sh '''#!/bin/bash
            source /usr/share/gazebo/setup.sh 
            source /ws_test/install/setup.bash
            if [ -f /tmp/.X1-lock ]; then export DISPLAY=:1.0; else  Xvfb :1 -screen 0 800x600x24  & export DISPLAY=:1.0; fi
            launch_test /ws_test/src/integration_gazebo_test/test/launch_odom_test.py
            '''

      }
      post {
        always {
          sh 'pwd; ls -l'
        }
      }      
    }

  }// Stages
  environment {
    MOUNT_DIRS = ' -v /tmp/.X11-unix:/tmp/.X11-unix:rw  -v /var/run/docker.sock:/var/run/docker.sock'
    CI = true
  }
  options {
    buildDiscarder(logRotator(numToKeepStr: '5', artifactDaysToKeepStr: '30'))
    timeout(time: 120, unit: 'MINUTES')
  }
}
