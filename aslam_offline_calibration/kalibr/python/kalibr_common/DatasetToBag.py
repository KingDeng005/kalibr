import os
import sys
import time
import argparse
import numpy as np
import signal
from dataset_store import Dataset

import cv2
import rospy
import rosbag
from cv_bridge import CvBridge
from sensor_msgs.msg import Image 
from sensor_msgs.msg import Imu


# make numpy print prettier
np.set_printoptions(suppress=True)

def signal_exit(signal, frame):
    sys.exit(1)

#helper to constrain certain arguments to be specified only once
class Once(argparse.Action):
    def __call__(self, parser, namespace, values, option_string = None):
        if getattr(namespace, self.dest) is not None:
            msg = '{o} can only be specified once'.format(o = option_string)
            raise argparse.ArgumentError(None, msg)
        setattr(namespace, self.dest, values)

def parseArgs():
    class KalibrArgParser(argparse.ArgumentParser):
        def error(self, message):
            self.print_help()
            sm.logError('%s' % message)
            sys.exit(2)
        def format_help(self):
            formatter = self._get_formatter()
            formatter.add_text(self.description)
            formatter.add_usage(self.usage, self._actions,
                                self._mutually_exclusive_groups)
            for action_group in self._action_groups:
                formatter.start_section(action_group.title)
                formatter.add_text(action_group.description)
                formatter.add_arguments(action_group._group_actions)
                formatter.end_section()
            formatter.add_text(self.epilog)
            return formatter.format_help()
    
    usage = """ 
    Example usage:
    python %(prog)s --dataset 2019-12-18-14-37-11 --begin "00:10:00"  --cam_topics /camera1/image_color/compressed  --imu_topics /xsens_driver/imupos --out_path ../../../
    """

    #setup the argument list
    parser = KalibrArgParser(description="Convert dataset to rosbag",usage=usage)

    #dataset source
    groupData = parser.add_argument_group("Dataset")
    groupData.add_argument('--dataset',dest='dataset_name',nargs=1,help='Dataset name containing camera and imu data',action=Once, required=True)
    groupData.add_argument('--begin',dest='begin',nargs=1,help ="begin timestamp",action=Once, required=True)
    groupData.add_argument('--end',dest='end',default="-0",nargs=1,help="end timestamp",action=Once, required=False)

    #configuration files
    groupTopic = parser.add_argument_group("Topic")
    groupTopic.add_argument('--cam_topics',nargs='+',dest='cam_topics',help='camera topic in dataset',action=Once, required=True)
    groupTopic.add_argument('--imu_topics',nargs='+',dest='imu_topics',help='imu topics in dataset',action=Once, required=True)

    #output
    groupOutput = parser.add_argument_group("Output")
    groupOutput.add_argument("--out_path",dest='out_path',nargs=1,help='output rosbag path')

    #print help if no argument is specified
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(2)

    #Parser the argument list
    try:
        parsed = parser.parse_args()
    except:
        sys.exit(2)

    return parsed

class DatasetConverter(object):

    def __init__(self,dataset_name,cam_topics,imu_topics,out_path):
        
        #setup param
        self.bridge = CvBridge()
        self.dataset = dataset_name[0]
        self.cam_topics = list(cam_topics)
        self.imu_topics = list(imu_topics)
        self.convert_topics = self.cam_topics+self.imu_topics
        self.out_path = os.path.join(os.path.dirname(__file__),
            out_path)
        if not os.path.exists(self.out_path):
            os.makedirs(self.out_path)

        self.bag = rosbag.Bag(self.out_path+"{}.bag".format(self.dataset),'w',
                                compression = rosbag.Compression.NONE)
        #open dataset
        try:
            self.ds = Dataset.open(self.dataset)
        except Exception as e:
            print("Cannot open bag: {}".format(self.dataset))
            raise Exception(e)
    
    def convert(self,begin=None,end=None,limit=None):
        begin = 0 if begin is None else begin
        end = '-0' if end is None else end
        for topic in self.convert_topics:
            print("******************************************************")
            print("Start convert {}".format(topic))
            for ts,msgs in self.ds.fetch(topic,ts_begin=begin,ts_end=end,limit=limit):
                
                if "image_color/compressed" in topic:
                    #convert compressed to color and resize image
                    img_np = cv2.imdecode(np.fromstring(msgs.data,np.uint8),cv2.IMREAD_COLOR)
                    #resize image
                    if img_np.shape[1] ==2048:
                        img_np = cv2.resize(img_np,(1024,576))
                    if img_np.shape[1] ==1920:
                        img_np = cv2.resize(img_np,(960,540))
                    img_ros = self.bridge.cv2_to_imgmsg(img_np,"bgr8")
                    img_ros.header.stamp = msgs.header.stamp
                    self.bag.write(topic[:-11],img_ros,t=msgs.header.stamp)
        
                if "xsens_driver/imupos" in topic:
                    #convert xsens_msgs/IMUDATA to sensor_msgs/Imu
                    rosimu = Imu()
                    rosimu.header.stamp = msgs.header.stamp
                    rosimu.angular_velocity.x = msgs.gyrx
                    rosimu.angular_velocity.y = msgs.gyry
                    rosimu.angular_velocity.z = msgs.gyrz

                    rosimu.linear_acceleration.x = msgs.accx
                    rosimu.linear_acceleration.y = msgs.accy
                    rosimu.linear_acceleration.z = msgs.accz
                    self.bag.write(topic,rosimu,t=msgs.header.stamp)
            print("save {} successful!!!".format(topic))
        print("Convert finished!!!")
        self.bag.close()

    def topic_check(self):
        topic_list = list(self.ds.list_topics())
        for topic in self.convert_topics:
            if topic not in topic_list:
                print("Cannot find topic {} in bag {}".format(topic,self.dataset))
                sys.exit()
        print("Topic Check successful!!! ")

def main():
    # Parse the arguments
    parsed = parseArgs()

    signal.signal(signal.SIGINT, signal_exit)
    #init converter
    bag_converter = DatasetConverter(parsed.dataset_name,parsed.cam_topics,parsed.imu_topics,parsed.out_path[0])
    #check topic
    bag_converter.topic_check()
    #run 
    bag_converter.convert(begin=parsed.begin[0])


if __name__ == "__main__":
    main()


