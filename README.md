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
* Following video shows that when execute the docker compose  
<img src="https://github.com/pstsengb/Image_for_repository/blob/main/jenkin_use/nv2_test_video.gif" width="500" height="300"/>

> The workflow of the robot movement and check method:
> 
> 1. give the robot initial pose
> 
> 2. robot start to movement ,the robot will go to 1,2,3,4 point (it will make the path form a rectangle)
> 
> 3. this 4 point can used to inspect the diagonal line a,b (a,b lenght in rectangular shape should very close)
>
<img src="https://github.com/pstsengb/Image_for_repository/blob/main/jenkin_use/rectangular_check.png" width="400" height="200"/>

## jenkin setting
1.jenkinsfile is ready

2.Please refer this instructions for Jenkins setting the pipline  [jenkins_for_ros](https://github.com/pstsengb/jenkins_for_ros)
