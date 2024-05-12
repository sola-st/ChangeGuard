def program(args, env):
    exit_status = ExitStatus.SUCCESS
    downloader = None
    initial_request = None
    final_response = None
    def separate():
        getattr(env.stdout, 'buffer', env.stdout).write(MESSAGE_SEPARATOR_BYTES)
    def request_body_read_callback(chunk):
        should_pipe_to_stdout = bool(
            OUT_REQ_BODY in args.output_options
            and initial_request
            and chunk
        )
        if should_pipe_to_stdout:
            msg = requests.PreparedRequest()
            msg.is_body_upload_chunk = True
            msg.body = chunk
            msg.headers = initial_request.headers
            write_message(requests_message=msg, env=env, args=args, with_body=True, with_headers=False)
    try:
        if args.download:
            args.follow = True  
            downloader = Downloader(output_file=args.output_file, progress_file=env.stderr, resume=args.download_resume)
            downloader.pre_request(args.headers)
        messages = collect_messages(args=args, config_dir=env.config.directory,
                                    request_body_read_callback=request_body_read_callback)
        force_separator = False
        prev_with_body = False
        for message in messages:
            is_request = isinstance(message, requests.PreparedRequest)
            with_headers, with_body = get_output_options(args=args, message=message)
            do_write_body = with_body
            if prev_with_body and (with_headers or with_body) and (force_separator or not env.stdout_isatty):
                separate()
            force_separator = False
            if is_request:
                if not initial_request:
                    initial_request = message
                if with_body:
                    is_streamed_upload = not isinstance(message.body, (str, bytes))
                    do_write_body = not is_streamed_upload
                    force_separator = is_streamed_upload and env.stdout_isatty
            else:
                final_response = message
                if args.check_status or downloader:
                    exit_status = http_status_to_exit_status(http_status=message.status_code, follow=args.follow)
                    if exit_status != ExitStatus.SUCCESS and (not env.stdout_isatty or args.quiet):
                        env.log_error(f'HTTP {message.raw.status} {message.raw.reason}', level='warning')
            write_message(requests_message=message, env=env, args=args, with_headers=with_headers,
                          with_body=do_write_body)
            prev_with_body = with_body
        if force_separator:
            separate()
        if downloader and exit_status == ExitStatus.SUCCESS:
            download_stream, download_to = downloader.start(
                initial_url=initial_request.url,
                final_response=final_response,
            )
            write_stream(stream=download_stream, outfile=download_to, flush=False)
            downloader.finish()
            if downloader.interrupted:
                exit_status = ExitStatus.ERROR
                env.log_error(
                    f'Incomplete download: size={downloader.status.total_size};'
                    f' downloaded={downloader.status.downloaded}'
                )
        return exit_status
    finally:
        if downloader and not downloader.finished:
            downloader.failed()
        if args.output_file and args.output_file_specified:
            args.output_file.close()
