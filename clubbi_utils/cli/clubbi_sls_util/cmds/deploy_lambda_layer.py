#! /usr/bin/env python

from os import environ
from subprocess import CalledProcessError, check_output, check_call

from argparse import ArgumentParser
from typing import Optional
import hashlib
from pathlib import Path

LAMBDA_LAYER_REVISION_KEY = "LambdaLayerRevision"
LOCK_PATH = Path("Pipfile.lock")


def get_remote_revision(stage: str) -> Optional[str]:
    cmd = f"npx sls info -s {stage} -c lambda_layer.yml --verbose"
    try:
        out_lines = check_output(cmd, shell=True).decode().split("\n")
    except CalledProcessError as e:
        print("Returned -1")
        print(*e.output.decode().split("\n"), sep="\n")
        return None

    revision_line = next(
        (line for line in out_lines if LAMBDA_LAYER_REVISION_KEY in line),
        None,
    )

    if revision_line is None:
        return None

    return revision_line.split(": ")[-1]


def get_local_revision() -> str:
    return hashlib.md5(LOCK_PATH.read_bytes()).hexdigest()


def deploy(stage: str, local_revision: str) -> None:
    env = environ.copy()
    env["LOCK_HASH"] = local_revision
    cmd = f"npx sls deploy -c lambda_layer.yml -s {stage}"
    print(f"runnning sls with '{cmd}' and LOCK_HASH={local_revision}")
    check_call(cmd, shell=True, env=env)


def deploy_lambda_layer(stage: str, force: bool) -> None:
    local_revision = get_local_revision()
    print(f"{local_revision=}")

    if force:
        print("Forcing deploy")
        return deploy(stage, local_revision)

    remote_revision = get_remote_revision(stage)
    print(f"{remote_revision=}")

    if local_revision == remote_revision:
        print("Versions match, lets do nothing!")
        return
    print("Versions doesn't match, lets deploy")
    deploy(stage, local_revision)


def main():
    parser = ArgumentParser()
    parser.add_argument("stage", type=str, help="Layer stage")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    deploy_lambda_layer(args.stage, args.force)
