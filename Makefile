PYTHON=python3.6

install_python_repo:
	sudo add-apt-repository -y ppa:fkrull/deadsnakes
	sudo apt-get update

install_python:
	sudo apt-get install -y $(PYTHON) $(PYTHON)-dev $(PYTHON)-venv cython
	sudo apt-get install -y build-essential libssl-dev libffi-dev openssl

venv_init:
	export XXHASH_FORCE_CFFI=1
	if [ ! -d "venv" ]; then $(PYTHON) -m venv venv ; fi;
	bash -c "source venv/bin/activate && \
		pip install --upgrade wheel pip setuptools && \
		pip install --upgrade --requirement requirements.txt"