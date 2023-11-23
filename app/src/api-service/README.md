### API Service Container 

This container has all the python files to run and expose thr backend apis.

To run the container locally:

Open a terminal and go to the location where api-service folder is.

Run 

```
sh docker-shell.sh
```

Once inside the docker container run 
```angular2html
uvicorn_server
```
To view and test APIs go to http://localhost:9000/docs