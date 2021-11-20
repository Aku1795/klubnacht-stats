setup-env:
	pip install virtualenv;
	python3 -m venv venv;
	source venv/bin/activate;
	pip install -r requirements.txt;

format: 
	source "venv/bin/activate";
	python -m black . ;