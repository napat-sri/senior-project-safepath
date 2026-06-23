# Napat's learning reflections

## ✅ 27 Apr 2026
### Git
- I've reviewed how to create a repository on Github and also several git commands which necessary use e.g. merge, push, pull. This can decrease issues during this project.

### Docker and Docker compose
- As I've used Docker before but not understand much, therefore today I've known the basics of how to create, build, and compose images into the container. Additionally, I know how different between Docker and Docker compose.

### Agentic workflow: LangGraph, LangFlow, n8n
- Previously, I've created my own agent to assist my daily life using n8n's framework, but today I've seen more agentic workflows that have some pros and cons and different usages. My colleagues and I can make the decisions which agent will be use in this project usefully.

## ✅ 28 Apr 2026
### Exploring Docker Image
- I research a Docker image which is relevant in this project from Docker Hub. I found ([Openstreetmap](https://hub.docker.com/r/overv/openstreetmap-tile-server)) that is an image that use to display a selected map. The main point is a large size of map resources and combining with my issue that I have to learn how to install it, so it takes much time to prepare.
- This is the main part of our project, it will be shown in the UI of an application. I will be more encourage to prepare and learn about this image and continue with the way to integrate with another images.

## ✅ 4 May 2026
### REST Architecture (FastAPI)
- I've reviewed how to use REST architecture in default protocols (GET, POST, PUT, DELETE)
- I've got more practice with learning how to build a Docker compose for a sample program of Movie Picker, then complete the functions inside to show the results of each
- At the beginning, I had a little bit confusing about how to build a Docker, after I research and try, I can build and run it perfectly. Then, I can write some function correctly at once, but some of them has error to fix. My overall practicing is quite good.

### Project Progress Update and Backlog
- My group updated the progress with Professor and guidance us some relevant resources to make it better.
- Then, we discuss more about workflow and plan to create our github project's backlog.
- We will learn more resources from both Professor's recommendation and our researches.
- In addition, as I cannot run the openstreetmap image completely, I tried to run again at home with read the docs again carefully. Finally, I can already run this image.

## ✅ 5 May 2026
### Personas
- I created a persona of this project with four main aspects: Personalization, Job/Context, Education & Technial Skill, and Relevance. These details show type of user who would want to use the product and hope to archive.
- My persona is a German project manager named "Markus Schneider". He is 38 years old who lives in a rented apartment in Charlottenburg. He works at a logistics company with frequently travels between office, client sites, and home by a mix of U-Bahn and walking. He is comfortable using everyday apps (e.g. Google Maps or WhatsApp) and digital tool for work (e.g. Excel or PM software). As he is good at product design, he doesn't like in complex settings or technicals. He wants to feel secure during his journey, not just efficiency, and avoid high-risk areas to gain his confidence.

### Scenarios
- My group discussed about scenarios of this project which describe a realistic situation according to our personas to achieve their goals. The scenarios focused on objective, actors (persona's references), activities, problems, and resolution (how to solve the problems).
- We found that Alex chen (A bachelor student) and John Doe (A tourist) have a similar scenario to reach our project's purpose. So, we create scenarios from both perspectives to think our product's features in the next process.

### User Stories
- I've reviewed the definition and how to format a user story which make us easy to understand the features based on users' needs. In addition, the user story can make us estimate, prioritise, and track in a product backlog.
- We will discuss the user stories during the week before the next class.

## ✅ 11 May 2026
### Project Checklist and Update
- My group continues the definition of the project especially creating user stories. And for my task is to create a timetable for sprints.
- Our professor asked for project update according his checklist: Group members, Vision statement, Architecture design, Personas, Scenarios, User stories, Features, and Timetable for Sprints. We completed most of them, however, some documents would add more text or link inside to track them easily.

## ✅ 12 May 2026
### RAG (Retrieval Augmented Generation)
- I've learned the introduction and the process of RAG.
- I tried to make a basic agent in Langflow using an information from MDH website to ask the address of Berlin campus as an example.

- An example of an agent

<img width="2560" height="1281" alt="image" src="https://github.com/user-attachments/assets/d2dbea48-ddaa-4385-9683-778271d5b3a0" />

- An example of asking the address of MDH university in Berlin

<img width="2560" height="1278" alt="image" src="https://github.com/user-attachments/assets/6c8522df-6d4c-4d1e-a479-3e19e2ce8778" />

## ❌ 18 May 2026
*I excused for a sick leave. However, I asked my group what they've done this day more about RAG and run an example workflow.*

## ✅ 19 May 2026
### RAG (Cont.)
- I've reviewed from yesterday I missed about indexing, chunking, collecting, and embedding the data. Then, I've tried to ask this agent and it can answer deeper compare with last week's workflow.
- I've learned how to create an agent which can be another choice to integrate in the project.

## ✅ 26 May 2026
### Project Updates
- Last week, we continued the project to prove our main features are making a conversation with a chatbot and suggesting the safe routes using an agent.
- My main task is on the frontend part of this application which according to these issues on the sprint:
  * [Create Homepage UI](https://github.com/napat-sri/senior-project-safepath/issues/24) (contributed with May)
  * [Create a basic information card](https://github.com/napat-sri/senior-project-safepath/issues/52)
  * [Create a route analysis service](https://github.com/napat-sri/senior-project-safepath/issues/70)
  * [Create a route options service](https://github.com/napat-sri/senior-project-safepath/issues/75)
- Another task is on the Langflow agent that I have to [create a chatbot button](https://github.com/napat-sri/senior-project-safepath/issues/55) and [create a chatbot agent](https://github.com/napat-sri/senior-project-safepath/issues/54) for answering the question about navigation and information about Berlin.
- During I created the frontend part and the Langflow agent, Pantida responded in a backend to create APIs and integrated with my part, and May was not only assisted my part but also processed the specific data in Berlin - crime, accident, lighting - to train it and integrated to the app in the next sprint.
- My next step is enhancing the route detail page. This page will show the insight of the selected route to see how much safety score breakdown in each category.

## ✅ 27 May 2026
### MCP (Model Context Protocol)
- I've learned about a concept and cores of MCP server which acts as a connection between AI application and external systems.
- I've tried to build an MCP server with the US weather API and connect to Claude Desktop. I followed the instructions and my server worked.
    * An example of the MCP server testing (US weather API)
<img width="2560" height="1504" alt="image" src="https://github.com/user-attachments/assets/8efb1b6e-9f1e-47fe-a331-facdac05e078" />

- My group have to adapt MCP server with creating our own one into the project.

## ✅ 1 Jun 2026
### Deploying to Production
- I've learned about the process of how to deploy the project on production to publish to public users. There are several tools include in this process:
    * VPS (Virtual Private Server) and hosting provider: Choose a server service provider and obtain your own IP address to connect to the server. (In this case, we use [Contabo](https://contabo.com/en/) because it is affordable and suits our project’s size.)
    * Server setup and SSH access: After we got a server IP address, we set the server to allow connecting via SSH authentication instead of password. This action will let our project more secure because each user has own private key and public key.
    * Docker and Reverse Proxy: We install [Docker on Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04) on the server (Ubuntu). Then we use [Caddy Docker Proxy](https://github.com/lucaslorentz/caddy-docker-proxy) as a reverse proxy to route HTTP/HTTPS traffic (ports 80/443) to our containers; SSH (port 22) remains for server administration (ideally restricted by firewall/security group).
    * Register a dynamic DNS (Domain Name Server): We use [Duck DNS](https://www.duckdns.org/) which is a free dynamic DNS hosted to set the domain name for the project. Then we use "ping" in command prompt to check the connection to the host and try to connect the server using this instead of a server IP address.
- I was glad to act as a professor's assistant by demonstrating the process to my classmates step-by-step and helping those who had issues configuring their own servers.

## ✅ 2 Jun 2026
### Deploying to Production (Cont.)
- We've continued the process of deploying to production:
    * Git branch strategy: We cannot deploy directly from the main branch, so we created a new branch called "prod" specifically to trigger auto-deploy. We also cloned our GitHub repository onto our server.
    * GitHub webhook: We set up a config file on the server and used [Webhook](https://github.com/adnanh/webhook/) with GitHub. This webhook will call our server on every `git push` to the "prod" branch.
    * Webhook container & deploy script: We created a Dockerfile for the webhook service and added it to Docker Compose on our server. We also created a deploy script to pull the latest changes and restart the project's services.

## ✅ 8 Jun 2026
### Deploying to Production (Cont.)
- We've reviewed the process from last week and continued further:
    * We started configuring Docker Compose for our app images (frontend, backend, openstreetmap, and langflow). Langflow was the first service we configured, using Caddy's reverse proxy for production deployment.
## ✅ 9 Jun 2026
### Deploying to Production (Cont.)
- We've recapped the full production deployment workflow — from choosing the VPS provider to deploying the script.
- We did a revision quiz to check our understanding. The quiz had 22 questions and took only 15 minutes.
- We've continued the langflow configuration; we encountered some conflicts and worked on solutions that fit our program.

## ✅ 15 Jun 2026
### Deploying to Production (Cont.)
- We've created a new docker compose file only for langflow, to separate with other services. This config will help us bring our own workflows into our production. And also provide an authentication to connect with own workflow list.
- We also updated commands inside the deploy script that include with docker compose configurations.
- We can bring our project's workflow into production completely.
- Previously, we used Portainer with internal authentication which can be concerned in security issue if there is any unpredicted case happen. To prevent this issue, we've learned about [Keycloak](https://www.keycloak.org/) which is an open source for authentication to applications and secure services using Single-Sign On (SSO) and OAuth protocol.

## ✅ 16 Jun 2026
### Preparing before Midterm
- Yesterday, we used Keycloak for authentication service, however, an issue was when we connected, a dashboard was empty because the user role wasn't correct. Today, we set the role of our user to be an "administrator", so right now we can access to the Portainer dashboard successfully.
- Our main event is to finalize services on our project which we will present on Midterm next week. Make sure our docker compose files: one for Langflow and one for other services combined together and all of them should be connected.
- Before the presentation day, we will prepare all relevant items: Slide, Demo application, and Features to be done and get ready for Q&A session which includes what we've learned from day one.

## 🎯 22 Jun 2026
### Midterm Presentation
- We presented the progress of our project from kick-off until Midterm here.
- The presentation took 15 minutes including these topics: Problem statement, Target users, Project timeline, Architecture diagram, Live demo, Sprint 1 progress & backlog, and The next steps.
- After the presentation, it was a Q&A part which other groups asked us to clarify, and also our professor asked and gave us a comment.