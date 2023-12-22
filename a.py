import rospy
from sensor_msgs.msg import Imu, BatteryState
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64
from message_filters import Subscriber, ApproximateTimeSynchronizer
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import TwistStamped
import requests
import time
import json
from utils import quaternion_to_euler, calculate_speed


def callback(imu_msg, battery_msg, rel_altitude_msg, position_msg, speed_sub):
    data_dict = {
        "takim_numarasi" : 1,
        "IHA_enlem": position_msg.latitude,
        "IHA_boylam": position_msg.longitude,
        "IHA_irtifa": rel_altitude_msg.data,
        "IHA_yonelme": imu_msg.orientation.x,
        "IHA_dikilme": imu_msg.orientation.y,
        "IHA_yatis": imu_msg.orientation.z,
        "IHA_hiz": calculate_speed(speed_sub.twist.linear.x, speed_sub.twist.linear.y, speed_sub.twist.linear.z),
        "IHA_batarya": int(battery_msg.percentage * 100),
        "IHA_otonom": 0
    }
    server_url = 'http://192.168.43.226:5000/update_data' 

    response = requests.post(server_url, json=data_dict)

    if response.status_code == 200:
        print(response.status_code)
        print(response.json())
    else:
        print(f"Hata: {response.status_code}")
    
    
    
def synchronize_topics():
    rospy.init_node('sync_node', anonymous=True)

    imu_sub = Subscriber('/mavros/imu/data', Imu)
    battery_sub = Subscriber('/mavros/battery', BatteryState)
    rel_altitude_sub = Subscriber('/mavros/global_position/rel_alt', Float64)
    position_sub = Subscriber('/mavros/global_position/global', NavSatFix)
    speed_sub = Subscriber('/mavros/local_position/velocity_local', TwistStamped)

    # ApproximateTimeSynchronizer to synchronize messages based on timestamps
    sync = ApproximateTimeSynchronizer(
        [imu_sub, battery_sub, rel_altitude_sub, position_sub, speed_sub],
        queue_size=10,
        slop=0.1,  # Adjust this parameter based on your message timestamp tolerances
        allow_headerless=True
    )
    sync.registerCallback(callback)

    rospy.spin()


if __name__ == '__main__':
    synchronize_topics()
   
   
