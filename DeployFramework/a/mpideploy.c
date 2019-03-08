#include <mpi.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#define HOSTNAME_MAXSIZE 100
#define every(x, i) (int i=0;i<x;i++)
#define PURPOSE_SERVER 	0
#define PURPOSE_CLIENT 	1
#define PURPOSE_MAIN	2
#define MAIN_SERVER_RANK 0

#define SERVER_TAG	10
#define CLIENT_TAG	11
#define REPLICA_NAME_MAX 100
struct argv;
typedef struct argv argvinfo;


/***
 * Command Line arguments
 */
struct argv{
	unsigned short server_nodes;
	unsigned short client_nodes;

};
argvinfo*alloc_argv(){
	return malloc(sizeof(struct argv));
}
argvinfo*free_argv(argvinfo*ptr){
	free(ptr);
	return NULL;
}

struct argv*parseargv(int argc,char*argv[]){
	argvinfo*retval=alloc_argv();
	for(int i=0;i<argc;i++){
		if(!strcmp("-s",argv[i])){
			retval->server_nodes=strtol(argv[i+1],NULL,10);
		}
		else if(!strcmp("-c",argv[i])){
			retval->client_nodes=strtol(argv[i+1],NULL,10);
		}
	}
	return retval;

}



void **alloc2D(int n,int m,ssize_t typesize){
	int i=0;
	void **retval=malloc(n*sizeof(char*));
	if(!retval)printf("[WARN]Null returned at alloc2D , it will crash maybe due to LOWMEM");
	for (i=0;i<n;i++)
	{
		retval[i]=(char*)malloc(typesize*m);
		if(!retval[i])printf("[WARN]Null returned at alloc2D , it will crash maybe due to LOWMEM");
	}
	return retval;
	
}
void** free2D(void**ptr,int n){
	for(int i=0;i<n;i++)free(ptr[i]);
	return NULL;
}
char **receiveHostnames(int procsize){
	int source=0;
	int tag=0;
	char message[100];
	MPI_Status status;
	char **hosts=(char**)alloc2D(procsize,HOSTNAME_MAXSIZE,sizeof(char));
	for(source=1;source<procsize;source++){
		MPI_Recv(hosts[source],HOSTNAME_MAXSIZE,MPI_CHAR,source,tag,MPI_COMM_WORLD,&status);
		
        }
	return hosts;

}
int getRandomPort(){
        rand();
}


int *generatePorts(int procsize){
	int source=0;
	int tag=0;
	MPI_Status status;
	int*ports=(int*)malloc(sizeof(int)*procsize);
	for(source=1;source<procsize;source++){
		ports[source]=getRandomPort();
		MPI_Send(ports+source,1,MPI_INT,source,tag,MPI_COMM_WORLD);
	}
	return ports;
	
}
int nodeAs(int rank,int purpose){
	MPI_Send(&purpose,1,MPI_INT,rank,0,MPI_COMM_WORLD);
	return purpose;	
}
int nodeAsMain(int rank){
	return PURPOSE_MAIN;
}
int nodeAsServer(int rank){
	return nodeAs(rank,PURPOSE_SERVER);
}
int nodeAsClient(int rank){
	return nodeAs(rank,PURPOSE_CLIENT);
}
char *clearNullChar(char*any){
	any[strlen(any)-1]='\\';
	return any;
}
void setupPath(char*hostname,int port){
	char command[1000];
	hostname=clearNullChar(hostname);
	sprintf(command,"mkdir -p %s/instance%d",hostname,port);
	system(command);
	return;

}
void startReplicaServer(char*hostname,int port,char*replicaName){
	printf("%s\n",replicaName);
}
char*getReplicaName(){
	MPI_Status status;
	char*replicaName=(char*)malloc(sizeof(char)*REPLICA_NAME_MAX);
	MPI_Recv(replicaName,REPLICA_NAME_MAX,MPI_CHAR,MAIN_SERVER_RANK,SERVER_TAG,MPI_COMM_WORLD,&status);
	return replicaName;

}
void server_start(char*hostname,int port){
	setupPath(hostname,port);	
	char*replicaName=getReplicaName();	
	startReplicaServer(hostname,port,replicaName);
	
}

void client_start(char*hostname,int port){
    
}

void applyPurpose(int purpose,char*hostname,int port){
	switch(purpose){
		case PURPOSE_SERVER:server_start(hostname,port);break;
		case PURPOSE_CLIENT:client_start(hostname,port);break;
	
	}
}
char*getHostname(){
	char *hostname=(char*)malloc(sizeof(char)*HOSTNAME_MAXSIZE);
	char path[HOSTNAME_MAXSIZE];
        FILE *fp=popen("/bin/hostname","r");
        while (fgets(path, sizeof(path)-1, fp) != NULL) {
       		sprintf(hostname,"%s", path);
       	}

	return hostname;

}
int*assignPurposes(int procsize){
	int*purposes=(int*)malloc(sizeof(int)*procsize);
	purposes[0]=nodeAsMain(0);
	for(int i=1;i<procsize;i++){
		if(i%2)purposes[i]=nodeAsClient(i);
                else purposes[i]=nodeAsServer(i);
        }
	return purposes;

}
void sentReplicaNames(int procsize,int replicas_per_shard){
	char replicaPrefix[3]="rs";
	char replicaBuffer[REPLICA_NAME_MAX];
	for(int i=1;i+replicas_per_shard<procsize;i+=replicas_per_shard){
		sprintf(replicaBuffer,"%s_%d\0",replicaPrefix,i);
		printf("%s\n",replicaBuffer);
		for(int j=0;j<replicas_per_shard;j++){
			MPI_Send(replicaBuffer,strlen(replicaBuffer),MPI_CHAR,i+j,SERVER_TAG,MPI_COMM_WORLD);
			printf("%d\t",i+j);	
		}	
		printf("\n");
	}

}
void setupConfigServer(){

}
void setupMongos(){


}

void setup(int procsize,char** hosts,int*ports,int*purposes,int replicas_per_shard){
	
	sentReplicaNames(procsize,replicas_per_shard);
	//setupConfigServer();
	//setupMongos();
	
	


}
void run(){/*while(1);*/}
int main(int argc,char*argv[]){

	int my_rank;
	int p;
	int source;
	int dest=MAIN_SERVER_RANK;
	int tag=0;
	int provided;



	char *hostname;
	int port=getRandomPort();
	int purpose=0;




	FILE *fp;
	int mainServer=0;
	MPI_Status status;
	MPI_Init(&argc,&argv);

	MPI_Comm_rank(MPI_COMM_WORLD,&my_rank);
	MPI_Comm_size(MPI_COMM_WORLD,&p);

	
	/*
	 * Secondary Processors
	 */
	if(my_rank!=0){

		char sentbuffer[HOSTNAME_MAXSIZE];
		char*replicaName[REPLICA_NAME_MAX];

		hostname=getHostname();
		strncpy(sentbuffer,hostname,strlen(hostname));						//copy the hostname because MPI destroys the buffer
		MPI_Send(sentbuffer,strlen(sentbuffer)+1,MPI_CHAR,dest,tag,MPI_COMM_WORLD); 		//sent my hostname to main
		MPI_Recv(&port,1,MPI_INT,mainServer,tag,MPI_COMM_WORLD,&status);			//receive my port number to main
		MPI_Recv(&purpose,1,MPI_INT,mainServer,tag,MPI_COMM_WORLD,&status);			//receive purpose

		applyPurpose(purpose,hostname,port);
		
		free(hostname);
	}
	/**
	 * The main processor
	 *	The main processor is also the configuration server
	 * */
	else{
		MPI_Status status;
		int tmp;
		char**hosts;
		int*ports;
		int*purposes;
		printf("Size of cluster %d\n",p);
		argvinfo*user_params=parseargv(argc,argv);	
		hosts=receiveHostnames(p);
		for(int i=1;i<p;i++){
			//printf("node %d hostname %s\n",i,hosts[i]);
		}
		ports=generatePorts(p);
		purposes=assignPurposes(p);
		

		setup(p,
			hosts,
			ports,
			purposes,
			5); //TODO : make it taking from command line
			
		run();


		free2D(hosts,p);
		free(ports);
		free(purposes);
	}
		
	MPI_Finalize();
	fflush(stdout);
}
