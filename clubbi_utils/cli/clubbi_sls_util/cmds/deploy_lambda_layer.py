#! /usr/bin/env python

from os import environ
from subprocess import CalledProcessError, SubprocessError, check_output, PIPE

from argparse import ArgumentParser
from typing import Dict, Optional
import hashlib
from pathlib import Path

LAMBDA_LAYER_REVISION_KEY = "LambdaLayerRevision"
LOCK_PATH = Path("Pipfile.lock")


class OsCommandError(SubprocessError):
    def __init__(self, error: CalledProcessError):
        self._error = error

    def __str__(self):
        msgs = (
            f"Command '{self._error.cmd}' exited with {self._error.returncode}",
            "stdout:",
            self._error.stdout.decode(),
            "stderr:",
            self._error.stderr.decode(),
        )
        return "\n".join(msgs)


def run_os_cmd(cmd: str, env: Dict[str, str] = {}) -> str:
    msg = f"runnning cmd: '{cmd}'"
    if env:
        envs_str = ";".join(f'{k}="{v}"' for k, v in env.items())
        msg += f" with {envs_str}"
    print(msg)

    _env = environ.copy()
    _env.update(env)

    try:
        return check_output(cmd, shell=True, stderr=PIPE, env=_env).decode()
    except CalledProcessError as e:
        raise OsCommandError(e)



def get_remote_revision(stage: str) -> Optional[str]:
    cmd = f"npx sls info -s {stage} -c lambda_layer.yml --verbose"
    out_lines = run_os_cmd(cmd).splitlines()

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
    cmd = f"npx sls deploy -c lambda_layer.yml -s {stage}"
    run_os_cmd(cmd, env={"LOCK_HASH": local_revision})


def deploy_lambda_layer(stage: str, force: bool) -> None:
    local_revision = get_local_revision()
    print(f"{local_revision=}")

    if force:
        print("Forcing deploy")
        return deploy(stage, local_revision)

    remote_revision = get_remote_revision(stage)
    print(f"{remote_revision=}")

    if local_revision == remote_revision:
        print("Versions are the same, let's do nothing!")
        return
    print("Versions are different, let's deploy!")
    deploy(stage, local_revision)


def main():
    parser = ArgumentParser()
    parser.add_argument("stage", type=str, help="Layer stage")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    deploy_lambda_layer(args.stage, args.force)
