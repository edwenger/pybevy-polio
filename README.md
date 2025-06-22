cargo build

python -m venv venv

source venv/bin/activate

maturin develop --release

python test.py