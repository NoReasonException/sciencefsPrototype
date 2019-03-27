#include <mpi.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include "cjson/cJSON.h"
#define HOSTNAME_MAXSIZE 255
#define COMMAND_MAXSIZE  1000
#define MONGO_ROUTER_ADDSHARD_COMMAND_MAXSIZE 500
#define MONGOS_ROUTER_START_COMMAND_MAXSIZE 500
#define RICH_STRING_MAX_PAYLOAD 255
#define ACK_REPLICAS_COMMAND_MAXSIZE 1000
#define RICH_STRING_METADATA_OFFSET 1
#define SAFE_PADDING 1

#define SERVER_START_PADDING 1
#define CONF_SERVER_START_PADDING(s_argvinfo) s_argvinfo->server_nodes+SERVER_START_PADDING


#define every_replica_server(s_argvinfo, i) (int i=1;i<=s_argvinfo->server_nodes;i++)
#define every_conf_server(s_argvinfo, i) (int i=s_argvinfo->server_nodes+SERVER_START_PADDING;i<=s_argvinfo->server_nodes+s_argvinfo->config_server_nodes;i++)
#define every_client_server(s_argvinfo, i) (int i=s_argvinfo->server_nodes+s_argvinfo->conf_server_nodes;i<=s_argvinfo->server_nodes+s_argvinfo->config_server_nodes+s_argvinfo->client_nodes;i++)

#define every_replica_server_set(s_argvinfo, i,j) (int i=0,j=SERVER_START_PADDING;j<=s_argvinfo->server_nodes;j+=s_argvinfo->replicas_per_shard,i++)
#define every_conf_replica_server_set(s_argvinfo, i,j) (int i=0,j=s_argvinfo->server_nodes+SERVER_START_PADDING;j<s_argvinfo->server_nodes+s_argvinfo->config_server_nodes;i+=1,j+=s_argvinfo->config_replicas_per_shard)




#define PURPOSE_SERVER 	0
#define PURPOSE_CLIENT 	1
#define PURPOSE_MAIN	2
#define PURPOSE_CONF 	3

#define MAIN_SERVER_RANK 0

#define SERVER_TAG	10
#define CLIENT_TAG	11
#define REPLICA_NAME_MAX 100

#define COMMAND_SUICIDE	1

#define INT_MAX_STRING 10


#define NUMBER_OF_REPLICA_SETS(s_argvinfo) (s_argvinfo->server_nodes+1)/s_argvinfo->replicas_per_shard
#define NUMBER_OF_CONFIG_REPLICA_SETS(s_argvinfo) (s_argvinfo->config_server_nodes+1)/s_argvinfo->config_replicas_per_shard



cJSON* _rs_replica_initiate_buildJson(char*replicaName,char**hosts,int*ports,int startOffset,int numberOfServers);
cJSON* _rs_configsvr_initiate_buildJson(char*replicaName,char**hosts,int*ports,int startOffset,int numberOfServers);




struct argv;
typedef struct argv argvinfo;



void * memcpy_slow ( void * destination, const void * source, size_t num ){
	for (int i = 0; i <num ; ++i)((char*)destination)[i]=((char*)source)[i];
	return destination;
}

union richmsg{
	char size;
	char payload[RICH_STRING_MAX_PAYLOAD];
};
/*****
*Rich String constructor
*
*
*/
char*richmsg_compose(char*str){
	

	union richmsg*retval=(union richmsg*)malloc(sizeof(union richmsg));
	retval->size=strlen(str);
	memcpy_slow(retval->payload+RICH_STRING_METADATA_OFFSET,str,retval->size);
	return (char*)retval;

}
char*richmsg_decompose(char*msg){
	char*retval=(char*)malloc(sizeof(char)*RICH_STRING_MAX_PAYLOAD);
	union richmsg *decompose=(union richmsg*)msg;
	memcpy_slow(retval,decompose->payload+RICH_STRING_METADATA_OFFSET,decompose->size);
	retval[decompose->size]='\0';
	return retval;

}
/***
*Deprecated , copies garbage sometimes
*Copies a richmsg
*/
char*richmsg_cp(char*msg){
	return richmsg_compose(((union richmsg *)msg)->payload+RICH_STRING_METADATA_OFFSET);
}
int richmsg_size(char*msg){
	return ((union richmsg*)msg)->size+RICH_STRING_METADATA_OFFSET;
}


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
 	popen(hostname) returns something of the form <hostname>\n\0 and this produces errors
 *
 */
char*replaceNewLineWithNull(char*str){
	for (int i = 0; i < strlen(str); ++i)
	{
		if(str[i]=='\n'){
			str[i]='\0';
			break;
		}
		else if(str[i]=='\0')break;
	}
	return str;
}


/****
 *	Concat of 2 buffers
 *	@WARN -> the responsibillity of freeing the buffer is on caller
 *
 */
char *concat(char*first,char*second){
	char*retval=(char*)malloc(sizeof(char)*(strlen(first)+strlen(second)+1));
	memcpy_slow(retval,first,strlen(first));
	memcpy_slow(retval+strlen(first),second,strlen(second)+1);

	return retval;
	

}
char*main_server_not_applicable(char**ptr){
	free(*ptr);
	*ptr=concat("MAIN_SERVER_NOT_APPLICABLE","");
	return *ptr;
}

/***
 *	The user arguments struct
 *	
 *	the .parseargv routine takes the argc/argv from the main routine returns this nice and clean struct
 *
 */
struct argv{
	unsigned short server_nodes;				//the amount of server nodes
	unsigned short replicas_per_shard;			//replicas per shards(obviously)
	unsigned short config_server_nodes;			//the amount of server nodes
	unsigned short config_replicas_per_shard;	//replicas per shards(obviously)
	unsigned short client_nodes;				//the amount of client nodes
	char*prefix;								//mongo executables folder (default /usr/bin)
	//char*benchmark_scripts_prefix				//benchmarks_scripts_prefix(defailt $pwd)

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
	param->prefix=concat("/usr/bin","");
	param->config_server_nodes=3;
	param->config_replicas_per_shard=3;



	procsize-=4;
	param->server_nodes=(int)procsize/2;
	param->client_nodes=(int)procsize/2;
	param->replicas_per_shard=2;

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
		if(!strcmp("--serv",argv[i])){
			retval->server_nodes=strtol(argv[i+1],NULL,10);
		}
		else if(!strcmp("--cli",argv[i])){
			retval->client_nodes=strtol(argv[i+1],NULL,10);
		}
		else if(!strcmp("--rps",argv[i])){
			retval->replicas_per_shard=strtol(argv[i+1],NULL,10);
		}
		else if(!strcmp("--prefix",argv[i])){
			free(retval->prefix);
			retval->prefix=concat(argv[i+1],"");
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
	void **retval=malloc(n*sizeof(char*)+SAFE_PADDING);
	if(!retval)printf("[WARN]Null returned at alloc2D , it will crash maybe due to LOWMEM");
	for (i=0;i<n+SAFE_PADDING;i++)
	{
		retval[i]=(char*)malloc(typesize*(m+SAFE_PADDING));
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
	void *releaseptr;
	char **hosts=(char**)alloc2D(procsize,HOSTNAME_MAXSIZE,sizeof(char));
	for(source=1;source<procsize;source++){
		MPI_Recv(hosts[source],HOSTNAME_MAXSIZE,MPI_CHAR,source,tag,MPI_COMM_WORLD,&status);
		hosts[source]=richmsg_decompose(releaseptr=hosts[source]);
		free(releaseptr);
    	//printf("RECEIVED %s\n",richmsg_decompose(hosts[source]));
    }
	hosts[0]=main_server_not_applicable(&hosts[0]);
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
	printf("Server %d on purpose %d\n",rank,purpose);
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
int nodeAsConfig(int rank){
	return nodeAs(rank,PURPOSE_CONF);

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
void startReplicaServer(argvinfo*user_params,char*hostname,int port,char*replicaName,char*dbpath){
	char command[1000];
	sprintf(command,"%s/mongod --shardsvr --replSet %s --port %d --bind_ip %s --dbpath %s >> log_%d & \n",user_params->prefix,replicaName,port,hostname,dbpath,port);
	//printf("%s",command);
	system(command);	
}

/***
 *Given the hostname , port , replica name and dbPath , this routine starts the mongod instances 
 *
 */
void startConfReplicaServer(argvinfo*user_params,char*hostname,int port,char*replicaName,char*dbpath){
	char command[1000];
	sprintf(command,"%s/mongod --configsvr --replSet %s --port %d --bind_ip %s --dbpath %s >> log_%d & \n",user_params->prefix,replicaName,port,hostname,dbpath,port);
	//printf("%s",command);
	system(command);	
}
/*
 *Clears the instances dataa
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
void server_start(argvinfo*user_params,char*hostname,int port){
	MPI_Status status;
    int receiveCommand;
	char *dbpath=setupPath(hostname,port);
	int isDead=0;
	
	char*replicaName=getReplicaName();
	startReplicaServer(user_params,hostname,port,replicaName,dbpath);
        
	while(1){
		if(isDead)break;
		MPI_Recv(&receiveCommand,sizeof(int),MPI_INT,MAIN_SERVER_RANK,SERVER_TAG,MPI_COMM_WORLD,&status);
                switch(receiveCommand){
                	case COMMAND_SUICIDE:{
				//printf("THREAD %d receive : SUICIDE\n",port);
				deletePath(dbpath);
				
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
	system("sleep 20");
	char buff_populate[COMMAND_MAXSIZE];
	char buff_query[COMMAND_MAXSIZE];
	sprintf(buff_populate,"python3 po_populate.py 200 >> %s_%d_populate_logs",hostname,port);
	sprintf(buff_query,"python3 po_query.py 0.9 0.001 >> %s_%d_query_logs",hostname,port);
	system(buff_populate);
	system(buff_query);

	



}

/***
 *This is every confs servers slave mainloop
 * @NotImplemented
 *
 */
void server_conf_start(argvinfo*user_params,char*hostname,int port){
	MPI_Status status;
    int receiveCommand;
	char *dbpath=setupPath(hostname,port);
	int isDead=0;
	
	char*replicaName=getReplicaName();
	startConfReplicaServer(user_params,hostname,port,replicaName,dbpath);
        
	while(1){
		if(isDead)break;
		MPI_Recv(&receiveCommand,sizeof(int),MPI_INT,MAIN_SERVER_RANK,SERVER_TAG,MPI_COMM_WORLD,&status);
                switch(receiveCommand){
                	case COMMAND_SUICIDE:{
				//printf("THREAD %d receive : SUICIDE\n",port);
				deletePath(dbpath);
				
				isDead=1;
				break;
				}
            }
        }
        
}
/***
 *Triggered by every slave .Here happenes the main split between client and server slaves by slave side
 *
 */
void applyPurpose(argvinfo*user_params,int purpose,char*hostname,int port){
	switch(purpose){
		case PURPOSE_SERVER:server_start(user_params,hostname,port);break;
		case PURPOSE_CONF:server_conf_start(user_params,hostname,port);break;
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
    char *rich_message;
    FILE *fp=popen("/bin/hostname","r");


    while (fgets(path, sizeof(path)-1, fp) != NULL) {
    	sprintf(hostname,"%s", path);
    }

    rich_message=richmsg_compose(replaceNewLineWithNull(hostname));
    free(hostname);
	return rich_message;

}
/***
 *The initial split between clients and server slaves by server side
 *
 */
int*assignPurposes(argvinfo*user_params,int procsize){
	int*purposes=(int*)malloc(sizeof(int)*procsize);
	purposes[0]=nodeAsMain(0);
	for(int i=1;i<procsize;i++){
		if(i<=user_params->server_nodes)purposes[i]=nodeAsServer(i);
        else if(i<=user_params->server_nodes+user_params->config_server_nodes)purposes[i]=nodeAsConfig(i);
        else purposes[i]=nodeAsClient(i);
    }
	return purposes;

}
/***
 *This called in order to generate the list of ascosiations between servers and replicaNames
 */
char** sentReplicaNames(argvinfo*user_args,int procsize){
	char replicaPrefix[4]="rs_";
	char tmp_buffer[100];
	char *replicaBuffer;
	char **replicaNames=alloc2D(procsize,REPLICA_NAME_MAX,sizeof(char));
	

	/***
		Replica Names for shards

	*/

	printf("ASC REPLICAS\n");
	for(int i=SERVER_START_PADDING,cnt=0;i<=user_args->server_nodes;i+=user_args->replicas_per_shard,cnt+=1){
		sprintf(tmp_buffer,"%d_M",cnt);
		replicaBuffer=concat(replicaPrefix,tmp_buffer);
		for(int j=0;j<user_args->replicas_per_shard&&j+i<=user_args->server_nodes;j++){
			memcpy_slow(replicaNames[i+j],replicaBuffer,strlen(replicaBuffer));
			printf("%s on rack %d\n",replicaNames[i+j],i+j);
			MPI_Send(replicaBuffer,strlen(replicaBuffer),MPI_CHAR,i+j,SERVER_TAG,MPI_COMM_WORLD);
			//free(replicaBuffer); MPI_Send takes ownership of the buffer

		}
		
	}
	/***
		Replica Names for configuration servers

	*/
	printf("ASC CONF REPLICAS\n");
	for(int i=user_args->server_nodes+SERVER_START_PADDING,cnt=0;i<=(user_args->server_nodes+user_args->config_server_nodes);i+=user_args->config_replicas_per_shard,cnt+=1){
		sprintf(tmp_buffer,"%d_CM",cnt);
		replicaBuffer=concat(replicaPrefix,tmp_buffer);
		for(int j=0;j<user_args->config_replicas_per_shard&&j+i<=user_args->server_nodes+user_args->config_server_nodes;j++){
			memcpy_slow(replicaNames[i+j],replicaBuffer,strlen(replicaBuffer));
			printf("%s on rack %d\n",replicaNames[i+j],i+j);
			MPI_Send(replicaBuffer,strlen(replicaBuffer),MPI_CHAR,i+j,SERVER_TAG,MPI_COMM_WORLD);
			//free(replicaBuffer); MPI_Send takes ownership of the buffer

		}
		
	}
	printf("END\n");
	replicaNames[0]=main_server_not_applicable(&replicaNames[0]);
	return replicaNames;

}

void evaluate_rs_initiate(argvinfo*user_params,char*primary_hostname,int port,char*rs_initiate_json){
	char buff[5000];
	sprintf(buff,"%s/mongo --host %s --port %d --eval 'rs.initiate(%s)' \0",user_params->prefix,primary_hostname,port,rs_initiate_json);
	//printf("%s",buff);
	system(buff);
}
/***
 *Acknowledge server Instances 
 *		Composes the rs.initiate({ ... }) json , and acknowledges each replicas primary with it!
 *
 *
 */
void ack_instances(argvinfo*user_params,char**hostnames,int*ports,int*purposes,char**replicaNames){
	char curr_replica[REPLICA_NAME_MAX] = "NONE";
	int curr_port;
	for(int i=1;i<user_params->server_nodes;i++){
		if(strcmp(curr_replica,replicaNames[i])){
			memcpy_slow(curr_replica,replicaNames[i],strlen(replicaNames[i]));
			curr_port=ports[i];
			printf("%s is %d at index %d with replicas %d\n",curr_replica,curr_port,i,user_params->replicas_per_shard);	
			evaluate_rs_initiate(user_params,hostnames[i],ports[i],cJSON_Print(_rs_replica_initiate_buildJson(replicaNames[i],hostnames,ports,i,user_params->replicas_per_shard)));
			printf("%s",cJSON_Print(_rs_replica_initiate_buildJson(replicaNames[i],hostnames,ports,i,user_params->replicas_per_shard)));
		
		}
	}	
}

/***
 *Acknowledge conf Instances 
 *		Composes the rs.initiate({ ... }) json , and acknowledges each replicas primary with it!
 *
 *
 */
void ack_config_instances(argvinfo*user_params,char**hostnames,int*ports,int*purposes,char**replicaNames){
	char curr_replica[REPLICA_NAME_MAX] = "NONE";
	int curr_port;
	for(int i=user_params->server_nodes+SERVER_START_PADDING;i<=user_params->server_nodes+user_params->config_server_nodes;i++){
		if(strcmp(curr_replica,replicaNames[i])){
			memcpy_slow(curr_replica,replicaNames[i],strlen(replicaNames[i]));
			curr_port=ports[i];	
			evaluate_rs_initiate(user_params,hostnames[i],ports[i],cJSON_Print(_rs_configsvr_initiate_buildJson(replicaNames[i],hostnames,ports,i,user_params->config_replicas_per_shard)));
		
		}
	}	
}
/***
 * Called by the main server , keeps the clock . after 10 seconds commands every slave to SUICIDE
 */
void run(int my_rank,int p,int *ports){
	system("sleep 10000");
	int command=COMMAND_SUICIDE;
	for(int i=1;i<=p+1;i++){
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
 *Creates a JSON in order to acknowledge every replica set where it belongs
 *	It returns a cJSON object representing the following json format 
 *	 	{
 *		    _id : <replicaSetName>,
 *		    members: [
 *		      { _id : 0, host : "host-0:host-0-port" },
 *		      { _id : 1, host : "host-1:host-1-port" },
 *		      { _id : 2, host : "host-2:host-2-port" },
 *		    ]
 *		}
 *
 *
 */
cJSON* _rs_replica_initiate_buildJson(char*replicaName,char**hosts,int*ports,int startOffset,int numberOfServers){
	cJSON *rs_initiate=					cJSON_CreateObject();
	cJSON *members_array=				cJSON_CreateArray();
	cJSON *_id_value=					cJSON_CreateString(replicaName);
	cJSON *member_iter_obj				=NULL;
	cJSON *member_iter_id				=NULL;
	cJSON *member_iter_hoststring		=NULL;
	char  *member_host_construct_buff	=(char*)malloc(sizeof(char)*(INT_MAX_STRING+HOSTNAME_MAXSIZE));
	char  *member_port_construct_buff	=itoa(0);




	cJSON_AddItemToObject(rs_initiate,"_id",_id_value);
	cJSON_AddItemToObject(rs_initiate,"members",members_array);

	for (int i = startOffset; i < startOffset+numberOfServers; i++)
	{

		member_iter_obj=cJSON_CreateObject();
		member_iter_id=cJSON_CreateNumber(i);				//convert it to cJSON_String
		cJSON_AddItemToObject(member_iter_obj,"_id",member_iter_id);				//pass it into main object

		//create the hostname:port string
		sprintf(member_host_construct_buff,"%s:%s",hosts[i],itoa_buff(member_port_construct_buff,ports[i]));
		member_iter_hoststring=cJSON_CreateString(member_host_construct_buff);
		cJSON_AddItemToObject(member_iter_obj,"host",member_iter_hoststring);


		cJSON_AddItemToArray(members_array,member_iter_obj);



	}

	return rs_initiate;
}
char**get_config_master_hosts(argvinfo*user_params,char**hosts){
	char**retval=alloc2D(NUMBER_OF_CONFIG_REPLICA_SETS(user_params),HOSTNAME_MAXSIZE,sizeof(char));
	int k;
	for every_conf_replica_server_set(user_params,k,j){
		sprintf(retval[k],"%s",hosts[j]);
		printf("%s\n",retval[k]);
	}
	return retval;

}
/***
	Currently only one config cluster supported(with as many shards as you want) , we always use the first config shard

*/
void activate_query_router_mongos(argvinfo*user_params,char**replicaNames,char**hosts,int*ports){
	char buff[1000];
	for every_conf_server(user_params,i){
		sprintf(buff,"%s/mongos --configdb %s/%s:21421 --bind_ip nre-Aspire-F5-573G --port 20000 >> mongos_log &",user_params->prefix,replicaNames[i],hosts[i],ports[i]);
		printf("%s\n",buff);
		system(buff);
		break;
	}
	system("sleep 10");
	for every_replica_server_set(user_params,i,j){
		sprintf(buff,"%s/mongo --host nre-Aspire-F5-573G --port 20000 --eval 'sh.addShard(\"%s/%s:%d\")' >> addShard_log f& ",user_params->prefix,replicaNames[j],hosts[j],ports[j]);
		printf("%s\n",buff);
		system(buff);
	}


}
cJSON* _rs_configsvr_initiate_buildJson(char*replicaName,char**hosts,int*ports,int startOffset,int numberOfServers){
	cJSON* retval=_rs_replica_initiate_buildJson(replicaName,hosts,ports,startOffset,numberOfServers);
	cJSON* confsvr_option=cJSON_CreateTrue();
	cJSON_AddItemToObject(retval,"configsvr",confsvr_option);
	return retval;

}
int main(int argc,char*argv[]){

	int my_rank;
	int p;
	int source;
	int dest=MAIN_SERVER_RANK;
	int tag=0;
	int provided;



	char *local_hostname;
	int port=getRandomPort();
	int purpose=0;




	FILE *fp;
	int mainServer=0;
	MPI_Status status;
	MPI_Init(&argc,&argv);

	MPI_Comm_rank(MPI_COMM_WORLD,&my_rank);
	MPI_Comm_size(MPI_COMM_WORLD,&p);
	argvinfo*user_params=parseargv(argc,argv,p);                    //parse user arguments 
	
	/*
	 * Secondary Processors
	 */
	if(my_rank!=0){

		char*sentbuffer;
		char*replicaName[REPLICA_NAME_MAX];

		sentbuffer=getHostname();
		local_hostname=richmsg_decompose(sentbuffer);						//copy the hostname because MPI destroys the buffer



		MPI_Send(sentbuffer,richmsg_size(sentbuffer),MPI_CHAR,dest,tag,MPI_COMM_WORLD); 		//sent my hostname to main
		MPI_Recv(&port,1,MPI_INT,mainServer,tag,MPI_COMM_WORLD,&status);			//receive my port number to main
		MPI_Recv(&purpose,1,MPI_INT,mainServer,tag,MPI_COMM_WORLD,&status);			//receive purpose

		applyPurpose(user_params,purpose,local_hostname,port);
	



		printf("RANK %d DEAD \n",my_rank);
		//free(hostname);

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

		printf("argvinfo server_nodes %d\n",user_params->server_nodes);


		hosts=receiveHostnames(p);								//receive hostnames from slaves
		ports=generatePorts(p);									//generate ports and sent the into the servers
		purposes=assignPurposes(user_params,p);					//sent in every server their purpise
		

		replicaNames=sentReplicaNames(user_params,p);				//sent in each server their replica name
		

		
		
		
		//get_config_master_hosts(user_params,hosts);
		
		system("sleep 10");	


		ack_instances(user_params,							//acknowledge instances 
				hosts,
				ports,
				purposes,
				replicaNames);

		ack_config_instances(user_params,					//acknowledge configuration instances 
				hosts,
				ports,
				purposes,
				replicaNames);

		system("sleep 10");

		printf("START MONGOS ROUTER\n");


		printf("host\t\tport\track\tpurpose\treplica\t\n");
		for (int i=1;i<p;i++){
			printf("%s\t%d\t%d\t%d\t%s\n",hosts[i],ports[i],i,purposes[i],replicaNames[i]);
		
		}
		activate_query_router_mongos(user_params,replicaNames,hosts,ports);






		//_rs_replica_initiate_buildJson("rs0_M",hosts,ports,3);
 
		run(my_rank,user_params->server_nodes+user_params->config_server_nodes,ports);



		printf("MAIN DEAD \n");
		free2D(hosts,p);
		free2D(replicaNames,user_params->server_nodes);
		free(ports);
		free(purposes);
	}
		
	MPI_Finalize();
	fflush(stdout);
}
	
