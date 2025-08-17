#!/bin/bash

# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.12 and required packages
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev

# Create and activate virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Create requirements.txt with the project dependencies
cat > requirements.txt << 'EOF'
alembic>=1.16.4
git+https://github.com/erdewit/eventkit.git
fastapi[standard]>=0.116.1
psycopg>=3.2.9
pydantic>=2.11.7
pydantic-settings>=2.10.1
python-dotenv>=1.1.1
requests>=2.32.4
sqlalchemy>=2.0.42
sqlmodel>=0.0.24
tenacity>=9.1.2
websocket-client>=1.8.0
EOF

# Install pip packages
pip install --upgrade pip
pip install -r requirements.txt

echo "Python environment setup complete!"
