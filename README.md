# Code Bench Backend Repository 
Click the Fork Button at the Top. You will have your version of this repository at `your-username/CodeBench-Backend`

Make sure you have Git Installed. 

To clone the forked repository in your PC, go to your command line and run 
```
git clone https://github.com/your-username/CodeBench-Backend
```

Go to the CodeBench-Backend folder with `cd CodeBench-Backend`
Now run 
```
git remote add upstream https://github.com/hanif-ali/CodeBench-Backend
```
This will later allow you to update your code with changes in mine.

When adding something to the code, create a new branch and do all your work in that branch.
You can create a new branch with `git branch new-branch-name`. For example,
```
git branch login-and-registration 
```
To move to the new branch, run 
```
git checkout new-branch-name
```
You can check which branch you are on with `git branch`

 Do all your work in the new branch and keep commiting your changes.

 To upload your new branch to your remote repository run,
``` 
git push origin new-branch-name
```

 Go to your Github Repository in your browser (https://github.com/your-username/CodeBench-Backend) and go to "Create a Pull Request" so that I can review and merge your changes with mine.

Whenever updating your code with changes in my code, run 
```
git pull upstream
```