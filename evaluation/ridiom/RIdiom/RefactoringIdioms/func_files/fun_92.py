def activate(self, env):
    activate_script = self._get_activate_script()
    bin_dir = "Scripts" if WINDOWS else "bin"
    activate_path = env.path / bin_dir / activate_script
    if sys.platform == "win32":
        args = None
        if self._name in ("powershell", "pwsh"):
            args = ["-NoExit", "-File", str(activate_path)]
        elif self._name == "cmd":
            args = ["/K", str(activate_path)]
        if args:
            completed_proc = subprocess.run([self.path, *args])
            return completed_proc.returncode
        else:
            return env.execute(self._path)
    import shlex
    terminal = shutil.get_terminal_size()
    with env.temp_environ():
        c = pexpect.spawn(
            self._path, ["-i"], dimensions=(terminal.lines, terminal.columns)
        )
    if self._name in ["zsh", "nu"]:
        c.setecho(False)
    if self._name == "zsh":
        c.sendline(f"emulate bash -c '. {shlex.quote(str(activate_path))}'")
    elif self._name == "xonsh":
        c.sendline(f"vox activate {shlex.quote(str(env.path))}")
    else:
        cmd = f"{self._get_source_command()} {shlex.quote(str(activate_path))}"
        if self._name in ["fish", "nu"]:
            cmd += "\r"
        c.sendline(cmd)
    def resize(sig, data):
        terminal = shutil.get_terminal_size()
        c.setwinsize(terminal.lines, terminal.columns)
    signal.signal(signal.SIGWINCH, resize)
    c.interact(escape_character=None)
    c.close()
    sys.exit(c.exitstatus)
