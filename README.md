# URL Scan

'URL Scan' project is a design for a system, that would be able to accept multiple user request, that wish to analyse suspicious URLs,
Through a web service called urlscan.


## Description

The system was design to handle multiple request of users and output the result.

The result for each user request will be: 

* Page verdict (malicious or not)
* Page screenshot and a URL page 

All this while being able to scale, consider time limits quotas, and be efficient.

The main high level design diagram is as follows:

![alt text](https://github.com/arielmaslaton/URL_Scan/blob/master/Untitled%20Diagram.drawio.png?raw=true)


## Detailed Description
First I will elaborate on the actual flow while explaining some of the thoughts, considerations and alternatives, 
That I came across while designing the system.

Since on premise option was not overruled, two main approaches were considered.
An on premise option, and a cloud based solution such as AWS, Azure, google Cloud etc...

### Early design path
After thinking about what is the main purpose of the system, the complexity of the requirements, performance, efficiency,
I have chosen to select the premise option.

Since IMHO, neither was a bad decision, it was hard to decide. 

A combination of EC2 for hosting and scaling with Amazon S3 for storage and other would be a good fit as well.

But several reasons affected my decision, such as:
On premise pros:
The increasing compute power of simple low-cost servers (as well as personal laptops)
the need for a very fast and reliable time limit query answers, 
the assumption that there is probably no need for a big IT team for such system, 
the importance of handling transactions efficiently and in a reliable way,
(also an assumption that there a probably not needing to perform a huge scale up overnight)

While I took into consideration my own personal experience with cloud services had issues of:
High and unpredictable costs (even with cost limits), High learning curve, needing cloud experts on complex issues   
All these made me decide on the premise approach.

## Flow

Each user will login to the web UI and start to handle his accounts and multiple request lists.

After uploading his list of requests, a service will handle the request list and produce it into a kafka message broker.

#### Kafka 
Kafka will act as the main bus when transferring messages between services and servers.
Its ability to have high performances along with handling scaling well, manage multiple consumers, transactions handling
and partitioning the incoming traffic seems like a good choice for the system.

The key for each message will be the URL, (if several users can work on the same URL, then the user ID can be concatenated)

The incoming queries will enter the INCOMING_QUERY topic.

From here, an apache flink job will consume the messages from kafka, process and handle the requests.


#### Apache Flink
Apache Flink is an open-source, unified stream-processing and batch-processing framework.
It has several key feature that make it a good fit for the system.
1. Flink works really well and have full built in support for working with kafka (as well as other interfaces), and handling transactions reliably.
2. Flink is designed for handling large amounts of streaming date with high throughput
3. Flink also takes care of parallelism well and with ease 
4. Flink also handle state transactions very efficiently and easily

All this made me choose Flink as the framework. 


#### processing dates
If needed, flink can handle 'key by' session with ease, while entering first Flink 'State process' called Query Process Handler.
Its job is to consume (in parallel) the incoming requests and commit(kafka delete) them when done.
Another job is to query the Ignite cache state from Rate limit. 

One of the key feature of Flink is its ability to backpressure when needed, so it will suit the current consideration of rate limit.

## Apache Ignite
Apache Ignite is a distributed database for high-performance computing with in-memory speed.
The use for a very fast, shared -in memory- state will fit this solution.

several Caches will be created: 
Rate Limit Cache(minute,hour,day)

Query result Cache (malicious, unclassified, etc...)

Query status cache (pending, done, waiting for image etc...)

Image Cache (until saved in storage)

Query Manager will query before inserting each list for the limit and will calculate the amount allowed 
while flink will perform the backpressure. 

If the limit is reached partially, it will calculate how much is left and will send partial list while updating the Query result cache.

If the limit has not reached (or a partial send is made) a cache query will be sent in order to verify if this URL was queried before.
And if the configured time has not passed - the answer will be taken from cache.

A process will send the request to urlscan.io via their api.
Since each request can take some time (several seconds) to process at urlscan and to reply (up to 10 seconds),
A retry mechanism will be used (as well as advised by urlscan.io team)

When a result is received, a next 'Flink state function' process will handle the received.
It is in charge of:

update cache for the results.

update relevant kafka topics such as ERRORs and needed re-transmit

Send a request for Image handler

Send the images to an image writer service

## image handler
The image handler will be in charge of taking the UUID for the urlscan result and request for the url screenshot via scanurl api

Also, besides saving the all the URL requests given by urlscan api reit will send the url for enrichment in order to save as a result the URL page.


Finally, a service will consume from the relevant kafka topics and will update the user query lists for the results for each URL.


### Dependencies
JAVA is preferred. (other languages are supported)
Linux is preferred.


## Authors

Ariel Maslaton  
[arielmaslaton@gmail.com](https://github.com/arielmaslaton/)


## License

This project is not licensed
