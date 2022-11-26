# Cron-Scheduler

#### The scheduler is built using the Actor Model, which guarantees concurrency, where each Actor is operating in a single-threaded illusion, moreover, an Actor's state is isolated and can never be modified directly by another Actor

#### Actors can only communicate together through messaging, and Actor's state can indirectly be modified upon receiving a certain message it's expecting

### An Actor can also create a finite number of child Actors

The Cron-Scheduler is built using 4 Actors

**Timer Actor** 
1. simply it acts as a global clock sending tick events

**Scheduler Actor** 
1. launching tasks periodically according to the defined periodicity by launching **Task Monitor Actor**
2. maintaining statistics for tasks that ran
3. timing out tasks according to the defined timeout

**Task Monitor Actor** 
1. launching tasks **Task Actor**
2. write task logs and execution time to a file
3. informs scheduler that a task has finished its execution

**Task Actor** 
1. calls the supplied function through the configuration provided
2. informs the task monitor that the execution is done
3. propagates the logs buffered to the task monitor actor

You can also have a look on this [Miro board](https://miro.com/app/board/uXjVP_2S3wg=/?share_link_id=644427807292) for the design overview

The Cron-Scheduler has a single point of entry which the method **launch_scheduler** located in launcher.py


Reasoning behind using the Actor Model
1. Each actor runs concurrently in an isolated state
2. Provides modularity, where each Actor is responsible for a certain functionality
3. Can be easily scaled horizontally, by applying different techniques which we can discuss briefly
   
Scaling Techniques
1. By using Routers, we can replicate a specific actor (X), then when a message is communicated to X, it should first be sent to the router, and the router should then forward the message to one of the workers, we can also use Consistent Hashing function to forward the messages in a fair pattern
2. Work-Pulling, to overcome the issue of unbounded mailbox and avoiding out of memory issues, where we can use Apache Kafka as an external tool to persist the messages in its queues and messages get distributed across the available workers, of course we can configure our workers (the consumers) to consume messages from specific partitions, and another option would be configuring our producer actor to assign a key to the event to configure the topic partition assignment
3. Akka Cluster Sharding where we shard Actors across the cluster, where each Actor is assigned an entity ID which is unique across the cluster, when a message is sent, a set of functions extract the shard ID as well as the entity ID, this makes it possible for you to locate the unique instance of that actor within the cluster. In the event that no actor currently exists, the actor will be created. The sharding system will ensure that only one instance of each actor exists in the cluster at any time.


### To create the venv and install dependencies run

`make venv`

### To run tests on your own machine, run

`make test`

upon running `make test`, you can find a coverage report generated, and its path is **htmlcov/index.html**

### To run the application on your own machine, run

`make run`

----------------------------------------------------------------------------------------------------------

### Environment Variables

1. **GRANULARITY** >> a string that represents the timer granularity (default is minute)
2. **SUPPORTED_EXTENSIONS** >> a list that holds all supported file extensions to be run (default
   is ["json","yaml","yml"])
3. **LOG_LEVEL** >> a string that holds the logger log level (default is INFO)
4. **LOGS_BASE_DIRECTORY** >> a string that holds the directory where logs will be written (default is "logs")
5. **JOBS_FILE_PATH** >> a string that holds the path of the jobs file (default is "jobs.json")

___

### Jobs Sample Representation

#### Jobs are being represented as JSON objects in a file named `jobs.json`

#### Below you can find a sample of the file to be submitted


```json
{
	"jobs": [{
		"identifier": "job1",
		"path": "periodic_functions.functions",
		"function_name": "sleep_2_mins",
		"timeout": "5m",
		"periodicity": "1m",
		"start_date": "2022-11-21"
	}]
}
```

## Future Work

1. Being able to track the history of the jobs ran through our scheduler with the usage of a database to persist the scheduler events
2. For local development, we can instead run docker containers for each job, and for production, we can instead deploy Kubernetes Jobs which get deleted upon success
3. In production, logs can be streamed to a cloud logging service (such as **GCP Logs Explorer**) or get pushed to **Datadog** to provide observability when certain conditions occur
4. Persisting the scheduler's state to provide Fault Tolerance
5. In production, we can use Apache Kafka as our messaging queue to avoid out of memory exceptions related to unbounded mailbox, this would also help us in monitoring our Actors by checking the consumer group lag which would in turn help us decide if we need to scale our Actor
6. We can also use Apache Kafka as a job submitter, where we can create a new actor which consumes from a jobs topic and sends events to the scheduler actor when a new job gets submitted


And you can also check this [Miro Board](https://miro.com/app/board/uXjVP_2S378=/?share_link_id=403730756861) for production prototype