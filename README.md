## Sound recording studio expert

### Description
This is an expert system (telegram bot) on how to provide a home sound recording studio, 
based on Bayesian belief network.

### How to run
* Install python:
```bash
    $ make install_python
```

* Create/update virtual environment with all necessary libraries by this commands:
```bash
    $ make venv_init
```

* Activate the virtual environment by command:
```bash
    $ source venv/bin/activate
```

* Create new file `mics.py` and paste your personal token:
```python
    token = 'PASTE_YOUR_TOKEN_HERE'
```

* Run this bot:
```bash
    $ make run
```
