# How to Contribute

Thank you for considering contributing to our project! Whether you're picking up an existing issue or creating one yourself, your efforts are appreciated.

## Steps to Contribute

### 1. Fork the Repository

Click on the "Fork" button at the top right corner of this repository to create your own fork.

### 2. Clone the Repository

Clone your forked repository to your local system using the following command:

```bash
git clone https://github.com/YourUsername/Dynamic-Report-Scheduler.git
```
### 3. Add Upstream Remote
To keep your local repository updated with the latest changes from the original repository, add an upstream remote:
```bash
git remote add upstream https://github.com/ZareefJafar/Dynamic-Report-Scheduler.git
```
See if upstream is added
```bash
git remote -v
```

### 4. Commit and Push Changes
Before making any changes, ensure your local repository is up to date with the upstream:

```bash
git pull upstream
```
Create your feature branch
```bash
git checkout -b feature-x
```
Make your changes, commit them with a clear message:
```bash
git commit -m 'Your commit message'
```
Rebase changes from remote develop branch
```bash
git fetch upstream
git rebase upstream/develop
```

Push your changes to your forked repository:
```bash
git push 
```
### 5. Create a Pull Request
Navigate to your forked repository on GitHub. GitHub will prompt you to create a pull request. Provide a clear description of your changes and submit the pull request.

Your pull request will be reviewed, and any necessary feedback will be provided. Thank you for contributing!
