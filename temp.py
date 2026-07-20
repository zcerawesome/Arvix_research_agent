import subprocess
import os
import select
import uuid

current_env = os.environ.copy()
process = subprocess.Popen(
        ['/bin/bash'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=current_env
    )

assert process.stdin and process.stdout and process.stderr
stdin, stdout, stderr = process.stdin, process.stdout, process.stderr


def run_command(cmd):
    marker = uuid.uuid4().hex
    stdin.write(f'{cmd}\n')
    stdin.write(f'echo {marker}\n')
    stdin.flush()

    streams = {stdout: 'stdout', stderr: 'stderr'}
    done = False
    while not done:
        ready, _, _ = select.select(streams.keys(), [], [])
        for stream in ready:
            line = stream.readline()
            if not line:
                continue
            line = line.rstrip('\n')
            if line == marker:
                done = True
                continue
            if stream == stderr:
                print(f'[{streams[stream]}] {line}')


run_command('python3 test.py')

stdin.close()
process.terminate()
