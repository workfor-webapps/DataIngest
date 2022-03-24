# PDEA
Pdf table data extraction and analysis repository

## Contributors:
* Curtin Institute for Computation (CIC)
  * Foad Farivar (foad.farivar@curtin.edu.au)
  * Daniel Marrable (D.Marrable@curtin.edu.au)
  * Carlo Martinotti (carlo.martinotti@curtin.edu.au)
 
* School of Management and Marketing 
  * Ramon Wenel (ramon.wenzel@curtin.edu.au)

# Running the scripts contained in this repository

### Pre requisite: 
For the sake of brevity, this document will assume the user is running on Linux. If a reader is using windows, they will be able to get a similar terminal interface by using [WSL](https://docs.microsoft.com/en-us/windows/wsl/install). The main method of using the app is via [Docker](https://www.docker.com/) container. You need to install Docker to your local system to be able to build and run the docker image.
The folowing folders should be present in your [developer@workfor.com.au] google drive:



## 1- Get the client_secret file
a. Login to google [cloud console](https://console.cloud.google.com/)  
b. At the top left corner click *[select a project]* and select **dataingest** 
c. From the top left Navigation bar, select *[APIs and Services]*
d. Click Credentials from the left side menu
e. Download the **OAuth 2.0 Client IDs** as a Json file and rename it to **"client_secret.json"**
f. Copy this file to the same directory as the Dockerfile

## 2- Docker build
a. In the main directory run: ``` docker build -t pdea[:tag] . ```

## 3- Docker run
a. If the image is sucessfully built in the previouse step run ``` docker run -d --name dataingest -e PORT=8080 -p 8080:8080 pdea[:tag] ```
b. You can check the logs of the running docker container by running: ``` docker logs -f --details dataingest```

## 4- Open the application
a. the application by default will be served an http://localhost:8080/

## 5- Stopping and removing the container
a. Run ```docker stop dataingest```
b. Run ```docker rm dataingest```
