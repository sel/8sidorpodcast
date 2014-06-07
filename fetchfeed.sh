#!/bin/bash

curl -LSs "http://pod8sidor.herokuapp.com" | tidy -q -xml -indent
