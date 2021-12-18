
from mario.core.CoreIO import CoreModel


class DynamicDatabase(CoreModel):

    def __init__(self,year, name=None, table=None, Z=None, E=None, V=None, Y=None ,EY=None, units=None, price=None, source=None, calc_all=True, **kwargs):
        super().__init__(name=name, table=table, Z=Z, E=E, V=V, Y=Y, EY=EY, units=units, price=price, source=source, calc_all=calc_all, year=year, **kwargs)

    def upload_data(self,mapper,database):
        if database != self:
            raise ValueError('not equal')
        
        if any([i not in database.matrices for i in mapper]):
            raise ValueError('non valid key')

        if any([not isinstance(i,int) for i in mapper.values()]):
            raise ValueError('values of the mapper should be int')

        for key,value in mapper.items():
            self.matrices[value] = database[key]
