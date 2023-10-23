import pytest
import rclpy
import time
import math
import numpy as np
import geometry_msgs
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from geometry_msgs.msg import PoseWithCovarianceStamped

class CmdPubSystem(Node):

    def __init__(self):
        super().__init__('pub_cmd_and_sub_odom')
        self.state = 'standBy'
        self.distance_L = 1.5
        self.distance_S = 1.0
        self.pi = math.pi
        self.odom_current = None
        self.odom_pervious = None
        self.record_position = {}  # record the 4 robot position for calculate the result
        self.point_count = 0 # record count of robot point movement 
        self.cmd_publisher = self.create_publisher(Twist, 'cmd_vel', 2)
        self.initialpose_publisher = self.create_publisher(PoseWithCovarianceStamped, 'initialpose', 1)
        self.odom_subscription = self.create_subscription(Odometry,'odom',self.odomCb,1)
        self.amclpose_subscription = self.create_subscription(PoseWithCovarianceStamped,'amcl_pose',self.amclposeCb,1)
        self.initial_received = False
        self.odom_received = False
        timer_period = 0.05  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)


    def odomCb(self, msg):
        self.odom_current = msg
        self.odom_received = True


    def setPerviousOdom(self):
        self.odom_pervious = self.odom_current


    def claculateOdomDiff(self):
        x_diff = self.odom_current.pose.pose.position.x - self.odom_pervious.pose.pose.position.x
        y_diff = self.odom_current.pose.pose.position.y - self.odom_pervious.pose.pose.position.y
        dis = math.hypot(x_diff, y_diff)
        #self.get_logger().warn('dis:%.2f' % dis) 
        return dis


    def claculateRotation(self):

        quaternion = self.odom_current.pose.pose.orientation
        x = quaternion.x
        y = quaternion.y
        z = quaternion.z
        w = quaternion.w
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (w * y - z * x)
        pitch = np.arcsin(sinp)

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)

        convert_yaw = yaw
        if(yaw<0.0):
            diff_yaw = yaw + self.pi
            convert_yaw = self.pi + diff_yaw

        #self.get_logger().info("convert_yaw:%.3f" % convert_yaw)
        return convert_yaw


    def recordPosition(self):
        self.record_position.update({self.point_count:[self.odom_current.pose.pose.position.x,self.odom_current.pose.pose.position.y]})
        self.point_count += 1


    def executeStop(self):
        move_cmd = Twist()
        move_cmd.linear.x = 0.0
        move_cmd.angular.z = 0.0
        self.cmd_publisher.publish(move_cmd)


    def executeForward(self):
        move_cmd = Twist()
        move_cmd.linear.x = 0.3
        self.cmd_publisher.publish(move_cmd)


    def executeRotate(self):
    	move_cmd = Twist()
    	move_cmd.angular.z = 0.4
    	self.cmd_publisher.publish(move_cmd)



    def pubInitialPose(self):
        initial_pose = PoseWithCovarianceStamped()
        initial_pose.header.frame_id = 'map'
        initial_pose.pose.pose.position.x = -1.9626833435179696
        initial_pose.pose.pose.position.y = -0.629841014391754
        initial_pose.pose.pose.orientation.x = 0.0
        initial_pose.pose.pose.orientation.y = 0.0
        initial_pose.pose.pose.orientation.z = 0.006029300345852586
        initial_pose.pose.pose.orientation.w = 0.9999818236034791
        self.initialpose_publisher.publish(initial_pose)


    def amclposeCb(self,msg):
        self.initial_received = True


    def calculate_result(self):

        firstline_x_diff = self.record_position[1][0] - self.record_position[3][0]
        firstline_y_diff = self.record_position[1][1] - self.record_position[3][1]
        firstline_length = math.hypot(firstline_x_diff, firstline_y_diff)
        secondline_x_diff = self.record_position[2][0] - self.record_position[4][0]
        secondline_y_diff = self.record_position[2][1] - self.record_position[4][1]
        secondline_length = math.hypot(secondline_x_diff, secondline_y_diff)

        self.get_logger().info('firstline_length:%.3f' % firstline_length)
        self.get_logger().info('secondline_length:%.3f' % secondline_length)

        if(abs(firstline_length - secondline_length)<0.15):
            assert True
        else:
            assert False




    def timer_callback(self):

        if self.odom_received:
            #self.get_logger().info(self.state)

            if(self.state == 'standBy'):
                if(not self.initial_received):
                    self.pubInitialPose()
                else:
                    self.state = 'moveforward_L'
                    self.setPerviousOdom()

            elif(self.state == 'moveforward_L'):
                move_dis = self.claculateOdomDiff()
                if(move_dis <=  self.distance_L):
                    self.executeForward()
                else:
                    self.executeStop()
                    self.recordPosition()
                    if(self.point_count == 2):
                        self.state = 'Rotate_1.57'
                    elif(self.point_count == 4):
                        self.state = 'Rotate_4.71'

            elif(self.state == 'moveforward_S'):
                move_dis = self.claculateOdomDiff()
                if(move_dis <=  self.distance_S):
                    self.executeForward()
                elif(self.point_count == 5):
                    self.executeStop()
                    self.state = 'Finish'
                    self.calculate_result()
                else:
                    self.executeStop()
                    self.recordPosition()
                    if(self.point_count == 3):
                        self.state = 'Rotate_3.14'

            elif(self.state == 'Rotate_1.57'):
                angle = self.claculateRotation()
                if(angle < 1.57 or angle > 6.21):
                    self.executeRotate()
                else:
                    self.executeStop()
                    self.state = 'moveforward_S'
                    self.setPerviousOdom()

            elif(self.state == 'Rotate_3.14'):
                angle = self.claculateRotation()
                if(angle < 3.141):
                    self.executeRotate()
                else:
                    self.executeStop()
                    self.state = 'moveforward_L'
                    self.setPerviousOdom()

            elif(self.state == 'Rotate_4.71'):
                angle = self.claculateRotation()
                if(angle < 4.712):
                    self.executeRotate()
                else:
                    self.executeStop()
                    self.state = 'moveforward_S'
                    self.setPerviousOdom()     

        else:
            pass
            #self.get_logger().info('Waiting for odom data')


def main(args=None):
    rclpy.init(args=args)
    cmdpub = CmdPubSystem()
    executor = MultiThreadedExecutor()
    executor.add_node(cmdpub)
    while rclpy.ok():
        if(cmdpub.state=="Finish"):
            print('Done') #TestGoodProcess can not get ros log
            break
        executor.spin_once(timeout_sec=0.1)
    
if __name__ == '__main__':
    main()


