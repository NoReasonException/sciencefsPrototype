#include <mpi.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include "cJSON/cJSON.h"
#define HOSTNAME_MAXSIZE 100
#define every(x, i) (int i=0;i<x;i++)
#define PURPOSE_SERVER 	0
#define PURPOSE_CLIENT 	1
#define PURPOSE_MAIN	2
#define MAIN_SERVER_RANK 0

#define SERVER_TAG	10
#define CLIENT_TAG	11
#define REPLICA_NAME_MAX 100

#define COMMAND_SUICIDE	1

#define INT_MAX_STRING 10
struct argv;
typedef struct argv argvinfo;




/***
 *	inspectStr -> for debbugging purposes
 */
void inspectStr(char*str){
	for(int i=0;i<strlen(str)+1;i++){
		printf("%d/%d : char = %c  isEnd = %d : isNewLine = %d \n",i,strlen(str),str[i],str[i]=='\0',str[i]=='\n');
	
	}	
	
}
/****
 *	...Because...C
 *
 */
char*addNull(char*str){
	str[strlen(str)-1]='\0';
	return str;
}

/****
 *	Concat of 2 buffers
 *	@WARN -> the responsibillity of freeing the buffer is on caller
 *
 */
char *concat(char*first,char*second){
	char*retval=(char*)malloc(sizeof(char)*(strlen(first)+strlen(second)+1));
	memcpy(retval,first,strlen(first));
	memcpy(retval+strlen(first),second,strlen(second)+1);

	return retval;
	

}
struct argv{
	unsigned short server_nodes;
	unsigned short client_nodes;
	unsigned short replicas_per_shard;

};
argvinfo*alloc_argv(){
	return malloc(sizeof(struct argv));
}
argvinfo*free_argv(argvinfo*ptr){
	free(ptr);
	return NULL;
}
argvinfo*default_construct(argvinfo*param,int procsize){
	param->server_nodes=(int)procsize/2;
	param->client_nodes=(int)procsize/2;
	param->replicas_per_shard=3;
	return param;
}

struct argv*parseargv(int argc,char*argv[],int procsize){
	argvinfo*retval=default_construct(alloc_argv(),procsize);	
	for(int i=0;i<argc;i++){
		if(!strcmp("-s",argv[i])){
			retval->server_nodes=strtol(argv[i+1],NULL,10);
		}
		else if(!strcmp("-c",argv[i])){
			retval->client_nodes=strtol(argv[i+1],NULL,10);
		}
		else if(!strcmp("-rps",argv[i])){
			retval->replicas_per_shard=strtol(argv[i+1],NULL,10);
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
        return abs(rand()%20000)+20000;
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
char* setupPath(char*hostname,int port){
	char postfix[100];
	char suffix[100];

	char *tmp;
	char *command;

	sprintf(suffix, "mkdir -p ");
	sprintf(postfix,"/instance_%d \0 ",port);
	tmp=concat(hostname,postfix);
	command=concat(suffix,tmp);
	

	system(command);
	free(command);
	return tmp;

}

void startReplicaServer(char*hostname,int port,char*replicaName,char*dbpath){
	char command[1000];
	sprintf(command,"mongod --shardsvr --replSet %s --port %d --bind_ip %s --dbpath %s >> log_%d & \n",replicaName,port,hostname,dbpath,port);
	printf("%s",command);
	system(command);

	
}
char* deletePath(char*dbpath){
	char command[100];
	sprintf(command,"rm -rf %s\n",dbpath);
	system(command);
	free(dbpath);
	return NULL;
}
void killReplicaServer(int processid){
	char command[100];
	sprintf(command,"kill %d \n",processid);
	system(command);
	return;



}
char*getReplicaName(){
	MPI_Status status;
	char*replicaName=(char*)malloc(sizeof(char)*REPLICA_NAME_MAX);
	MPI_Recv(replicaName,REPLICA_NAME_MAX,MPI_CHAR,MAIN_SERVER_RANK,SERVER_TAG,MPI_COMM_WORLD,&status);
	return replicaName;

}
void server_start(char*hostname,int port){
	int forkretval;
	MPI_Status status;
        int receiveCommand;
	char *dbpath=setupPath(hostname,port);
	int isDead=0;
	
	char*replicaName=getReplicaName();
	startReplicaServer(hostname,port,replicaName,dbpath);
        
	while(1){
		if(isDead)break;
		MPI_Recv(&receiveCommand,sizeof(int),MPI_INT,MAIN_SERVER_RANK,SERVER_TAG,MPI_COMM_WORLD,&status);
                switch(receiveCommand){
                	case COMMAND_SUICIDE:{
				printf("THREAD %d receive : SUICIDE\n",port);
				deletePath(dbpath);
				killReplicaServer(forkretval);
				isDead=1;
				break;
			}
                }
        }
        
}

void client_start(char*hostname,int port){
//	printf("CLIENT RUN %d\n",port);
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
	return addNull(hostname);

}
int*assignPurposes(argvinfo*user_params,int procsize){
	int*purposes=(int*)malloc(sizeof(int)*procsize);
	purposes[0]=nodeAsMain(0);
	for(int i=1;i<procsize;i++){
		if(i<user_params->server_nodes)purposes[i]=nodeAsServer(i);
                else purposes[i]=nodeAsClient(i);
        }
	return purposes;

}
char** sentReplicaNames(argvinfo*user_args){
	char replicaPrefix[4]="rs_";
	char tmp_buffer[100];
	char *replicaBuffer;
	char **replicaNames=alloc2D(user_args->server_nodes,REPLICA_NAME_MAX,sizeof(char));
	for(int i=1,cnt=0;i<user_args->server_nodes;i+=user_args->replicas_per_shard,cnt+=1){
		sprintf(tmp_buffer,"%d_M",cnt);
		replicaBuffer=concat(replicaPrefix,tmp_buffer);
		for(int j=0;j<user_args->replicas_per_shard&&j+i<user_args->server_nodes;j++){
			memcpy(replicaNames[i+j],replicaBuffer,strlen(replicaBuffer));
			MPI_Send(replicaBuffer,strlen(replicaBuffer),MPI_CHAR,i+j,SERVER_TAG,MPI_COMM_WORLD);
			//free(replicaBuffer); MPI_Send takes ownership of the buffer

		}
		
	}
	return replicaNames;

}


void ack_instances(argvinfo*user_params,char**hostnames,int*ports,int*purposes,char**replicaNames){
	char curr_replica[REPLICA_NAME_MAX] = "NONE";
	int curr_port;
	for(int i=0;i<user_params->server_nodes;i++){
		if(strcmp(curr_replica,replicaNames[i])){
			memcpy(curr_replica,replicaNames[i],strlen(replicaNames[i]));
			curr_port=ports[i];
			printf("%s is %d\n",curr_replica,curr_port);			
		}
	}	
}
void run(int my_rank,int p,int *ports){
	system("sleep 10");
	int command=COMMAND_SUICIDE;
	for(int i=1;i<=p;i++){
		MPI_Send(&command,1,MPI_INT,i,SERVER_TAG,MPI_COMM_WORLD);
		printf("SERVER %d SENT KILL ON %d(%d)\n",my_rank,i,ports[i]);
	}

}
char*itoa(int n){
	char*str=(char*)malloc(sizeof(char)*INT_MAX_STRING);
	sprintf(str,"%d",n);
	return str;

}
char *itoa_buff(char*buff,int n){
	sprintf(buff,"%d",n);
	return buff;
}
char* _rs_initiate_build(char*replicaName,char**hosts,int*ports,int n){
	cJSON *rs_initiate=cJSON_CreateObject();
	cJSON *_id_value=cJSON_CreateString(replicaName);
	cJSON *iter_object;
	cJSON *id_iter_object;
	
	cJSON_AddItemToObject(rs_initiate,"_id",_id_value);
	char*_member_id_buff=(char*)malloc(sizeof(char)*INT_MAX_STRING);
	
	//printf("%s",cJSON_Print(rs_initiate));
	

	for(int i=0;i<n;i++){
		iter_object=cJSON_CreateObject();
		_member_id_buff=itoa_buff(_member_id_buff,i);

	
	
	}

	return NULL;


}
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
		printf("THREAD %d TERMINATES\n",port);
	
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
		char**replicaNames;
		int*ports;
		int*purposes;
		printf("Size of cluster %d\n",p);
		argvinfo*user_params=parseargv(argc,argv,p);	
		hosts=receiveHostnames(p);
		ports=generatePorts(p);
		purposes=assignPurposes(user_params,p);
		

		replicaNames=sentReplicaNames(user_params);
		
		
		ack_instances(user_params,
				hosts,
				ports,
				purposes,
				replicaNames);
		_rs_initiate_build("rs0_M",hosts,ports,3);

		run(my_rank,user_params->server_nodes,ports);

		
		free2D(hosts,p);
		free2D(replicaNames,user_params->server_nodes);
		free(ports);
		free(purposes);
	}
		
	MPI_Finalize();
	fflush(stdout);
}
