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
/***
 *	The user arguments struct
 *	
 *	the .parseargv routine takes the argc/argv from the main routine returns this nice and clean struct
 *
 */
struct argv{
	unsigned short server_nodes;				//the amount of server nodes
	unsigned short client_nodes;				//the amount of client nodes
	unsigned short replicas_per_shard;			//replicas per shards(obviously)

};

/***
 * alloc_argv(void)
 *Allocates a struct argv*
 *@Note you must free this pointer using free_argv	
 *
 */
argvinfo*alloc_argv(void){
	return malloc(sizeof(struct argv));
}
/***
 *free_argv(struct argv*)
 *Please use it as follows...
 *	ptr=free_argv(ptr)
 *
 *in order to properly set ptr=NULL after freeing
 *
 */
argvinfo*free_argv(argvinfo*ptr){
	free(ptr);
	return NULL;
}
/****
 *In case the user gives a number of params , defaults must exist
 *This routine returns a properly constructed struct argv* with all the defaults
 *
 *
 */
argvinfo*default_construct(argvinfo*param,int procsize){
	param->server_nodes=(int)procsize/2;
	param->client_nodes=(int)procsize/2;
	param->replicas_per_shard=3;
	return param;
}
/***
 *Parses all the user params , returns a struct argv*
 *
 *
 */
argvinfo*parseargv(int argc,char*argv[],int procsize){
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
/***
 *Allocs a generic 2D array
 *Its mandatory to free using free2D , otherwise you will have n*m*typesize leaked bytes in each call
 *
 */
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
/***
 *Properly deconstruct a 2D array initialized using alloc2D
 *Please use as follows
 *		ptr=free2D(ptr)
 *
 *
 */
void** free2D(void**ptr,int n){
	for(int i=0;i<n;i++)free(ptr[i]);
	return NULL;
}
/***
 *blocs untill all slaves return their hostnames
 *returns a 2D array allocated with alloc2D(please @See alloc2D and free2D in order to avoid leaks)
 *
 */
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
/***
 *Returns a proper 20000<p<40000 port
 *
 */
int getRandomPort(){
        return abs(rand()%20000)+20000;
}

/****
 *Sends in all slaves the ports that they will use
 */
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
/***
 * Sents a purpose into the x-th slave (x=rack)
 * The purposes may be...
 * 
 * ->	PURPOSE_SERVER  0		//participate into the mongod cluster
 * ->	PURPOSE_CLIENT  1		//runs the benchmark tester
 * ->	PURPOSE_MAIN    2		//the main server (only assigned on rack 0)
 *
 */
int nodeAs(int rank,int purpose){
	MPI_Send(&purpose,1,MPI_INT,rank,0,MPI_COMM_WORLD);
	return purpose;	
}
/***
 *A simple wrapper over nodeAs(rack,purpose) routine who assigns in x-th server(x=rank)
 * The PURPOSE_MAIN(2) 
 *
 */
int nodeAsMain(int rank){
	return PURPOSE_MAIN;
}
/***
 *A simple wrapper over nodeAs(rack,puprose) routine who assigns in x-th server(x=rank)
 * The PURPOSE_SERVER (0)
 *
 */
int nodeAsServer(int rank){
	return nodeAs(rank,PURPOSE_SERVER);
}
/***
 *A simple wrapper over nodeAs(rack,purpose) routine who assigns in x-th server(x=rank)
 *The PURPOSE_CLIENT(1)
 *
 */
int nodeAsClient(int rank){
	return nodeAs(rank,PURPOSE_CLIENT);
}
/***
 *Setups a path in given host and port
 *	Expected Behaviour
 *
 */
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
/***
 *Given the hostname , port , replica name and dbPath , this routine starts the mongod instances 
 *
 */
void startReplicaServer(char*hostname,int port,char*replicaName,char*dbpath){
	char command[1000];
	sprintf(command,"mongod --shardsvr --replSet %s --port %d --bind_ip %s --dbpath %s >> log_%d & \n",replicaName,port,hostname,dbpath,port);
	printf("%s",command);
	system(command);

	
}
/*
 *Clears the instances data
 *
 * */
char* deletePath(char*dbpath){
	char command[100];
	sprintf(command,"rm -rf %s\n",dbpath);
	system(command);
	free(dbpath);
	return NULL;
}
/***
 * kill a specific instance
 *
 *
 *
 */
void killReplicaServer(int processid){
	char command[100];
	sprintf(command,"kill %d \n",processid);
	system(command);
	return;



}
/***
 *Used by server slaves to retieve their assosiate replica name
 *
 *
 */
char*getReplicaName(){
	MPI_Status status;
	char*replicaName=(char*)malloc(sizeof(char)*REPLICA_NAME_MAX);
	MPI_Recv(replicaName,REPLICA_NAME_MAX,MPI_CHAR,MAIN_SERVER_RANK,SERVER_TAG,MPI_COMM_WORLD,&status);
	return replicaName;

}
/***
 *This is every servers mainloop
 *starts the replica server , and then waits for further commands
 *	
 *The commands untill now are...
 *
 *(1->)	COMMAND_SUICIDE on tag SERVER_TAG
 *	This command deletes the dbPath data , causing the mongodb instance to crash(and eventually stop(#TheEasyWay))
 */
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
/***
 *This is every client slave mainloop
 * @NotImplemented
 *
 */
void client_start(char*hostname,int port){
//	printf("CLIENT RUN %d\n",port);
}
/***
 *Triggered by every slave .Here happenes the main split between client and server slaves by slave side
 *
 */
void applyPurpose(int purpose,char*hostname,int port){
	switch(purpose){
		case PURPOSE_SERVER:server_start(hostname,port);break;
		case PURPOSE_CLIENT:client_start(hostname,port);break;
	
	}
}
/****
 *This called by each slave , returning their actual hostnames
 *
 */
char*getHostname(){
	char *hostname=(char*)malloc(sizeof(char)*HOSTNAME_MAXSIZE);
	char path[HOSTNAME_MAXSIZE];
        FILE *fp=popen("/bin/hostname","r");
        while (fgets(path, sizeof(path)-1, fp) != NULL) {
       		sprintf(hostname,"%s", path);
       	}
	return addNull(hostname);

}
/***
 *The initial split between clients and server slaves by server side
 *
 */
int*assignPurposes(argvinfo*user_params,int procsize){
	int*purposes=(int*)malloc(sizeof(int)*procsize);
	purposes[0]=nodeAsMain(0);
	for(int i=1;i<procsize;i++){
		if(i<user_params->server_nodes)purposes[i]=nodeAsServer(i);
                else purposes[i]=nodeAsClient(i);
        }
	return purposes;

}
/***
 *This called in order to generate the list of ascosiations between servers and replicaNames
 */
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
/***
 *Acknowledge Instances ?
 *
 *
 */
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
/***
 * Called by the main server , keeps the clock . after 10 seconds commands every slave to SUICIDE
 */
void run(int my_rank,int p,int *ports){
	system("sleep 10");
	int command=COMMAND_SUICIDE;
	for(int i=1;i<=p;i++){
		MPI_Send(&command,1,MPI_INT,i,SERVER_TAG,MPI_COMM_WORLD);
		printf("SERVER %d SENT KILL ON %d(%d)\n",my_rank,i,ports[i]);
	}

}
/*
 *classic itoa implementation
 * accepts a number , returns it as string in buffer
 * @Note the caller has the responsibillity to free this buffer
 */
char*itoa(int n){
	char*str=(char*)malloc(sizeof(char)*INT_MAX_STRING);
	sprintf(str,"%d",n);
	return str;

}
/***
 *classic itoa with reuseable buffers
 *@Note if the buffer is smaller that needed , SEGFAULT may be generated
 *@Note use the safe itoa instead
 */
char *itoa_buff(char*buff,int n){
	sprintf(buff,"%d",n);
	return buff;
}
/***
 *
 *
 *
 */
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
		argvinfo*user_params=parseargv(argc,argv,p);			//parse user arguments 
		hosts=receiveHostnames(p);					//receive hostnames from slaves
		ports=generatePorts(p);						//generate ports and sent the into the servers
		purposes=assignPurposes(user_params,p);				//sent in every server their purpise
		

		replicaNames=sentReplicaNames(user_params);			//sent in each server their replica name
		
		
		ack_instances(user_params,					//acknowledge instances 
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
