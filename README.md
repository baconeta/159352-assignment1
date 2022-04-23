
# Web Portfolio Assignment

A web container version of a simple HTTP server and stock portfolio site.

Made for 159.352 Advanced Web Development at Massey University April 2022 by Joshua Pearson.

![image](https://user-images.githubusercontent.com/36744690/164894147-fdc230ac-a08c-4586-92b8-2dce05185a07.png)


## Demo

https://jp159352.herokuapp.com/

username and password: 20019455

See [run locally](#run-locally) for information on how to launch and use the server locally.

## Home page

This page contains almost nothing. I chose to have this page be built and set up with the navigation bar in order for a user to quickly access the two pages.

Click one of the two links: Portfolio or Research to get started.

## Portfolio

![image](https://user-images.githubusercontent.com/36744690/164894241-c8de3368-a8e9-4f6f-acaf-0888592d3285.png) 

On this page, you have a few elements including:
- A navigation bar at the top, indicating the current page we are one.
- A disclaimer link showing where we retrieve price and symbol data required by IEX.
- A portfolio containing the ticker, number, and average price of each share of a stock we own.
- A live calculation displaying the gain or loss we have made purchashing and holding the shares of each stock in the portfolio.
- Form input with autocomplete stock name, quantity, and prices with error handling on input.
- A reset button that clears the user input from the form.
- Space below the buttons will display any user relevant messages after they press update.

## Research

![image](https://user-images.githubusercontent.com/36744690/164894398-d1ce24a6-63a3-43e7-810b-4f186080fea7.png)

On this page, the elements are simpler before pressing research. We have:
- An input box where the user can select (with autocomplete) a stock to research.
- Once submitted if the user enters a valid stock, you will see the stocok information and a chart of the last 5 years of stock history.
Note the chart defaults to only viewing 1 year data in the window for cleaner views but there are range buttons above the chart and a bar below to finetune the viewing window.

Also, note that the chart uses CanvasJS free which is techncially only valid for free for 30 days so this may stop working at any time.


## Container and deployment info

This project was built almost exclusively using python 3.10. Once completed, I loaded this into a docker container and deployed it to Heroku.
The dockerfile data is visible inside the repo but the relevant data is here:

```docker
  FROM python:3.10.0a2-slim-buster
  RUN pip3 install requests
  COPY . /src
  WORKDIR /src
  CMD python server.py $PORT
```

The Dockerfile to run on Docker locally was changed to be:
```docker
  FROM python:3.10.0a2-slim-buster
  RUN pip3 install requests
  COPY . /src
  WORKDIR /src
  EXPOSE 8080
  CMD python server.py 8080
```

We use $PORT to allow Heroku on deployment to select the port used for hosting services.

Some images of the process are below.

Command line:
![image](https://user-images.githubusercontent.com/36744690/164895717-0d04f994-6237-4f0e-a11a-9a73bd811bbd.png)

Docker running locally:
![image](https://user-images.githubusercontent.com/36744690/164895752-7a0c0155-140c-489b-93d3-7717cd57d0cb.png)

Accessible and working completely on localhost:8080
![image](https://user-images.githubusercontent.com/36744690/164896193-5dded4cb-84e9-4358-bce9-94aabb2ef3a1.png)


## Run Locally

- _Clone the project from Github_

```bash
  git clone https://github.com/baconeta/159352-assignment1
```

Go to the project directory

```bash
  cd assignment1
```

Install dependencies

```bash
  pip3 install requests
```

Start the server (you should confirm that line 25 is commented out and line 26 is uncommented unless running in a Docker container - see below for more info)

```bash
  python3 server.py
```

- _Run locally without cloning from git repo_

In your local environment or IDE ensure you have the requests library installed (consider using pip3 install requests)

Otherwise similarly to above using the command line:

Go to the project directory

```bash
  cd assignment1
```

Install dependencies

```bash
  pip3 install requests
```

Start the server. 
You can also skip this cmd line command and instead run it in an anaconda or venv environment inside your IDE and run the server file manually.

```bash
  python3 server.py
```

Make sure the following code is set correctly otherwise ensure you pass the port argument into the run command. Docker and Heroku require the sys argument instead to be uncommented as it is in the repo version of server.py.
![image](https://user-images.githubusercontent.com/36744690/164895225-59cfae01-a2a4-45d3-9f01-77e8d47978d8.png)


Once the server is running using either method you can access the the locally hosted site using:
http://localhost:8080/

username and password: 20019455
## Tech Stack

**Server:** 

Python 3.10 using the following main modules
- requests
- base64 _core builtin_
- socket _core builtin_

Docker container
- Docker version 20.10.14, build a224086
- Docker Desktop 4.7.1 (77678)

Heroku
- heroku/7.60.1 win32-x64 node-v14.19.0
- config: web /bin/sh -c python\ server.py\ \$PORT

![image](https://user-images.githubusercontent.com/36744690/164894926-d52da68c-0c80-4c0e-8f99-fdb86631fb7c.png)


**Tools:**
- PyCharm 2022.1 (Professional Edition)
- Anaconda3 Python Environment
- Webstorm 2022.1 (Professional Edition)
- [IEX REST API](https://iexcloud.io/) (free version)
- [CanvasJS](https://canvasjs.com/) (30 day free trial)



## Acknowledgements and references

 - [CanvasJS stock chart reference](https://canvasjs.com/docs/stockcharts/basics-of-creating-html5-stockchart/)
 - [IEX docs](https://iexcloud.io/docs/api/#api-reference)
 - [Docker documentation](https://docs.docker.com/get-started/)
