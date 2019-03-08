mongod --configsvr --replSet crs0 --port 27030 --bind_ip 127.0.0.1 --dbpath srv/mongodb/crs0-0 &
mongod --configsvr --replSet crs0 --port 27031 --bind_ip 127.0.0.1 --dbpath srv/mongodb/crs0-1 &
mongod --configsvr --replSet crs0 --port 27032 --bind_ip 127.0.0.1 --dbpath srv/mongodb/crs0-2 &


echo -e "name\treplset\tnum\tport"
echo -e "mongod\tcrs0\t0\t27030"
echo -e "mongod\tcrs0\t1\t27031"
echo -e "mongod\tcrs0\t2\t27032"

