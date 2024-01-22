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


def extract_executed_lines(result_string, offsets):
    prefix = 'Lines executed: ['
    if prefix not in result_string:
        return [], []
    temp = result_string[result_string.find(prefix) + len(prefix):]
    all_lines = list(map(int, temp[:temp.find(']')].split(', ')))
    return ([line-offsets['old'][0]+1 for line in all_lines if offsets['old'][0] <= line <= offsets['old'][1]],
            [line-offsets['new'][0]+1 for line in all_lines if offsets['new'][0] <= line <= offsets['new'][1]])


def calc_changed_lines_coverage(changed_lines, executed_lines):
    if not executed_lines:
        return 0.0
    if not changed_lines:
        return 1.0
    covered_lines = set()
    total_changed_lines = []
    for changed_line in changed_lines:
        total_changed_lines.extend(range(changed_line[0], changed_line[1]+1))
        for executed_line in executed_lines:
            if changed_line[0] <= executed_line <= changed_line[1]:
                covered_lines.add(executed_line)
    return len(covered_lines)/len(total_changed_lines)


def timestamp():
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.now()
    return round((now-epoch).total_seconds()*1000000.0)
