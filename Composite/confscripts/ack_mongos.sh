mongo --port 27030 --eval 'rs.initiate({_id:"crs0",configsvr:true,members:[{_id: 0,host: "127.0.0.1:27030"},{_id: 1,host: "127.0.0.1:27031"},{ _id: 2,host: "127.0.0.1:27032"}]})'



