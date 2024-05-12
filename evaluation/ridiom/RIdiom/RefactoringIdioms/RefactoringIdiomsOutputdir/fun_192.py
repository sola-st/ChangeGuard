def get_experts(settings):
    (
        discussions_commentors,
        discussions_last_month_commentors,
        discussions_authors,
    ) = get_discussions_experts(settings=settings)
    commentors , last_month_commentors , authors  = discussions_commentors, discussions_last_month_commentors, {**discussions_authors}
    return commentors, last_month_commentors, authors
