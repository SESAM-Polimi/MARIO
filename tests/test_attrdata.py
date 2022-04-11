"""Tests for Database class"""

import sys
import os
from numpy import eye
import pytest
import pandas.testing as pdt
import pandas as pd
from pymrio import Extension,IOSystem

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

MAIN_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCK_PATH = f"{MAIN_PATH}/tests/mocks"

from mario.core.CoreIO import CoreModel
from mario.core.AttrData import Database
from mario.test.mario_test import load_test
from mario.log_exc.exceptions import (
    WrongInput, 
    NotImplementable,
    DataMissing
)
from mario import parse_from_excel


@pytest.fixture()
def CoreDataIOT():

    return load_test("IOT")


@pytest.fixture()
def CoreDataSUT():

    return load_test("SUT")

@pytest.fixture()
def agg_IOT():

    data = parse_from_excel(
        path = f"{MOCK_PATH}/IOT_aggregation.xlsx",
        table = 'IOT'
    )

    data.path = f"{MOCK_PATH}/IOT_aggregation.xlsx"

    return data

def test_build_new_instance(CoreDataIOT):

    CoreDataIOT.calc_all(matrices=["X"])
    CoreDataIOT.clone_scenario("baseline", "dummy")

    dummy = CoreDataIOT.build_new_instance("dummy")

    assert dummy.scenarios == ["baseline"]

    for k, v in dummy["baseline"].items():
        CoreDataIOT.calc_all([k], scenario="dummy")
        pdt.assert_frame_equal(CoreDataIOT["dummy"][k].round(0), v.round(0))


def test_to_iot(CoreDataSUT, CoreDataIOT):

    assert CoreDataSUT.copy().to_iot("A", inplace=True) is None
    assert isinstance(CoreDataSUT.copy().to_iot("A", inplace=False), Database)

    for method in ["A", "B", "C", "D"]:
        CoreDataSUT.copy().to_iot(method)

    CoreDataSUT.clone_scenario("baseline", "dummy")
    cpy = CoreDataSUT.to_iot("A", False)

    assert CoreDataSUT.table_type == "SUT"
    assert cpy.table_type == "IOT"
    assert cpy.scenarios == ["baseline"]

    assert cpy.sets == CoreDataIOT.sets

    for index in ["Satellite account", "Factor of production", "Consumption category"]:
        assert set(cpy.get_index(index)) == set(CoreDataSUT.get_index(index))

    assert cpy.units.keys() == CoreDataIOT.units.keys()


def test_get_aggregation_excel(CoreDataIOT, CoreDataSUT):
    path = f"{CoreDataIOT.directory}/agg.xlsx"

    for db in [CoreDataIOT, CoreDataSUT]:
        for level in db.sets:
            db.get_aggregation_excel(path, levels=level)
            file = pd.ExcelFile(path)
            assert file.sheet_names == [level]
            pdt.assert_index_equal(
                file.parse(sheet_name=level, index_col=0).index,
                pd.Index(db.get_index(level)),
            )

        db.get_aggregation_excel(path, levels="all")
        file = pd.ExcelFile(path)
        assert set(file.sheet_names) == set(db.sets)

        with pytest.raises(WrongInput) as msg:
            db.get_aggregation_excel(path, levels="dummy")

        assert "acceptable level/s" in str(msg.value)

def test_read_aggregated_index(CoreDataIOT,CoreDataSUT):

    with pytest.raises(WrongInput) as msg:
        CoreDataIOT.read_aggregated_index(io='io',levels=['dummy'])
    
    assert "is not an acceptable label" in str(msg.value)

    # test by reading pd.DataFrame
    aggregations_sut = {
        level : pd.DataFrame(index=CoreDataSUT.get_index(level),columns=['Aggregation'])
        for level in CoreDataSUT.sets
        }
    
    aggregations_iot = {
        level : pd.DataFrame(index=CoreDataIOT.get_index(level),columns=['Aggregation'])
        for level in CoreDataIOT.sets
    }

    # Testing the presence of nans
    with pytest.raises(DataMissing) as msg:
        CoreDataIOT.read_aggregated_index(io=aggregations_sut,ignore_nan=False)

    assert "nan values found" in str(msg.value)

    cpy_sut = CoreDataSUT.copy()
    cpy_iot = CoreDataIOT.copy()

    # filling the pd.DataFrames and reading them
    for ii,db in enumerate([cpy_sut,cpy_iot]):
        for k,v in [aggregations_sut,aggregations_iot][ii].items():
            v.iloc[:,0] = k
            db.read_aggregated_index(io={k:v},levels=k)
            pdt.assert_frame_equal(
                db.get_index(k,'aggregated'),v
            )

# TODO :: Drop to be checked
def test_aggregate(agg_IOT):

    sats = agg_IOT.get_index('Satellite account')
    aggregator = {
        'Satellite account': pd.DataFrame(['sats']*len(sats),index=sats,columns=['Agg'])
    }
    # test error catch for different units
    with pytest.raises(WrongInput) as msg:
        agg_IOT.aggregate(
            io = aggregator,
            levels = 'Satellite account',
            inplace = False
        )

    assert "different units" in str(msg.value)

    file = pd.ExcelFile(agg_IOT.path)
    for level in agg_IOT.sets:


        xlsx = file.parse(sheet_name=level,index_col=0)
        aggr = agg_IOT.aggregate(
                    io = agg_IOT.path,
                    levels = level,
                    inplace = False,
                    #drop = ['delete']
                )

        if level == 'Satellite account':
            assert aggr.get_index(level) == ['sats']
            assert len(aggr.get_index(level)) == 1
        else:
            assert set(aggr.get_index(level)) == set(xlsx.values.ravel())

            
def test_to_pymrio(CoreDataIOT,CoreDataSUT):

    with pytest.raises(NotImplementable) as msg:
        CoreDataSUT.to_pymrio()
    
    assert "pymrio supports only IO tables." in str(msg.value)

    with pytest.raises(WrongInput) as msg:
        # no " " in names are accepted
        CoreDataIOT.to_pymrio(satellite_account = "Dummy Dummy")

    assert "does not accept values containing space" in str(msg.value)

    io = CoreDataIOT.to_pymrio(
        satellite_account = "Extensions",
        factor_of_production = "Value_added"
        ).calc_all()

    assert isinstance(io,IOSystem)
    assert isinstance(io.Extensions,Extension)
    assert isinstance(io.Value_added,Extension)

    assert set(io.get_regions()) == set(CoreDataIOT.get_index("Region"))
    assert set(io.get_sectors()) == set(CoreDataIOT.get_index("Sector"))
    assert set(io.get_Y_categories()) == set(CoreDataIOT.get_index("Consumption category"))

    assert set(io.Extensions.get_rows()) == set(CoreDataIOT.get_index("Satellite account"))
    assert set(io.Value_added.get_rows()) == set(CoreDataIOT.get_index("Factor of production"))

    x = CoreDataIOT.X.droplevel(level=1)
    x.columns = ['indout']
    pdt.assert_frame_equal(
        io.x , x ,check_names=False
    )

    Y = CoreDataIOT.Y.droplevel(level=1).droplevel(level=1,axis=1)
    pdt.assert_frame_equal(
        io.Y , Y ,check_names=False
    )

    A = CoreDataIOT.z.droplevel(level=1).droplevel(level=1,axis=1)
    pdt.assert_frame_equal(
        io.A,A,check_names=False
    )

    Z = CoreDataIOT.Z.droplevel(level=1).droplevel(level=1,axis=1)
    pdt.assert_frame_equal(
        io.Z,Z,check_names=False
    )

    e = CoreDataIOT.e.droplevel(level=1,axis=1)
    pdt.assert_frame_equal(
        io.Extensions.S,e,check_names=False
    )   

    E = CoreDataIOT.E.droplevel(level=1,axis=1)
    pdt.assert_frame_equal(
        io.Extensions.F,E,check_names=False
    )   

    EY = CoreDataIOT.EY.droplevel(level=1,axis=1)
    pdt.assert_frame_equal(
        io.Extensions.F_Y,EY,check_names=False
    )   

    v = CoreDataIOT.v.droplevel(level=1,axis=1)
    pdt.assert_frame_equal(
        io.Value_added.S,v,check_names=False
    )   

    V = CoreDataIOT.V.droplevel(level=1,axis=1)
    pdt.assert_frame_equal(
        io.Value_added.F,V,check_names=False
    )   






    

