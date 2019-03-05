#include <mpi.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#define HOSTNAME_MAXSIZE 100
#define every(x, i) (int i=0;i<x;i++)
struct argv;
typedef struct argv argvinfo;


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

int main(int argc,char*argv[]){

	int my_rank;
	int p;
	int source;
	int dest;
	int tag=0;
	int provided;
	char message[1000];
	char path[1000];
	FILE *fp;
	MPI_Status status;
	MPI_Init(&argc,&argv);

	MPI_Comm_rank(MPI_COMM_WORLD,&my_rank);
	MPI_Comm_size(MPI_COMM_WORLD,&p);

	
	/*
	 * Secondary Processors
	 */
	if(my_rank!=0){

		//Retrieve the hostname
		FILE *fp=popen("/bin/hostname","r");
		//if(fp==NULL)exit(1);
		/* Read the output a line at a time - sent to buffer. */
  		while (fgets(path, sizeof(path)-1, fp) != NULL) {
		    sprintf(message,"%s", path);
	 	}
		dest=0;
		//send the buffer to main
		MPI_Send(message,strlen(message)+1,MPI_CHAR,dest,tag,MPI_COMM_WORLD);

	}
	/**
	 * The main processor
	 *
	 * */
	else{
		char**hosts;
		printf("Size of cluster %d\n",p);
		argvinfo*user_params=parseargv(argc,argv);	
		hosts=receiveHostnames(p);
		for(int i=1;i<p;i++){
			printf("%s\n",hosts[i]);
		}
		free2D(hosts,p);
	}
		
	MPI_Finalize();
	fflush(stdout);
}
