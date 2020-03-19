IP=$1
echo "Grabbing Key for $1"
if [ -z `ssh-keygen -F "$IP" 2> /dev/null` ]; then
  ssh-keyscan -H "$IP" >> ~/.ssh/known_hosts
fi
