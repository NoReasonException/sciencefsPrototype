mongod --shardsvr --replSet rs0 --port 27017 --bind_ip 127.0.0.1 --dbpath $1/srv/mongodb/rs0-0 &
mongod --shardsvr --replSet rs0 --port 27018 --bind_ip 127.0.0.1 --dbpath $1/srv/mongodb/rs0-1 &
mongod --shardsvr --replSet rs0 --port 27019 --bind_ip 127.0.0.1 --dbpath $1/srv/mongodb/rs0-2 &


mongod --shardsvr --replSet rs1 --port 27020 --bind_ip 127.0.0.1 --dbpath $1/srv/mongodb/rs1-0 &
mongod --shardsvr --replSet rs1 --port 27021 --bind_ip 127.0.0.1 --dbpath $1/srv/mongodb/rs1-1 &
mongod --shardsvr --replSet rs1 --port 27022 --bind_ip 127.0.0.1 --dbpath $1/srv/mongodb/rs1-2 &



echo -e "name\treplset\tnum\tport"
echo -e "mongod\trs0\t0\t27017"
echo -e "mongod\trs0\t1\t27018"
echo -e "mongod\trs0\t2\t27019"
echo -e "\n"
echo -e "mongod\trs1\t0\t27020"
echo -e "mongod\trs1\t1\t27021"
echo -e "mongod\trs1\t2\t27022"



