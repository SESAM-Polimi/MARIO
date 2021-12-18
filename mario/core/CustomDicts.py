
from collections import UserDict

class Matrices(UserDict):
    """
    A costumized dict for having a better control on matrices property
    in mario.Core

    Properties
    -----------
    _bs_name : str
        This represents the name of the baseline scenario
    _dynamic : boolean
        Shows if the database is dynamic or not
    """
    def __init__(self,baseline_name,dynamic=False,vals={}):
        if baseline_name is None:
            if dynamic:
                raise ValueError('A Dynamic database can not be initialized with year=None')
            else:
                raise AssertionError('Matrices instantiated uncorrectly.')

        if dynamic:
            if not isinstance(baseline_name,int):
                raise ValueError('year for a dynamic database should be an integer number.')
        self._bs_name = baseline_name
        self._dynamic = dynamic

        super().__init__(vals)

    def __setitem__(self, key, item):
        if key == 'baseline':
            key = self._bs_name

        if self._dynamic and not isinstance(key,int):
            raise ValueError('For a dynamic database, only integer keys are accepted.')

        if not isinstance(item,dict):
            raise ValueError('item should be a dict.')


        super().__setitem__(key, item)

    def __getitem__(self, key):

        if key == 'baseline':
            key = self._bs_name

        if self._dynamic and isinstance(key,str):
            try:
                key = int(key)
            except: 
                pass

        return super().__getitem__(key)

if __name__ == '__main__':
    test = Matrices(2020,True)
    test['baseline'] = {}
    #%%

# %%
