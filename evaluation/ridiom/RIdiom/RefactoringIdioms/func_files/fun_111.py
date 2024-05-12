def report_generator(
    df, clustering_variables, fill_missing_report=None
):
    if fill_missing_report:
        df = df.fillna(value=fill_missing_report)
    df["dummy"] = 1
    numeric_cols = df.select_dtypes(np.number).columns
    report = (
        df.groupby(["Cluster"])[  
            numeric_cols
        ]  
        .agg(
            [
                ("sum", "sum"),
                ("mean_with_zeros", lambda x: np.mean(np.nan_to_num(x))),
                ("mean_without_zeros", lambda x: x.replace(0, np.NaN).mean()),
                (
                    "mean_25-75",
                    lambda x: np.mean(
                        np.nan_to_num(
                            sorted(x)[
                                round(len(x) * 25 / 100) : round(len(x) * 75 / 100)
                            ]
                        )
                    ),
                ),
                ("mean_with_na", "mean"),
                ("min", lambda x: x.min()),
                ("5%", lambda x: x.quantile(0.05)),
                ("25%", lambda x: x.quantile(0.25)),
                ("50%", lambda x: x.quantile(0.50)),
                ("75%", lambda x: x.quantile(0.75)),
                ("95%", lambda x: x.quantile(0.95)),
                ("max", lambda x: x.max()),
                ("count", lambda x: x.count()),
                ("stdev", lambda x: x.std()),
                ("mode", lambda x: x.mode()[0]),
                ("median", lambda x: x.median()),
                ("# > 0", lambda x: (x > 0).sum()),
            ]
        )
        .T.reset_index()
        .rename(index=str, columns={"level_0": "Features", "level_1": "Type"})
    )  
    clustersize = report[
        (report["Features"] == "dummy") & (report["Type"] == "count")
    ].copy()  
    clustersize.Type = (
        "ClusterSize"  
    )
    clustersize.Features = "# of Customers"
    clusterproportion = pd.DataFrame(
        clustersize.iloc[:, 2:].values
        / clustersize.iloc[:, 2:].values.sum()  
    )
    clusterproportion[
        "Type"
    ] = "% of Customers"  
    clusterproportion["Features"] = "ClusterProportion"
    cols = clusterproportion.columns.tolist()
    cols = cols[-2:] + cols[:-2]
    clusterproportion = clusterproportion[cols]  
    clusterproportion.columns = report.columns
    a = pd.DataFrame(
        abs(
            report[report["Type"] == "count"].iloc[:, 2:].values
            - clustersize.iloc[:, 2:].values
        )
    )  
    a["Features"] = 0
    a["Type"] = "# of nan"
    a.Features = report[
        report["Type"] == "count"
    ].Features.tolist()  
    cols = a.columns.tolist()
    cols = cols[-2:] + cols[:-2]
    a = a[cols]  
    a.columns = report.columns  
    report = report.drop(
        report[report.Type == "count"].index
    )  
    report = pd.concat(
        [report, a, clustersize, clusterproportion], axis=0
    )  
    report["Mark"] = report["Features"].isin(clustering_variables)
    cols = report.columns.tolist()
    cols = cols[0:2] + cols[-1:] + cols[2:-1]
    report = report[cols]
    sorter1 = {
        "ClusterSize": 9,
        "ClusterProportion": 8,
        "mean_with_zeros": 7,
        "mean_with_na": 6,
        "max": 5,
        "50%": 4,
        "min": 3,
        "25%": 2,
        "75%": 1,
        "# of nan": 0,
        "# > 0": -1,
        "sum_with_na": -2,
    }
    report = (
        report.assign(
            Sorter1=lambda x: x.Type.map(sorter1),
            Sorter2=lambda x: list(reversed(range(len(x)))),
        )
        .sort_values(["Sorter1", "Mark", "Sorter2"], ascending=False)
        .drop(["Sorter1", "Sorter2"], axis=1)
    )
    report.columns.name = ""
    report = report.reset_index()
    report = report.drop(columns=["index"])
    return report
