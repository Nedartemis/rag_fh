from backend.preprocess_crs.extract_all_infos import load_df_tables
from backend.preprocess_crs.filters import Filters
from backend.preprocess_crs.projects import Projects


def _save_filters_bounds_projects() -> None:
    for project in Projects:
        tables = load_df_tables(project)
        bounds = Filters(
            projects=tables["title"].unique().tolist(),
            date_min=tables["date"].min(),
            date_max=tables["date"].max(),
            cr_num_min=int(tables["num_cr"].min()),
            cr_num_max=int(tables["num_cr"].max()),
        )
        bounds.save(project.get_label())


if __name__ == "__main__":
    print("---")
    _save_filters_bounds_projects()
    obj = Filters.load(Projects.MAUBEUGE.get_label())
    print(obj)
    print("---")
