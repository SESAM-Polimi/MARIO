# -*- coding: utf-8 -*-
"""
This module contains all the mario parsers API
"""
#%%
from mario.core.CustomDicts import Matrices
from mario.core.AttrData import Database
from mario.core.DyDatabase import DynamicDatabase
from mario.tools.tableparser import (
    eora_single_region,
    txt_praser,
    excel_parser,
    exio3,
    monetary_sut_exiobase,
    eora_multi_region,
    eurostat_sut,
)

from mario.log_exc.exceptions import WrongInput, LackOfInput
#%%
DATABASES = {
    "Database": {'func':Database,'args':[],'baseline_name':'baseline','dynamic':False},
    'Dynamic': {'func': DynamicDatabase,'args':['year'],'dynamic':True}
}

#%%
def parse_from_txt(
    path,
    table,
    mode="flows",
    calc_all=False,
    year=None,
    name=None,
    source=None,
    model="Database",
    **kwargs,
):

    """Parsing database from text files

    .. note::

        This function works with different files to parse the io data. So every matrix & units should be placed in different txt files.


    Parameters
    ----------
    path : str
        defined the folder that contains data files.

    table : str
        acceptable options are 'IOT' & 'SUT'

    mode : str
        defined the base matrices to parse. The options are:

            * `flows`: needs [Z.txt, Y.txt, EY.txt, V.txt, E.txt, units.txt] in the path
            * `coefficients`: needs [z.txt, Y.txt, EY.txt, v.txt, e.txt, units.txt] in the path

    calc_all : boolean
        if True, by default will calculate z,v,e,V,E,Z after parsing

    year : int, Optional
        optional to the Database (just for recoding the metadata)

    source : str, Optional
        optional to the Database (just for recoding the metadata)

    name : str, Optional
        optional but suggested. is useful for visualization and metadata.

    Returns
    -------
    mario.Database
    """
    if model not in DATABASES:
        raise WrongInput("Available DATABASES are {}".format([*DATABASES]))

    matrices, indeces, units = txt_praser(path, table, mode)

    return DATABASES[model](
        name=name,
        table=table,
        source=source,
        year=year,
        init_by_parsers={"matrices": matrices, "_indeces": indeces, "units": units},
        calc_all=calc_all,
        **kwargs,
    )


def parse_from_excel(
    path,
    table,
    mode="flows",
    data_sheet=0,
    unit_sheet="units",
    calc_all=False,
    year=None,
    name=None,
    source=None,
    model="Database",
    **kwargs,
):

    """Parsing database from excel file

    .. note::

        * This function works with a a single excel that contains data & units
        * Please look at the tutorials to understand the format/shape of the data

    Parameters
    ----------
    path : str
        defined the excel file that contains data & units.

    table : str
        acceptable options are 'IOT' & 'SUT'

    mode : str
        defined the base matrices to parse. The options are:

            * `flows`: needs [Z, Y, EY, V, E,] in a singel sheet and unit in another sheet
            * `coefficients`: needs [z, Y, EY, v, e, units.txt] in a singel sheet and unit in another sheet

    data_sheet : str, int
        defines the sheet index/name which the data is located(by defualt the first sheet is considered)

    units_sheet : str,int
        defines the sheet index/name in which the units are located (by default in a sheet named units )

    calc_all : boolean
        if True, by default will calculate z,v,e,Z,V,E after parsing

    year : int, Optional
        optional to the Database (just for recoding the metadata)

    source : str, Optional
        optional to the Database (just for recoding the metadata)

    name : str, Optional
        optional but suggested. is useful for visualization and metadata.

    Returns
    -------
    mario.Database
    """


    if model not in DATABASES:
        raise WrongInput("Available DATABASES are {}".format([*DATABASES]))

    _matrices = Matrices(baseline_name=DATABASES[model].get('baseline_name',year),dynamic=DATABASES[model]['dynamic'])
    matrices, indeces, units = excel_parser(path, table, mode, data_sheet, unit_sheet)
    _matrices[_matrices._bs_name] = matrices['baseline']

    return DATABASES[model]['func'](
        name=name,
        table=table,
        source=source,
        year=year,
        init_by_parsers={"matrices": _matrices, "_indeces": indeces, "units": units},
        calc_all=calc_all,
        **kwargs,
    )


def parse_exiobase_sut(
    path,
    calc_all=False,
    name=None,
    year=None,
    model="Database",
    **kwargs,
):

    """Parsing exiobase mrsut

    .. note::

        mario v.0.1.0, supports only Monetary Exiobase MRSUT database.

    Parameters
    ----------
    path : str
        defined the zip file containing data

    calc_all : boolean
        if True, by default will calculate z,v,e after parsing

    year : int, Optional
        optional to the Database (just for recoding the metadata)

    name : str, Optional
        optional but suggested. is useful for visualization and metadata.

    Returns
    -------
    mario.Database
    """

    if model not in DATABASES:
        raise WrongInput("Available DATABASES are {}".format([*DATABASES]))

    matrices, indeces, units = monetary_sut_exiobase(
        path,
    )

    return DATABASES[model](
        name=name,
        table="SUT",
        source="Exiobase Monetary Multi Regional Supply and Use Table (https://www.exiobase.eu/)",
        year=year,
        init_by_parsers={"matrices": matrices, "_indeces": indeces, "units": units},
        calc_all=calc_all,
        **kwargs,
    )


def parse_exiobase_3(
    path,
    calc_all=False,
    year=None,
    name=None,
    model="Database",
    version="3.8.2",
    **kwargs,
):

    """Parsing exiobase3

    .. note::

        pxp & ixi does not make any difference for the parser.

    Parameters
    ----------

    path : str
        defined the zip file containing data

    calc_all : boolean
        if True, by default will calculate z,v,e after parsing

    year : int, Optional
        optional to the Database (just for recoding the metadata)

    name : str, Optional
        optional but suggested. is useful for visualization and metadata.

    version : str
        accpetable versions are:

            * 3.8.2: F_Y for the final demand satellite account
            * 3.8.1: F_hh for the final demand satellite account

    Returns
    -------
    mario.Database

    """
    if model not in DATABASES:
        raise WrongInput("Available DATABASES are {}".format([*DATABASES]))

    if version not in ["3.8.2", "3.8.1"]:
        raise WrongInput("Acceptable versions are {}".format(["3.8.2", "3.8.1"]))
    matrices, indeces, units = exio3(path, version)

    return DATABASES[model](
        name=name,
        table="IOT",
        source="Exiobase3",
        year=year,
        init_by_parsers={"matrices": matrices, "_indeces": indeces, "units": units},
        calc_all=calc_all,
        **kwargs,
    )


def parse_eora(
    path,
    multi_region,
    indeces=None,
    name_convention="full_name",
    aggregate_trade=True,
    year=None,
    name=None,
    calc_all=False,
    model="Database",
    **kwargs,
) -> object:
    """Parsing eora databases

    .. note::

        * for multi_region database, only `eora26` is acceptable
        * multi_region database has some inconsistencies that are modified when parsed.
        * to see the modifications after parsing call 'meta_history'

    Parameters
    ----------
    path : str
        path to the zip file containing the database

    multi_region : bool
        True for eora26 else False

    indeces : str
        in case of multi_region database, the indeces.zip file path should be
        given

    name_convension : str
        will take the full names of countries if `full_name` otherwise, takes
        the abbreviations

    aggregate_trade : boolean
        if True, will aggregated all the trades into total imports and exports
        in single region database

    year : int, Optional
        for recording on the metadata

    name : str, Optional
        for recording on the metadata

    calc_all : boolean
        if True, will calculate the main missing matrices

    Returns
    -------
    mario.Database
    """
    if model not in DATABASES:
        raise WrongInput("Available DATABASES are {}".format([*DATABASES]))

    if multi_region:
        if year is None or indeces is None:
            raise LackOfInput(
                "For multi region Eora, the year and indeces path should be defined"
            )

        matrices, indeces, units = eora_multi_region(
            data_path=path, index_path=indeces, year=year, price="bp"
        )

        kwargs["notes"] = [
            "ROW deleted from database due to inconsistency.",
            "Intermediate imports from ROW added to VA matrix",
            "Intermediate exports to ROW added to Y matrix",
        ]

    else:
        matrices, indeces, units = eora_single_region(
            path=path, name_convention=name_convention, aggregate_trade=aggregate_trade
        )

    return DATABASES[model](
        name=name,
        table="IOT",
        year=year,
        source="Eora website @ https://www.worldmrio.com/",
        init_by_parsers={"matrices": matrices, "_indeces": indeces, "units": units},
        calc_all=calc_all,
        **kwargs,
    )


def parse_eurostat(
    supply_path,
    use_path,
    region,
    year,
    consumption_categories=[
        "Final consumption expediture",
        "Gross Capital formation",
        "Exports of goods and services",
    ],
    factors_of_production=[
        "Compensation of employees",
        "Other taxes less other subsidies on production",
        "Consumption of fixed capital",
        "Operating surplus and mixed income, net",
        "Taxes less subsidies on products",
    ],
    imports=["Imports of goods and services"],
    model="Database",
    name=None,
    calc_all=False,
    **kwargs,
) -> object:

    """Parsing Eurostat databases

    .. note::

        * this function is not generally applicable to any Eurostat table: it works only for specific table formats. Please refer to the example on the website
        * first rule: it is not possible to parse file different from .xls format
        * second rule: in each .xsl file, be sure data are referring to only one region
        * third rule: use only "total" as stock/flow parameter, and only one unit of measure
        * forth rule: supply must be provided in activity by commodity, use must be provided in commodity by activitiy formats
        * fifth rule: only SUT table are supported

    Parameters
    ----------
    supply_path : str
        path to the .xls file containing the supply table
    use_path : str
        path to the .xls file containing the use table

    region : str
        name of the region: be consistent with the Eurostat names!

    year : int
        year to which the table is referring. Multiple years can be contained in the .xls files but one only can be parsed

    consumption_categories : list, Optional
        By default, a list of consumption categories that balance the tables according to the Eurostat criteria. The user can decide to modify them

    factors_of_production : list, Optional
        By default, a list of factors of production that balance the tables according to the Eurostat criteria. The user can decide to modify them

    imports : list, Optional
        By default, a list of imports that balance the tables according to the Eurostat criteria. The user can decide to modify them

    name : str, Optional
        for recording on the metadata

    calc_all : bool, Optional
        if True, will calculate the main missing matrices

    Returns
    -------
    mario.Database
    """

    if model not in DATABASES:
        raise WrongInput("Available DATABASES are {}".format([*DATABASES]))

    table = "SUT"
    if table == "SUT":
        matrices, indeces, units = eurostat_sut(
            supply_path,
            use_path,
            region,
            year,
            consumption_categories,
            factors_of_production,
            imports,
        )

    return DATABASES[model](
        name=name,
        table=table,
        source="eurostat",
        year=year,
        init_by_parsers={"matrices": matrices, "_indeces": indeces, "units": units},
        calc_all=calc_all,
        **kwargs,
    )

# %%
