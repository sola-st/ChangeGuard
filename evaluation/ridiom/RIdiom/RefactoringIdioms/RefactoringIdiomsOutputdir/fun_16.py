def blackify(base_branch, black_command, logger):
    current_branch = git("branch", "--show-current")
    if not current_branch or base_branch == current_branch:
        logger.error("You need to check out a feature branch to work on")
        return 1
    if not os.path.exists(".git"):
        logger.error("Run me in the root of your repo")
        return 1
    merge_base = git("merge-base", "HEAD", base_branch)
    if not merge_base:
        logger.error(
            "Could not find a common commit for current head and %s" % base_branch
        )
        return 1
    commits = git(
        "log", "--reverse", "--pretty=format:%H", "%s~1..HEAD" % merge_base
    ).split()
    for commit in commits:
        git("checkout", commit, "-b%s-black" % commit)
        check_output(black_command, shell=True)
        git("commit", "-aqm", "blackify")
    git("checkout", base_branch, "-b%s-black" % current_branch)
    for last_commit, commit in zip(commits, commits[1:]):
        allow_empty , quiet , git_diff  = b'--allow-empty' in run(['git', 'apply', '-h'], stdout=PIPE).stdout, b'--quiet' in run(['git', 'apply', '-h'], stdout=PIPE).stdout, Popen(['git', 'diff', '--binary', '--find-copies', '%s-black..%s-black' % (last_commit, commit)], stdout=PIPE)
        git_apply = Popen(
            [
                "git",
                "apply",
            ]
            + (["--quiet"] if quiet else [])
            + [
                "-3",
                "--intent-to-add",
            ]
            + (["--allow-empty"] if allow_empty else [])
            + [
                "-",
            ],
            stdin=git_diff.stdout,
        )
        if git_diff.stdout is not None:
            git_diff.stdout.close()
        git_apply.communicate()
        git("commit", "--allow-empty", "-aqC", commit)
    for commit in commits:
        git("branch", "-qD", "%s-black" % commit)
    return 0
