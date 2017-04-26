# SimpleHttpServer
A simple python3 HTTP Server with routing logic that can cache select item requests.

This is a sample project to evaluate different portions of Python3 web services development.

Requirements are to handle GET, POST, and DELETE operations on a select number of endpoints otherwise return response code 404.

Included a build.sh file to verify python3.5 is installed on the system and run.sh wrapper to start the service.

The code is divided into two modules (server and simple_datastore) to isolate the front end functionality from the back-end storage. This would allow the components to be reused, modified, and tested independent of one another.

# Server
The server module is the main entry point into the project and is focused on running the HTTP server code until a KeyboardInterrupt is triggered (i.e. Ctrl-C). The server utilizes a HTTP request handler to operate on a given connection/request which will go through one of the do_* methods. Since there are two general functions to the POST operations the underlying processing was shifted to separate methods to keep the entry method as clean as possible.

A couple of helper methods are also added to the handler to abstract some nuances or shared code sections to promote re-use and rapid development/enhancements. The converters between bytes and str make it more explicit for any other developers to understand that python3 communication/sockets use bytes and not raw strings. This will hopefully reduce any issues in this area should new methods/endpoints be added.

# Datastore
The simple_datastore module is focused on abstracting the underlying datastore which would allow the possibility of replacing the storage format without impacting any reliant modules. The current implementation utilizes a simple shelve object (roughly equivalent to a file backed dictionary) to flush the information to disk when added/removing elements. The ease of access and similarities to a standard dictionary made integration with the shelve fast; it was also built into the standard libraries which reduced external/3rd party dependencies. If this project is converted to a multi-client format it would need additional synchronization and possibly converting to a SQL database or some similar technology.

The PendingDataUpdate class within this module is a helper class to store and reference pending requests that have not been pushed to disk. Having a separate class does add a bit of complexity but helps improve code readability and extensibility.

# Possible Extensions
- Convert to a multi-client model. This may require converting the backing datastore, adding locks for synchronization, and leveraging parallel processing/threading for handling simultaneous client access.
- Review any issues with multi-client sharing a common pending queue which could cause unexpected behavior depending on when individual clients commit changes.
- Review the endpoint pattern as there seems to be inefficiencies built in with respect to looking up the key. There's the general conflict of the root element representing both the key and the operations (/set and /commit).
- Extend the service to load configuration information from a conf file (host/port)
