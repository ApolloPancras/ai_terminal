cd /Users/apollo/workspace/cnNetTool
sudo /opt/anaconda3/envs/lottery/bin/python setDNS.py --best-dns-num 2 
sudo killall -HUP mDNSResponder
sudo sed -i '' '8,$d' /etc/hosts
cd /Users/apollo/workspace/cnNetTool
sudo /opt/anaconda3/envs/lottery/bin/python setHosts.py -num 1 --max 90
sudo killall -HUP mDNSResponder
