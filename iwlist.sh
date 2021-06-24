#!/bin/bash
# interface de rede wlp3s0
# arquivo executavel:  chmod +x iwlist.sh
for counter in $(seq 1 1000); do sudo iwlist wlp3s0 scan; sleep 5; done
