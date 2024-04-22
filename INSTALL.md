### **Tested in Ubuntu 20.04.6 LTS**

### Install Miniconda

[Installing Miniconda on a headless Linux server](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)

### Setting up the Conda Environment

Download the `requirements.yml` from the repository.

Create the Conda environment named `sched` using `requirements.yml`:

```bash
conda env create --name sched --file requirements.yml
```
Activate the conda environment
```bash
conda activate sched
```

### Runnning the Dynamic-Report-Scheduler
onfigure `creads.db`, then execute the scheduler:

```bash
python3 reportSchedulerPython.py
```

### (Optional) To run as a 24/7 service in linux
[Creating Services](https://www.baeldung.com/linux/create-remove-systemd-services)

