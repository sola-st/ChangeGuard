def plot(self, *, ax=None, name=None, ref_line=True, **kwargs):
    self.ax_, self.figure_, name = self._validate_plot_params(ax=ax, name=name)
    info_pos_label = (
        f"(Positive class: {self.pos_label})" if self.pos_label is not None else ""
    )
    line_kwargs = {"marker": "s", "linestyle": "-"}
    if name is not None:
        line_kwargs["label"] = name
    line_kwargs.update(**kwargs)
    ref_line_label = "Perfectly calibrated"
    existing_ref_line = ref_line_label in self.ax_.get_legend_handles_labels()[1]
    if ref_line and not existing_ref_line:
        self.ax_.plot([0, 1], [0, 1], "k:", label=ref_line_label)
    self.line_ = self.ax_.plot(self.prob_pred, self.prob_true, **line_kwargs)[0]
    self.ax_.legend(loc="lower right")
    xlabel = f"Mean predicted probability {info_pos_label}"
    ylabel = f"Fraction of positives {info_pos_label}"
    self.ax_.set(xlabel=xlabel, ylabel=ylabel)
    return self
