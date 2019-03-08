#include <mpi.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
int main(int argc,char*argv[]){

	int my_rank;
	int p;
	int source;
	int dest;
	int tag=0;
	int provided;
	char message[100];
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
		if(fp==NULL)exit(1);
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

		printf("Size of cluster %d",p);
		
		for(source=1;source<p;source++){
			MPI_Recv(message,100,MPI_CHAR,source,tag,MPI_COMM_WORLD,&status);
			printf("%s\n",message);
		}
	}
		
	MPI_Finalize();
	fflush(stdout);
}
