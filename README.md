# rlab_assignment
This repository deploy a simulation environment using docker and set up jenkins for automated testing. The testing scenario involves a robot moving in a rectangular pattern within the simulation environment, with the final result being tested.
## docker deployment
1. Clone the repository
```
git clone https://github.com/pstsengb/rlab_assignment
```
2. Go to the file and build the image (simulation environment use the navigation2)
```
cd rlab_assignment
docker build -t ros2_x86_no_gpu . -f Dockerfile_ros2_x86_no_gpu
```
3. Go to the docker file and run the docker compose (it will launch everything that including the simulation environment and test node)
```
cd rlab_assignment/docker
docker-compose -f docker-compose.yaml up
```
## jenkin setting
1.jenkinsfile is ready
2.Please refer this instructions for Jenkins setting the pipline  [jenkins_for_ros](https://github.com/pstsengb/jenkins_for_ros)
