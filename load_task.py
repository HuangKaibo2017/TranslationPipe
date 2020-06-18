from typing import Dict, Any, List
from pathlib import Path
import pandas as pd

def load_task(directory: Path) -> pd.DataFrame:
    if not directory.exists():
        raise ValueError(f"requirement folder '{str(uri)}' is not exists.")
    if not directory.is_dir():
        raise ValueError(f"directory arguement has to be a directory, but '{str(directory)}' found.")
    dfs: pd.DataFrame = None
    for task_file in directory.glob("*.xlsx"):
        if task_file.name.startswith("~$"):
            continue
        df: pd.DataFrame = pd.read_excel(task_file, na_values=[''], na_filter=False)
        dfs = pd.concat([dfs, df])
    return dfs