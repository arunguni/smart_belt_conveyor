# Smart Belt Conveyor
1.	Introduction
In this project, the design and working prototype of an IoT-based smart belt conveyor has been achieved using the Wokwi simulation platform, MQTT server, and Node-RED. MQTT protocol uses the Publisher subscriber concept for communication, using which data is collected from Wokwi and transferred over network to the Node-RED tool (Kashyap, Sharma and Verma, 2021). Node-RED on the other hand, is a visual tool based on flow-based programming that is used for developing IoT systems, which is used further to develop the user interface for monitoring this project smart belt conveyor (Clerissi et al., 2018). Developed system accurately and reliably collects data from multiple sensors like temperature, pressure and humidity, stores data in csv file, and also maintains the security of data by authenticating MQTT broker with unique Id.
2.	Updated System
2.1.	Updated system architecture
Updated System Architecture with integration of multiple sensors and motors for reliable data collection and actuation. Previously designed system included each of one temperature, pressure and humidity sensor, however, new updated includes three of each sensor and two of pir motion sensors. 
2.2.	Updates Description
For the accurate monitoring of the environmental conditions, the system has two additional temperature and humidity sensors (DHT22) and two pressure sensors (utilized from previously designed prototype in assignment 1). Also, the system is now equipped with two PIR motion detectors, which will be useful if one motion sensor fails to detect the product. For the optimized performance of the conveyor belt, an additional motor has been added to improve the overall power of the belt.
2.3.	Code Changes
To accommodate the additional sensors ,significant code changes has been performed. Some of the issues were encountered while updating the code, which are as follows:
•	Reading the data from multiple sensors introduced a huge latency, which in turn would decrease the overall product detection speed of the system.
•	As micropython doesn’t support multi-threading or multi-processing, no parallel processing could be done to avoid the introduced latency in product detection.
To address the above encountered issue, following approach were taken:
•	Read the data from the sensors every few seconds. The exact value can be defined by the system administrator from the code itself. It is recommended to be below 60 seconds.
•	Two infinity loops were utilized in the code to solve the above problems. The inner loop detects the products and rotates the motor for given time as mentioned above and exits the inner loop. The outer loop reads the data from the sensors and publishes the data to the network while the motor is stopped, so that no product is undetected during this latency period.

2.3.1.	Code Snippets and Explanation
The function that moves the motors is not changed despite using multiple motors, as same motor controller is used to provide motor movement instructions. Some additional variables are declared and initialized. These variables will be used to hold threshold data, instructions data, time, and some temporary values.
Code structure is as follows:
Outer loop {
	Read sensors data
	Inner loop { 
		If (Environmental conditions inside threshold) {
			Rotate motors
			Count products using pir motion detector
		}
		Else {
			Alert the user
		}
		If (defined seconds elapsed){
	Break this inner loop
}
}
Print and publish sensor and counted product data
}
3.	Designing and Building IoT Data Pipeline
3.1.	Data Pipeline Design
As Raspberry Pico Pi W is used for this project, it collects the data from the sensors, processes it and publishes it to the MQTT broker(HiveMQ) over the Wi-Fi. The published data is then read from the Node-RED by subscribing to the same topic(a2/conveyorbelt), which is further processed using nodes and sent to Node-RED dashboard/UI for real-time monitoring. Using csv and write file nodes, the collected data is then written into a file for data storing purpose.
3.2.	Building IoT Data Pipeline
3.2.1.	Setting up MQTT Broker
3.2.2.	Connecting to Network(Wokwi)
Updated attributes of Pico to work with Wi-Fi (ref. Module 3 Activity 3.2). 
main.py:
To connect with Wi-Fi network, network library was imported and “.connect” was executed to establish connection with the Wokwi-GUEST Wi-Fi. 
3.2.3.	Connecting to MQTT Broker and Publishing the Data from Wokwi Simulation
umqttsimple.py: (ref: Module 3, Activity 3.2)
To provide a secure connection to the MQTT broker, umqttsimple.py file is utilized which can be found in the projects used in the unit modules.
main.py
To establish connection with the MQTT broker successfully, MQTTClient was imported from umqttsimple. Then the required server parameters were initialized and passed to the MQTTClient. The connect() function was called to connect to the specified server.
After the connection, it is possible to publish data with the given topic to the connected broker server. In this project, a JSON object with some required information is published to the server with “a2/conveyorbelt” as the topic. 
3.2.4.	Connecting to MQTT Broker and getting data to Node-Red
“MQTT in” node is utilized to get data, which is published from the Wokwi simulation to the broker into the node-red for further processing and monitoring.
To connect with the MQTT-broker, required server information was entered as shown in the above two figures. This created a server is used in next step to subscribe and read the data.
After creating the server, created “mqtt” was selected from Server dropdown. The topic needs to be same as the topic mentioned in Wokwi simulation so that this node can read the data published in this topic i.e., a2/conveyorbelt.
3.2.5.	Processing and storing the data
The data comes through the MQTT IN node which is then converted to json object using the json node. Then the object is passed to both “showData” function node and “storeData” function node. The showData function processes the data to accurate format before passing it to the visualization nodes. The storeData function processes the data and passes it to the csv node to convert the json object data into csv formatted data. The csv formatted data is then appended to a file using the write file node i.e., storage.
json node:
showData function node:
Data in json format from json node is read and formatted into array of messages, which enables the use of multiple gauges and charts in node-RED dashboard for visual representation of collected data.
storeData function node:
Takes data in Json node in json format and stores it in message object and returns the msg object as the value of payload attribute.  
csv node:
Converts the incoming object data (msg.payload) into csv formatted data. 
storage write file node:
Storing data in “.csv” file using the write file node within the assigned path.
storage.csv
Data stored in “.csv” format and displayed using Ms Excel.
4.	User Interface Design
The user interface includes 14 different gauges and donuts to visualise data in Node-RED dashboard. At very first Belt status is displayed, followed by Total products. Total products are then visualised in bar chart. Products per minute, hour and day is visualised using donuts and line charts. For sensor data like Temperature, Pressure and Humidity, gauge and line chart are used for data visualization. 
Above figure shows the implementation of nodes for capturing data from broker and processing data for visualization in node-RED dashboard.
5.	Testing and Validation
Case Id	Test Cases	Expected Results	Remarks
1	Increasing the temperature to higher than given maximum threshold	Belt should stop, LED should turn on and the belt status and the temperature should be reflected in the node-red dashboard	Pass
2	Decreasing the humidity to the lower value than minimum humidity threshold	Belt should stop, LED should turn on and the belt status and the humidity should be reflected in the node-red dashboard	Pass
3	Increasing and decreasing the pressure data randomly within the threshold	Belt should not stop running. The change in the pressure data should be reflected in the dashboard	Pass
4	Simulating motion using both pir motion detectors	The product count should increase, and the data should be reflected in the dashboard	Pass
5	Simulating rapid motion using both pir motion detectors	The product count should increase rapidly, and the data should be reflected in the dashboard within given time	Pass
6	Simulating motion while the system is trying to publish collected data to MQTT broker	The motors should be stopped during this duration. Product count should not be affected. After, the publishing is completed the motors should start rotating for given duration and product count should increase if motion is detected	Pass
7	Simulating all three temperature sensors to have random value	The motors should stop, and the LED should turn on if a sensor data is outside normal threshold. The sensors data should be updated in node-red dashboard and the Belt Status should be updated as required	Pass
8	Simulating all three humidity sensors to have random value	The motors should stop, and the LED should turn on if a sensor data is outside normal threshold. The sensors data should be updated in node-red dashboard and the Belt Status should be updated as required	Pass
9	Simulating all three pressure sensors to have random value	The motors should stop, and the LED should turn on if a sensor data is outside normal threshold. The sensors data should be updated in node-red dashboard and the Belt Status should be updated as required	Pass
10	Checking if the published data to MQTT broker is being stored in a csv file	The published data should be accessed by the node-red and should be written to the csv file.	Pass

6.	Monitoring and Optimization
6.1.	Monitoring
6.1.1.	Realtime Data Monitoring(Node-RED)
Node-RED Dashboard is used to monitor real-time data from the system. Alert is also implemented by changing the gauge colours depending on the received data. For example: temperature gauges will turn yellow if the temperature data is below threshold and turn red if the temperature is above threshold. The alerting system is same for all environmental condition data.
The charts give insight into historical data of up to 1 hr. It helps to determine the environmental condition patterns with time.
6.1.2.	Data Logging(Node-RED)
Every received data is logged into a csv file. This data can help to detect any kind of anomalies in the system. It can also be analysed to improve the performance of the system.
6.1.3.	Broker Monitoring(HiveMQ)
As this system uses HiveMQ free cluster, there are not many tools available to monitor the health and performance of the system. However, some of the metrics can be viewed which can be useful.
Web Client can be a useful tool to monitor the incoming data to the broker. It helps to determine if the incoming data is in appropriate format and is reliable before sending it for processing.
6.2.	Optimization
•	While publishing and subscribing, QoS 0 is used to reduce the bandwidth usage and response speed of the system.
•	Data is published to the broker from the Wokwi simulation every given second (for now 5 seconds). It can be changed as required from the code. Rather than detecting changes and publishing. This approach is suitable for conveyor belt system since it allows the belt to rotate and detect objects faster for given amount of time.
•	Rather than publishing data from sensors separately, a single message in json format is published every time, which is then processed into appropriate data from node-red for visualization. This approach allows the system to spend minimal time uploading the data to the broker.
7.	Security, Scalability, Reliability and Performance
7.1.	Security
For security, MQTT broker is authenticated with unique Id and password.
7.2.	Scalability
The designed system is scalable in terms of data collection, data transmission and data processing. Multiple sensors can be integrated to collect more data which enhances the scalability of the system in Wokwi simulation for sensing data. The horizontal scaling in MQTT broker can handle more clients and eventually handle multiple loads of messages. Higher volume of data can be store in CSV file, however, a scalable database can be integrated in the system for handling high volume of data for long term storage. 
7.3.	Reliability
Due to the integration of multiple sensors and actuators, system is now more reliable in case of accurate data transmission. Failure in one sensor/actuator can be optimized by another.
7.4.	Performance
Overall, data from sensors are efficiently transferred over MQTT broker and visualised using node-RED dashboard giving accurate information and reliable performance. Whole system’s performance is accurate in terms of data capture and data transmission.
8.	Ethical Aspects
While developing and deploying a system like smart IoT belt conveyor, various ethical aspects are required to be considered. Some of the ethical aspects of this system are as follows:
•	In case of data collection, it is essential to collect only appropriate data as personal data of user operating the system should not be collected by the sensors, which eventually can breach privacy concerns if unattended.
•	Similarly, user/operator needs to be informed about any kind of surveillance within the system that might breach their privacy. 
9.	Conclusion
In conclusion, the updated Smart IoT-based Conveyor Belt system works smoothly giving an accuracy, reliability and efficiency in data collection and processing. Visual representation in node-RED as user interface, demonstrates the working of overall system and IoT data pipeline. Performed testing and validation also declares the effectiveness of the designed system. On the other hand, monitoring features of this system helps in keeping system UpToDate. Implementation of this system in real-life may need to have changes, however the flow and overall architecture will be similar in virtual and reality. 
