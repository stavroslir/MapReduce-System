# Setting Up a Local NFS Server on Mac

Create the Directory to Share
    mkdir -p /Users/<yourusername>/nfs
    
# Update the NFS Exports File
The NFS exports file /etc/exports defines the directories that will be shared out and what IP addresses have access to them.
Open the exports file in a text editor with superuser permissions. If the file does not exist, this command will create it:
    sudo nano /etc/exports

In the open file, add the following line, replacing <yourusername> with your actual username. This line will share the directory you created with any machine on your local network:
    /Users/<yourusername>/nfs -alldirs -mapall=<yourusername> -network 192.168.0.0 -mask 255.255.0.0
Save and close the file.


# Start the NFS Server
On macOS, the NFS server can be started and stopped using the nfsd command. Start the server with the following command:
    sudo nfsd start

If you make changes to the /etc/exports file while the server is running, you can update the running server with this command:

    sudo nfsd update

# Verify the NFS Share
You can verify that your directory is being shared by running this command:
    showmount -e
The output should include the directory you are sharing.


# Apply the necessary yaml file to create PV and PVClaims

    kubectl apply -f pers-volume.yaml
    kubectl apply -f pers-volume-cl.yaml
