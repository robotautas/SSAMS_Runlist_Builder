import pandas as pd
from comments import comment1, comment2, comment3, comment4


class RunlistBuilder:
    def __init__(
        self,
        file: str,
        batch_controls: dict[str, str],
        settings: dict[str, str],
        jlimits: dict[str, str | list[str]],
        output_folder: str,
    ) -> None:
        raw_sheet = pd.read_excel(file, header=None, index_col=0)[4:]
        self.sheet = raw_sheet.reset_index().rename(columns={"index": "position"})
        self.sheet.columns = ["position", "lab_code", "client_code", "c_content"]
        self.sheet = self.sheet.dropna(subset=["lab_code", "client_code"], how="all")
        self.batch_controls = dict(batch_controls)  # to be on a safe side memory wise
        self.settings = dict(settings)
        self.jlimits = dict(jlimits)
        self.output_folder = output_folder
        self.summary_definitions = self.sum_defs()

        print(self.summary_definitions)

    def SmType_column(self, row) -> None:
        match row["lab_code"]:
            case "C1" | "C2" | "C3" | "C5" | "C7" | "C8" | "C9" | "OXII":
                return row["lab_code"]
            case "Grafitas" | "GRAFITAS" | "grafitas":
                return "RIP"
            case _:
                return "UKN"

    def Pos_column(self, row) -> None:
        return row["position"]

    def Sample_Name_column(self, row) -> None:
        match row["lab_code"]:
            case "C1" | "C2" | "C3" | "C5" | "C7" | "C8" | "C9" | "OXII":
                if pd.notna(row["client_code"]):
                    return f"{row['lab_code']}_{row['client_code']}"
                else:
                    return f"{row['lab_code']}_{self.counts[row['lab_code']].pop(0)}"
            case "Grafitas" | "GRAFITAS" | "grafitas":
                return "Grafitas"
            case _:
                return row["lab_code"]

    def Sample_Name_2_column(self, row) -> None:
        if row["lab_code"] in ["Grafitas", "GRAFITAS", "grafitas"]:
            return "LT"
        return "M"


    def Item_column(self, row) -> None:
        return row["Pos"]

    def Grp_column(self, row) -> None:
        return "0"

    def Sum_column(self, row) -> None:
        lab_code = row["lab_code"].lower()
        # if lab_code in self.summary_definitions:
        #     return self.summary_definitions[lab_code]
        # return '123'  # Default value

        match lab_code:
            case "grafitas":
                for k, v in enumerate(self.summary_definitions):
                    if v == "GRAFITAS_LT":
                        return k + 1
            case "ft" | "ftalis" | "ph. a" | "bkg":
                for k, v in enumerate(self.summary_definitions):
                    if v == "FTALIS":
                        return k + 1
            case "c1" | "c2" | "c3" | "c5" | "c7" | "c8" | "c9" | "oxii":
                for k, v in enumerate(self.summary_definitions):
                    if v == lab_code.upper():
                        return k + 1
            case _:

                return "123"  # Default value

    def Runs_column(self, row) -> None:
        return self.settings["runs"]

    def Md_column(self, row) -> None:
        return "T"

    def Tlimit_column(self, row) -> None:
        return self.settings["tlimit"]

    def Climit_column(self, row) -> None:
        return "0"

    def Warm_column(self, row) -> None:
        return self.settings["warm"]

    def Jn_column(self, row) -> None:
        return self.settings["jn"]

    def Jlimit_column(self, row) -> None:
        match row["lab_code"].lower():
            case (
                "c1"
                | "c2"
                | "c3"
                | "c5"
                | "c7"
                | "c8"
                | "c9"
                | "oxii"
                | "grafitas"
                | "ft"
            ):
                if self.jlimits[row["lab_code"].lower()][1] == "on":
                    return self.jlimits[row["lab_code"].lower()][0]
                else:
                    return self.jlimits["default"]
            case _:
                return self.jlimits["default"]

    def apply_columns(self) -> None:
        self.sheet["Pos"] = self.sheet.apply(self.Pos_column, axis=1)
        self.sheet["SmType"] = self.sheet.apply(self.SmType_column, axis=1)

        mask = self.sheet["client_code"].isna() & self.sheet["lab_code"].isin(
            ["C1", "C2", "C3", "C5", "C7", "C8", "C9", "OXII"]
        )
        self.sheet.loc[mask, "client_code"] = (
            self.sheet.loc[mask].groupby("lab_code").cumcount() + 1
        ).astype(str)

        self.sheet["Sample Name"] = self.sheet.apply(self.Sample_Name_column, axis=1)
        self.sheet["Sample Name 2"] = self.sheet.apply(
            self.Sample_Name_2_column, axis=1
        )
        self.sheet["Item"] = self.sheet.apply(self.Item_column, axis=1)
        self.sheet["Grp"] = self.sheet.apply(self.Grp_column, axis=1)

        self.sheet["Sum"] = self.sheet.apply(self.Sum_column, axis=1)
        mask = ~self.sheet["lab_code"].isin(
            [
                "C1",
                "C2",
                "C3",
                "C5",
                "C7",
                "C8",
                "C9",
                "OXII",
                "FTALIS",
                "GRAFITAS_LT",
                "Grafitas",
                "Ft",
                "bkg",
                "Ph. A",
            ]
        )
        self.sheet.loc[mask, "Sum"] = mask.cumsum() + len(
            self.summary_definitions
        )  # position index number in a mask series

        self.sheet["Runs"] = self.sheet.apply(self.Runs_column, axis=1)
        self.sheet["Md"] = self.sheet.apply(self.Md_column, axis=1)
        self.sheet["Tlimit"] = self.sheet.apply(self.Tlimit_column, axis=1)
        self.sheet["Climit"] = self.sheet.apply(self.Climit_column, axis=1)
        self.sheet["Warm"] = self.sheet.apply(self.Warm_column, axis=1)
        self.sheet["Jn"] = self.sheet.apply(self.Jn_column, axis=1)
        self.sheet["Jlimit"] = self.sheet.apply(self.Jlimit_column, axis=1)

    def batch_table(self) -> str:
        return f"""batch isotope   14C
batch source    S1
batch park      0
batch mode      {self.batch_controls['mode']}
batch autorange no
batch parkmode  {self.batch_controls['parkmode']}
batch judge     {self.batch_controls['judge']}
batch wlimit    1000"""

    def cathode_wheel_list(self) -> str:
        cathode_wheel = ""
        for i, row in self.sheet.iterrows():
            cathode_wheel += f"cat {row['Pos']:>4} {row['SmType']:<8} {row['Sample Name']:<16} {row['Sample Name 2']}\n"
        return cathode_wheel

    def runlist_item_table(self) -> str:
        runlist_items = ""
        for i, row in self.sheet.iterrows():
            runlist_items += f"item {row['Item']:>4} {row['Pos']:>4} {row['Grp']:>3} {row['Sum']:>3} {row['Runs']:>4} {row['Md']:>2} {row['Tlimit']:>6} {row['Climit']:>6} {row['Warm']:>4} {row['Jn']:>2} {row['Jlimit']:>6}\n"
        return runlist_items

    def sort_defs(self, sarasas: list[str]) -> list[str]:
        standarts_list = []
        ft_ox_list = []
        for standart in sarasas:
            match standart:
                case "FTALIS" | "OXII":
                    ft_ox_list.append(standart)
                case _:
                    standarts_list.append(standart)
        standarts_list.sort()
        return ft_ox_list + standarts_list

    def sum_defs(self) -> list[tuple[int, str]]:
        sum_def_set = set()
        for i, row in self.sheet.iterrows():
            match row["lab_code"].lower():
                case "grafitas":
                    sum_def_set.add("GRAFITAS_LT")
                case "ft" | "ftalis" | "ph. a" | "bkg":
                    sum_def_set.add("FTALIS")
                case "c2":
                    sum_def_set.add("C2")
                case "c3":
                    sum_def_set.add("C3")
                case "c7":
                    sum_def_set.add("C7")
                case "c9":
                    sum_def_set.add("C9")
                case "oxii":
                    sum_def_set.add("OXII")
                case "c1":
                    sum_def_set.add("C1")
                case "c5":
                    sum_def_set.add("C5")
                case "c8":
                    sum_def_set.add("C8")

        result = self.sort_defs(list(sum_def_set))

        return result

    def sum_def_table(self) -> str:
        sum_def_str = ""
        for key, value in enumerate(self.sum_defs()):
            sum_def_str += f"sum {key + 1:>3} {value}\n"
        return sum_def_str[:-1] #remove trailing \n

    def runlist_str(self) -> str:
        self.apply_columns()
        return f"""{comment1}
{self.batch_table()}\n
{comment2}
{self.cathode_wheel_list()}
{comment3}
{self.runlist_item_table()}
{comment4}
{self.sum_def_table()}
"""


if __name__ == "__main__":
    builder = RunlistBuilder(
        file="./examples/s4.xlsx",
        batch_controls={"mode": "nrm", "parkmode": "on", "judge": "on"},
        settings={
            "runs": "20",
            "tlimit": "1800",
            "jn": "6",
            "warm": "100",
        },
        jlimits={
            "default": "0.24",
            "grafitas": ["9", "on"],  # if 'on' then use the value
            "ft": ["3", "on"],
            "c1": ["0.24", "on"],
            "c2": ["0.24", "on"],
            "c3": ["0.23", "on"],
            "c5": ["0.24", "on"],
            "c7": ["0.24", "on"],
            "c8": ["3", "on"],
            "c9": ["3", "on"],
            "oxii": ["0.5", "on"],
        },
        output_folder="./runlists",
    )
    print(builder.runlist_str())
    # print(builder.runlist_str())
