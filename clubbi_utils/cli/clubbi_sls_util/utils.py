import asyncio
from os import environ
from typing import Dict


async def run_os_cmd(cmd: str, env: Dict[str, str] = {}, echo: bool = True) -> str:
    """Run command in shell return output and print stdout in real time with the echo parameter

    Args:
        cmd (str): Shell command
        env (Dict[str, str], optional): Environment variables for the process. Defaults to {}.
        echo (bool, optional): Should print stdout in real time. Defaults to True.

    Raises:
        RuntimeError: On !=0 returncode throw exception with stdout and stderr

    Returns:
        str: stdout as string decoded
    """
    msg = f"runnning cmd: '{cmd}'"
    if env:
        envs_str = ";".join(f'{k}="{v}"' for k, v in env.items())
        msg += f" with {envs_str}"
    print(msg)

    _env = environ.copy()
    _env.update(env)

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=_env,
    )

    output_str = ""
    communicate_cor = proc.communicate()

    assert proc.stdout is not None
    async for chunk in proc.stdout:
        chunk_decoded = chunk.decode()
        if echo:
            print(chunk_decoded, end="")
        output_str += chunk_decoded

    stdout, stderr = await communicate_cor
    if proc.returncode != 0:
        msgs = (
            f"Command '{cmd}' exited with {proc.returncode}",
            "stdout:",
            output_str + stdout.decode(),
            "stderr:",
            stderr.decode(),
        )
        raise RuntimeError("\n".join(msgs))
    return output_str
