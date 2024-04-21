# How to Contribute

Thank you for considering contributing to our project! Whether you're picking up an existing issue or creating one yourself, your efforts are appreciated.

## Steps to Contribute

### 1. Fork the Repository

Click on the "Fork" button at the top right corner of this repository to create your own fork.

### 2. Clone the Repository

Clone your forked repository to your local system using the following command:

```bash
git clone https://github.com/{YourUsername}/Dynamic-Report-Scheduler.git
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

### 4. Develope and Commit
Create your feature branch (e.g., feature/add-data-size, hotfix/fix-date)
```bash
git checkout -b feature/feature-x
```
Stage the changes using
```bash
git add .
```
Commit your changes with a clear and concise message using imperative verbs::
```bash
git commit -m 'Your commit message'
```

## Pull Changes from upstream
Pull Changes from main, develop branchs of upstream
```bash
git pull upstream main develop
```

## Pull Changes from upstream
Take the commits in your `feature-x` branch and apply them to the head of the `develop` branch.\
It update the feature-x with latest commits of `develop`.

```bash
git rebase develop feature/feature-x
```
If conflicts arise during the rebase process, resolve them, stage the changes, and continue the rebase:
```bash
git add .
git rebase --continue
```
Resolve conflicts and Push all changes to your forked repository:
```bash
git push origin feature/feature-x
```
### 5. Create a Pull Request
Navigate to your forked repository on GitHub and create a pull request. Mention the issue it will close (e.g., Closes issue #12)Provide a clear and detailed description of your changes, explaining the problem you're solving and the solution you're proposing.

Your pull request will undergo review, and any necessary feedback will be provided. Thank you for your valuable contribution!
