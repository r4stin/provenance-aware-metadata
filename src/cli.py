import click, subprocess, sys, json
from pathlib import Path

@click.group()
def cli():
    pass

@cli.command(help="Generate JSON-LD from metadata/source.yml")
def build():
    subprocess.check_call([sys.executable, "src/build_metadata.py"])

@cli.command(help="Validate JSON-LD against SHACL")
def validate():
    subprocess.check_call([sys.executable, "src/validate_metadata.py"])

@cli.command(help="Sign image via c2patool using claim.json (env-driven keys)")
def sign():
    # Prefer env-driven signer; fallback to built-in dev signer in tool
    subprocess.check_call(["bash", "src/sign_c2pa.sh"])

@cli.command(help="Serve API (FastAPI)")
def serve():
    subprocess.check_call(["uvicorn", "src.api:app", "--reload"])

@cli.command(help="Show signed image manifest info")
def info():
    subprocess.check_call(["c2patool", "data/image.c2pa.jpg", "--info"])

@cli.command(help="Fetch from Wikimedia Commons and build JSON-LD")
@click.option("--title", required=True, help='Commons title, e.g. "File:Leibniz_University_Hannover.jpg"')
def build_from_commons(title):
    subprocess.check_call([sys.executable, "src/fetch_commons.py", title])
    subprocess.check_call([sys.executable, "src/build_metadata.py"])
    subprocess.check_call([sys.executable, "src/validate_metadata.py"])


if __name__ == "__main__":
    cli()
