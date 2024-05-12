def roadmap_pdeps(context):
    KNOWN_STATUS = {
        "Under discussion",
        "Accepted",
        "Implemented",
        "Rejected",
        "Withdrawn",
    }
    context["pdeps"] = collections.defaultdict(list)
    pdeps_path = (
        pathlib.Path(context["source_path"]) / context["roadmap"]["pdeps_path"]
    )
    for pdep in sorted(pdeps_path.iterdir()):
        if pdep.suffix != ".md":
            continue
        with pdep.open() as f:
            title = f.readline()[2:]  
            status = None
            for line in f:
                if line.startswith("- Status: "):
                    status = line.strip().split(": ", 1)[1]
                    break
            if status not in KNOWN_STATUS:
                raise RuntimeError(
                    f'PDEP "{pdep}" status "{status}" is unknown. '
                    f"Should be one of: {KNOWN_STATUS}"
                )
        html_file = pdep.with_suffix(".html").name
        context["pdeps"][status].append(
            {
                "title": title,
                "url": f"pdeps/{html_file}",
            }
        )
    github_repo_url = context["main"]["github_repo_url"]
    resp = requests.get(
        "https://api.github.com/search/issues?"
        f"q=is:pr is:open label:PDEP repo:{github_repo_url}",
        headers=GITHUB_API_HEADERS,
    )
    if resp.status_code == 403:
        sys.stderr.write("WARN: GitHub API quota exceeded when fetching pdeps\n")
        resp_bkp = requests.get(context["main"]["production_url"] + "pdeps.json")
        resp_bkp.raise_for_status()
        pdeps = resp_bkp.json()
    else:
        resp.raise_for_status()
        pdeps = resp.json()
    with open(
        pathlib.Path(context["target_path"]) / "pdeps.json", "w", encoding="utf-8"
    ) as f:
        json.dump(pdeps, f)
    compiled_pattern = re.compile(r"^PDEP-(\d+)")
    def sort_pdep(pdep):
        title = pdep["title"]
        match = compiled_pattern.match(title)
        if not match:
            msg = f"""Could not find PDEP number in '{title}'. Please make sure to
                write the title as: 'PDEP-num: {title}'."""
            raise ValueError(msg)
        return int(match[1])
    for pdep in sorted(pdeps["items"], key=sort_pdep):
        context["pdeps"]["Under discussion"].append(
            {"title": pdep["title"], "url": pdep["html_url"]}
        )
    return context
