
## Getting Started

1. Navigate to folder on your hdd

2. clone the repository  

   `git clone https://github.com/Castronova/topkapi-modeling.git`

3. initialize and update submodules (i.e. pytopkapi repository)

   `git submodule init`  
   `git submodule update`  



## Common Git Operations

**NOTE: NEVER USE `--force` in any push commands!**

### Adding a new file to the repository

* create new file in directory

* view the status of your repository

   `git status`

* add the file to git tracking

   `git add my-file-name`

* stage the file for commit   

   `git commit -m "this is my commit message.  Describe what changes have been made to the file"`

* push the file(s) to the server  
   
   `git push origin master`

### Modified files

* list all modified files

   `git status`  
  
   `git status -uno`

* stage all modified files 

   `git commit -am "a message explaining the changes that I've made"`

* push changed files to server

   `git push`

### Update local files with those on server  

   `git pull`

### Revert local file to the state on server  

   `git checkout my-file-name`



