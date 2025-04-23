# OSFinalProject
 OS Term Project - CSI: 4500

 Team ValaschoKauppilaBerman


# Quickstart Instructions

Move the required scripts ("setup.sh", "search", "update_embeddings") and folder ("py_src") into the directory ~/bin/

Assuming that Python 3.12 is already installed:

1. First, run the setup.sh script. This will setup the Python virtual environment and install the Python dependencies. Error messages may be displayed if your system is missing other dependencies which Python needs. In this case, install those and then run the script again.

2. (OPTIONAL) If you wish to specify a custom list of directories to be supported by the search, create a file named 'custom_dirs.txt' in the location ~/os_search/custom_dirs.txt. If possible, try to use absolute paths to the directories to be searched. Otherwise, relative filepaths will be relative to the user's home directory ~/, which may not be the user's intention. Write each directory path on a separate line, with the only separator being the newline character, (DO NOT USE COMMAS OR OTHER SYMBOLS TO SEPARATE LIST ENTRIES IN THE TEXT FILE). If a custom list of directories is not specified, the directories which will be searched are the user's Documents, Downloads, and Desktop directories.

3. Run the command "update_embeddings" in the terminal. (It may be necessary to execute "chmod +x <file_name>" before execution.) Please note that running this command may take a while, especially the first time that it is run.

4. Now, you can run the command "search" in the terminal to search for information from your files using retrieval augmented generation. When you are done, type "quit" or "exit" to end the session.

5. (OPTIONAL) To automatically update the vector database, run the command "crontab -e" and use the text editor to add the line "@reboot /<absolute_path_to>/update_embeddings". Now, the update_embeddings script will run automatically on startup to update the vector database.