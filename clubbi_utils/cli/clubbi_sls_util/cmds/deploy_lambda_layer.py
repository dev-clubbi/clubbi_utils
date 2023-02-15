#! /usr/bin/env python

from argparse import ArgumentParser
import re
from typing import Dict, Optional
import hashlib
from pathlib import Path
import asyncio
from ..utils import run_os_cmd

LAMBDA_LAYER_REVISION_KEY = "LambdaLayerRevision"
LOCK_PATH = Path("Pipfile.lock")


async def get_remote_revision(stage: str) -> Optional[str]:
    cmd = f"npx sls info -s {stage} -c lambda_layer.yml --verbose"
    try:
        cmd_out = await run_os_cmd(cmd, echo=False)
    except RuntimeError as e:
        if re.search(r"Stack with id .* does not exist", str(e)):
            return None
        raise e
    out_lines = cmd_out.splitlines()

    revision_line = next(
        (line for line in out_lines if LAMBDA_LAYER_REVISION_KEY in line),
        None,
    )

    if revision_line is None:
        return None

    return revision_line.split(": ")[-1]


def get_local_revision() -> str:
    return hashlib.md5(LOCK_PATH.read_bytes()).hexdigest()


async def deploy(stage: str, local_revision: str) -> None:
    cmd = f"npx sls deploy -c lambda_layer.yml -s {stage}"
    await run_os_cmd(cmd, env={"LOCK_HASH": local_revision})
    print(f"Deployed in {stage}!")


async def deploy_lambda_layer(stage: str, force: bool) -> None:
    local_revision = get_local_revision()
    print(f"{local_revision=}")

    if force:
        print("Forcing deploy")
        return await deploy(stage, local_revision)

    remote_revision = await get_remote_revision(stage)
    print(f"{remote_revision=}")

    if local_revision == remote_revision:
        print("Versions are the same, let's do nothing!")
        return
    print("Versions are different, let's deploy!")
    await deploy(stage, local_revision)


def main():
    parser = ArgumentParser()
    parser.add_argument("stage", type=str, help="Layer stage")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    asyncio.run(deploy_lambda_layer(args.stage, args.force))
