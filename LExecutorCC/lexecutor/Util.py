from datetime import datetime
import subprocess
import time

process = None


def start_server():
    global process
    #logger.info("Starting model server")
    server_log = open("model_server.log", "w")
    process = subprocess.Popen(
        "python -m lexecutor.predictors.codet5.ModelServer".split(" "),
        stderr=server_log, stdout=server_log)
    time.sleep(5)  # give server time to spin up


def shutdown_server():
    if process is not None:
        process.kill()


def gather_files(files_arg, suffix=".py"):
    if all([f.endswith(".txt") for f in files_arg]):
        files = []
        for f in files_arg:
            with open(f) as fp:
                for line in fp.readlines():
                    files.append(line.rstrip())
    else:
        for f in files_arg:
            if not f.endswith(suffix):
                raise Exception(f"Incorrect argument, expected {suffix} file: {f}")
        files = files_arg
    return files


def timestamp():
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.now()
    return round((now-epoch).total_seconds()*1000000.0)
