### **Tested in Ubuntu 20.04.6 LTS**

### Install Miniconda

- Create a directory where minicaonda will be installed
```bash
sudo mkdir -p ~/miniconda3
```
- Download latest miniconda
```bash 
sudo wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
```
- Run the install script
```bash
sudo bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
```
- Delete the intall script
```bash   
sudo rm -rf ~/miniconda3/miniconda.sh
```
- After installing, initialize your newly-installed Miniconda
```bash   
sudo ~/miniconda3/bin/conda init bash
```

### Setting up the Conda Environment

To recreate the Conda environment, follow these steps:

```bash
conda env create --name sched --file requirements.yml
```
Go to the conda environment
```bash
conda activate sched
```

## To create a screen session to run the scheduler program uninterrupted

Create screen named `sched_v1`
```bash
screen -S sched_v1
```
See all screen
```bash
screen -ls
```
Attach to the ```sched_v1``` named screen session
```bash
screen -r sched_v1
```

