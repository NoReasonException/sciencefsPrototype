mongo --port 27017 --eval 'rs.initiate({_id:"rs0",members:[{_id: 0,host: "127.0.0.1:27017"},{_id: 1,host: "127.0.0.1:27018"},{ _id: 2,host: "127.0.0.1:27019"}]})'
mongo --port 27020 --eval 'rs.initiate({_id:"rs1",members:[{_id: 0,host: "127.0.0.1:27020"},{_id: 1,host: "127.0.0.1:27021"},{ _id: 2,host: "127.0.0.1:27022"}]})'


